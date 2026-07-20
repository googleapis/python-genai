# google/genai/_migrate/codemod.py
import libcst as cst

from google.genai._migrate.visitors import (CountTokensVisitor,
                                            GenerateContentVisitor,
                                            GenerativeModelVisitor,
                                            ImportAndConfigureVisitor,
                                            StartChatVisitor)


def transform_source(src: str) -> str:
    """
    Parses Python source code with libcst and applies the migration visitors.

    The visitors are applied sequentially to ensure state (like the symbol_table
    mapping variable names to model strings) is passed down correctly.

    Args:
        src: The raw Python source code string to be migrated.

    Returns:
        The migrated Python source code string, with formatting preserved.

    Raises:
        ValueError: If the source code contains invalid Python syntax.
    """
    if not src.strip():
        return src

    try:
        module = cst.parse_module(src)
    except cst.ParserSyntaxError as e:
        raise ValueError(f"Failed to parse Python source: {e}") from e

    # Shared state container: maps legacy model variable names to their string names.
    # e.g., {"model": "'gemini-1.5-flash'"}
    symbol_table = {}

    # Apply visitors sequentially.
    # Order matters:
    # 1. Imports/configure must run first to establish the `client` variable.
    # 2. GenerativeModelVisitor must run before the others to populate the symbol_table.
    # 3. The remaining visitors use the symbol_table to rewrite method calls.
    module = module.visit(ImportAndConfigureVisitor())
    module = module.visit(GenerativeModelVisitor(symbol_table))
    module = module.visit(GenerateContentVisitor(symbol_table))
    module = module.visit(StartChatVisitor(symbol_table))
    module = module.visit(CountTokensVisitor(symbol_table))

    return module.code
