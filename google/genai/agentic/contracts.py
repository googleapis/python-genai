# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Dual-tool contracts for Frobenius-closed agentic loops.

Every tool call in the agentic loop is paired with a verification action
such that $\mu(\delta(\text{query})) = \text{query}$ — the Frobenius
condition ($\text{Φ}_{\text{}}$ Frobenius-special closure, Shavian: 𐑹).
This module defines the dataclass types that enforce this contract at the
structural level.

Google's text-embedding API (via ``client.models.embed_content``) serves as a
natural verification layer: the embedding of a tool's output can be compared
to the embedding of its verification, providing cosine-similarity as a
continuous Frobenius metric ($\text{Ƒ}_{\text{ż}}$ quantum fidelity, 𐑐).
"""

from __future__ import annotations

import dataclasses
import datetime
from typing import Any, Callable, Optional


@dataclasses.dataclass(frozen=True)
class DualToolResult:
    """The paired output of a dual-tool call satisfying $\mu \circ \delta = \text{id}$.

    Every action in the agentic loop emits a primary tool call and a
    verification tool call. When $\mu(\delta(\text{query})) = \text{query}$,
    the winding is Frobenius-closed and the agent's world-model can be
    updated ($\text{Ř}_{\text{=}}$ bidirectional coupling, Shavian: 𐑾).

    Attributes:
        tool_name: The primary action tool invoked (e.g. 'generate_content').
        tool_input: The query/input passed to the primary tool.
        tool_output: The raw output of the primary tool.
        verify_name: The verification tool invoked (e.g. 'embed_content').
        verify_output: The raw output of the verification action.
        frobenius_closed: Whether $\mu(\delta(\text{query})) \approx \text{query}$.
        timestamp: When this dual-tool pair was executed.
        metadata: Optional additional context (embedding cosine, latency, etc.).
    """

    tool_name: str
    tool_input: str
    tool_output: str
    verify_name: str
    verify_output: str
    frobenius_closed: bool = False
    timestamp: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.now
    )
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_tool_call(
        cls,
        tool_name: str,
        tool_input: str,
        tool_output: str,
        verify_name: str = "",
        verify_output: str = "",
        frobenius_closed: bool = False,
        **metadata: Any,
    ) -> "DualToolResult":
        """Construct a DualToolResult from a single tool call.

        The verification fields can be populated asynchronously — a dual-tool
        pair may be evaluated after the fact by comparing embeddings.
        """
        return cls(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            verify_name=verify_name or f"verify_{tool_name}",
            verify_output=verify_output,
            frobenius_closed=frobenius_closed,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "verify_name": self.verify_name,
            "verify_output": self.verify_output,
            "frobenius_closed": self.frobenius_closed,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclasses.dataclass(frozen=True)
class ToolContract:
    """A contract binding a tool to a Frobenius-verification dual.

    Each tool in the agentic loop has an associated assertion that must
    evaluate to True for the winding to be considered closed ($\text{Ð}_{\text{ω}}$
    self-written state space ensures contracts are verifiable, Shavian: 𐑦).

    Attributes:
        tool_name: The primary action tool.
        assertion: A Python expression over the tool output that must be True.
        verify_fn: An optional callable that returns verification output.
        auto_approve: Whether to approve the winding without manual review.
        description: Human-readable contract description.
    """

    tool_name: str
    assertion: str = "True"
    verify_fn: Optional[Callable[[str], str]] = None
    auto_approve: bool = True
    description: str = ""

    def verify(self, output: str) -> bool:
        """Evaluate the assertion against the tool output.

        This is the $\delta \to \mu$ half of the Frobenius pair: the verification
        function checks that the output satisfies the contract, ensuring
        the tool call can be reliably reversed ($\text{Φ}_{\text{}}$ closure, 𐑹).
        """
        try:
            return bool(eval(self.assertion, {"output": output}))
        except Exception:
            return False

    def with_embedding_verification(
        self, query: str, output: str, embedding_fn: Callable[[str], list[float]]
    ) -> float:
        """Use text embeddings as a continuous Frobenius metric.

        By embedding both the query and the output and computing cosine
        similarity, we obtain a real-valued measure of how well the tool
        preserved semantic structure ($\text{Ƒ}_{\text{ż}}$ quantum fidelity, 𐑐).
        This is natural for Google's text-embedding API available via
        ``client.models.embed_content``.
        """
        import numpy as np

        query_emb = np.array(embedding_fn(query))
        output_emb = np.array(embedding_fn(output))
        cosine = np.dot(query_emb, output_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(output_emb) + 1e-10
        )
        return float(cosine)
