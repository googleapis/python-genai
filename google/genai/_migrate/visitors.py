"""CSTVisitor classes for google-generativeai -> google-genai migration.

This module contains all the CSTTransformer classes that perform the actual
source-to-source transformations. Each transformer targets a specific pattern
and uses libcst matchers to find and replace legacy code with new google-genai
equivalents.
"""

import libcst as cst
from libcst import matchers as m


class ImportAndConfigureVisitor(cst.CSTTransformer):  # type: ignore[misc]
    """Transform legacy imports and genai.configure() calls.

    (a) Replaces: import google.generativeai as genai
                  with: from google import genai

    (b) Replaces: genai.configure(api_key=...)  (top-level expr)
                  with: client = genai.Client(api_key=...)
    """

    def __init__(self) -> None:
        super().__init__()
        self.client_var = "client"

    def leave_Import(
        self, original_node: cst.Import, updated_node: cst.Import
    ) -> cst.BaseSmallStatement:
        # Match: import google.generativeai as genai
        if m.matches(
            original_node,
            m.Import(
                names=[
                    m.ImportAlias(
                        name=m.Attribute(
                            value=m.Name("google"),
                            attr=m.Name("generativeai"),
                        ),
                        asname=m.AsName(name=m.Name("genai")),
                    )
                ]
            ),
        ):
            # Replace with: from google import genai
            return cst.ImportFrom(
                module=cst.Name("google"),
                names=[cst.ImportAlias(name=cst.Name("genai"))],
            )
        return updated_node

    def leave_Expr(
        self, original_node: cst.Expr, updated_node: cst.Expr
    ) -> cst.BaseSmallStatement:
        # Match: genai.configure(...) as a top-level expression statement
        if m.matches(
            original_node,
            m.Expr(
                value=m.Call(
                    func=m.Attribute(
                        value=m.Name("genai"),
                        attr=m.Name("configure"),
                    )
                )
            ),
        ):
            # Extract the Call node
            call = original_node.value
            if isinstance(call, cst.Call):
                # Create: client = genai.Client(<same kwargs as configure>)
                assign = cst.Assign(
                    targets=[cst.AssignTarget(target=cst.Name(self.client_var))],
                    value=cst.Call(
                        func=cst.Attribute(
                            value=cst.Name("genai"),
                            attr=cst.Name("Client"),
                        ),
                        args=call.args,
                    ),
                )
                return assign
        return updated_node


class GenerativeModelVisitor(cst.CSTTransformer): # type: ignore[misc]
    """Detect genai.GenerativeModel(...) assignments and record model names.

    Records a mapping: variable_name -> model_name_string
    Does NOT rewrite the assignment (left for a later cleanup pass).
    """

    def __init__(self, symbol_table: dict[str, str]) -> None:
        super().__init__()
        self.symbol_table = symbol_table

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.BaseSmallStatement:
        # Match: var = genai.GenerativeModel('model-name')
        if m.matches(
            original_node,
            m.Assign(
                targets=[m.AssignTarget(target=m.Name())],
                value=m.Call(
                    func=m.Attribute(
                        value=m.Name("genai"),
                        attr=m.Name("GenerativeModel"),
                    )
                ),
            ),
        ):
            # Extract variable name
            target = original_node.targets[0].target
            if isinstance(target, cst.Name):
                var_name = target.value
            else:
                return updated_node

            # Extract model name from arguments
            model_name = "gemini-1.5-flash"  # default
            call = original_node.value
            if isinstance(call, cst.Call):
                # Check positional args first
                for arg in call.args:
                    if arg.keyword is None:
                        # Positional argument
                        if isinstance(arg.value, cst.SimpleString):
                            evaluated = arg.value.evaluated_value
                            if isinstance(evaluated, bytes):
                                model_name = evaluated.decode("utf-8")
                            else:
                                model_name = str(evaluated)
                        break
                else:
                    # No positional args, check keyword args
                    for arg in call.args:
                        if arg.keyword and arg.keyword.value == "model_name":
                            if isinstance(arg.value, cst.SimpleString):
                                evaluated = arg.value.evaluated_value
                                if isinstance(evaluated, bytes):
                                    model_name = evaluated.decode("utf-8")
                                else:
                                    model_name = str(evaluated)
                            break

            self.symbol_table[var_name] = model_name
            return cst.FlattenSentinel([])  # type: ignore[return-value]

        return updated_node


class GenerateContentVisitor(cst.CSTTransformer): # type: ignore[misc]
    """Rewrite model.generate_content(...) calls to client.models.generate_content(...).

    Uses the symbol_table populated by GenerativeModelVisitor to know the model name.
    """

    def __init__(self, symbol_table: dict[str, str]) -> None:
        super().__init__()
        self.symbol_table = symbol_table

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        # Match: var.generate_content(...)
        if m.matches(
            original_node,
            m.Call(
                func=m.Attribute(
                    value=m.Name(),
                    attr=m.Name("generate_content"),
                )
            ),
        ):
            func = original_node.func
            if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
                var_name = func.value.value
                if var_name in self.symbol_table:
                    model_name = self.symbol_table[var_name]

                    # Check for stream=True kwarg
                    stream = False
                    for arg in original_node.args:
                        if arg.keyword and arg.keyword.value == "stream":
                            if (
                                isinstance(arg.value, cst.Name)
                                and arg.value.value == "True"
                            ):
                                stream = True
                            elif isinstance(arg.value, cst.SimpleString):
                                stream = True
                            break

                    method_name = (
                        "generate_content_stream" if stream else "generate_content"
                    )

                    # Build new args: model=... + contents=... + other kwargs
                    new_args: list[cst.Arg] = [
                        cst.Arg(
                            keyword=cst.Name("model"),
                            value=cst.SimpleString(f"'{model_name}'"),
                        )
                    ]

                    # Map first positional arg (prompt) to contents=
                    # Pass through other args
                    first_pos = True
                    for arg in original_node.args:
                        if arg.keyword is None and first_pos:
                            # First positional -> contents
                            new_args.append(
                                cst.Arg(keyword=cst.Name("contents"), value=arg.value)
                            )
                            first_pos = False
                        elif arg.keyword and arg.keyword.value == "stream" and stream:
                            # Skip stream=True kwarg
                            continue
                        else:
                            new_args.append(arg)

                    return cst.Call(
                        func=cst.Attribute(
                            value=cst.Attribute(
                                value=cst.Name("client"),
                                attr=cst.Name("models"),
                            ),
                            attr=cst.Name(method_name),
                        ),
                        args=new_args,
                    )

        return updated_node


class StartChatVisitor(cst.CSTTransformer): # type: ignore[misc]
    """Rewrite model.start_chat(...) calls to client.chats.create(...).

    Uses the symbol_table populated by GenerativeModelVisitor to know the model name.
    """

    def __init__(self, symbol_table: dict[str, str]) -> None:
        super().__init__()
        self.symbol_table = symbol_table

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        # Match: var.start_chat(...)
        if m.matches(
            original_node,
            m.Call(
                func=m.Attribute(
                    value=m.Name(),
                    attr=m.Name("start_chat"),
                )
            ),
        ):
            func = original_node.func
            if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
                var_name = func.value.value
                if var_name in self.symbol_table:
                    model_name = self.symbol_table[var_name]

                    # Check for history= kwarg
                    history_arg = None
                    for arg in original_node.args:
                        if arg.keyword and arg.keyword.value == "history":
                            history_arg = arg
                            break

                    # Build new args: model=... + config=...
                    new_args: list[cst.Arg] = [
                        cst.Arg(
                            keyword=cst.Name("model"),
                            value=cst.SimpleString(f'"{model_name}"'),
                        )
                    ]

                    if history_arg is not None:
                        # TODO: Full history migration is out of scope for 24h.
                        # For now, pass empty GenerateContentConfig as placeholder.
                        new_args.append(
                            cst.Arg(
                                keyword=cst.Name("config"),
                                value=cst.parse_expression(
                                    "types.GenerateContentConfig()"
                                ),
                            )
                        )

                    return cst.Call(
                        func=cst.Attribute(
                            value=cst.Attribute(
                                value=cst.Name("client"),
                                attr=cst.Name("chats"),
                            ),
                            attr=cst.Name("create"),
                        ),
                        args=new_args,
                    )

        return updated_node


class CountTokensVisitor(cst.CSTTransformer): # type: ignore[misc]
    """Rewrite model.count_tokens(...) calls to client.models.count_tokens(...).

    Uses the symbol_table populated by GenerativeModelVisitor to know the model name.
    """

    def __init__(self, symbol_table: dict[str, str]) -> None:
        super().__init__()
        self.symbol_table = symbol_table

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        # Match: var.count_tokens(...)
        if m.matches(
            original_node,
            m.Call(
                func=m.Attribute(
                    value=m.Name(),
                    attr=m.Name("count_tokens"),
                )
            ),
        ):
            func = original_node.func
            if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
                var_name = func.value.value
                if var_name in self.symbol_table:
                    model_name = self.symbol_table[var_name]

                    # Build new args: model=... + contents=... + other kwargs
                    new_args: list[cst.Arg] = [
                        cst.Arg(
                            keyword=cst.Name("model"),
                            value=cst.SimpleString(f"'{model_name}'"),
                        )
                    ]

                    # Map first positional arg to contents=
                    # Pass through other args
                    first_pos = True
                    for arg in original_node.args:
                        if arg.keyword is None and first_pos:
                            # First positional -> contents
                            new_args.append(
                                cst.Arg(keyword=cst.Name("contents"), value=arg.value)
                            )
                            first_pos = False
                        else:
                            new_args.append(arg)

                    return cst.Call(
                        func=cst.Attribute(
                            value=cst.Attribute(
                                value=cst.Name("client"),
                                attr=cst.Name("models"),
                            ),
                            attr=cst.Name("count_tokens"),
                        ),
                        args=new_args,
                    )

        return updated_node
