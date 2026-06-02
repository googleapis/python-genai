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
"""AgentTrajectory — monotonic winding history with $\Omega_{\text{z}}$ invariant.

The trajectory is the state space of the agentic loop. It records a monotonic
sequence of windings. Each winding records the four phases of the THINK→ACT→
OBSERVE→UPDATE cycle and whether the Frobenius condition $\mu \circ \delta =
\text{id}$ was satisfied.

The winding counter is never reset — the trajectory is the state space
($\text{Ð}_{\text{ω}}$ imscriptive context, Shavian: 𐑦). Structural health
metrics (frobenius_ratio, winding_count) provide the topological invariants
that distinguish $\text{O}_{\text{2}}$ (integer-winding, Shavian: 𐑭) from
$\text{O}_{\text{0}}$ (zero-winding, Shavian: 𐑷).
"""

from __future__ import annotations

import dataclasses
import datetime
from typing import Any, Optional

from .contracts import DualToolResult


@dataclasses.dataclass(frozen=True)
class AgentCycle:
    """A single complete winding of the agentic loop.

    Attributes:
        winding: Monotonically increasing winding number (never reset).
        timestamp: When this cycle was executed.
        action_name: The primary action tool invoked.
        action_input: The input/query to the action.
        dual_result: The DualToolResult from the action+verification pair.
        update_note: Summary of the world-model update applied after verification.
        done: Whether this cycle terminated the agentic loop.
        conclusion: The final conclusion if done=True.
        frobenius_closed: Whether $\mu \circ \delta = \text{id}$ was satisfied.
    """

    winding: int
    timestamp: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.now
    )
    action_name: str = ""
    action_input: str = ""
    dual_result: Optional[DualToolResult] = None
    update_note: str = ""
    done: bool = False
    conclusion: str = ""
    frobenius_closed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "winding": self.winding,
            "timestamp": self.timestamp.isoformat(),
            "action_name": self.action_name,
            "action_input": self.action_input,
            "dual_result": self.dual_result.to_dict() if self.dual_result else None,
            "update_note": self.update_note,
            "done": self.done,
            "conclusion": self.conclusion,
            "frobenius_closed": self.frobenius_closed,
        }


class AgentTrajectory:
    """Monotonic trajectory of agentic windings.

    The trajectory is the state space — it is never summarized or discarded.
    Each winding adds a new point to the monotonic advance ($\Omega_{\text{z}}$
    invariant, Shavian: 𐑭).

    Attributes:
        _cycles: Ordered list of completed windings.
        _winding_counter: Strictly increasing, never reset.
    """

    def __init__(self, initial_cycles: Optional[list[AgentCycle]] = None):
        self._cycles: list[AgentCycle] = list(initial_cycles or [])
        self._winding_counter: int = len(self._cycles)

    @property
    def winding_count(self) -> int:
        """Total completed windings (monotonic, never reset)."""
        return self._winding_counter

    @property
    def frobenius_ratio(self) -> float:
        """Fraction of windings where $\mu \circ \delta = \text{id}$ was satisfied.

        A ratio of 1.0 means every winding was Frobenius-closed.
        This is the structural health metric for $\text{O}_{\text{2}}$ promotion.
        """
        if not self._cycles:
            return 0.0
        closed = sum(1 for c in self._cycles if c.frobenius_closed)
        return closed / len(self._cycles)

    def append(self, cycle: AgentCycle) -> None:
        """Append a completed winding.

        The winding field is auto-assigned if not already set.
        """
        if cycle.winding == 0:
            object.__setattr__(cycle, "winding", self._winding_counter + 1)
        self._cycles.append(cycle)
        self._winding_counter = len(self._cycles)

    def last(self) -> Optional[AgentCycle]:
        """Return the most recent winding, or None if empty."""
        return self._cycles[-1] if self._cycles else None

    def to_context(self) -> list[dict[str, Any]]:
        """Serialize the entire trajectory for LLM context injection.

        Returns the full winding history so the model can reason over
        its own prior states — enabling $\text{Ð}_{\text{ω}}$ self-written
        state space (Shavian: 𐑦).
        """
        return [c.to_dict() for c in self._cycles]

    def structural_health(self) -> dict[str, Any]:
        """Compute topological health metrics.

        Returns:
            A dict with winding_count, frobenius_ratio, last_winding,
            total_updates, and the $\Omega$ invariant status.
        """
        return {
            "winding_count": self.winding_count,
            "frobenius_ratio": self.frobenius_ratio,
            "last_winding": self.last().winding if self._cycles else 0,
            "total_updates": sum(
                1 for c in self._cycles if c.update_note
            ),
            "omega_invariant": (
                "𐑭" if self.frobenius_ratio >= 0.95
                else "𐑴" if self.frobenius_ratio >= 0.8
                else "𐑷"
            ),
            "structural_tier": (
                "O\u2082" if self.winding_count >= 2 and self.frobenius_ratio >= 0.8
                else "O\u2081" if self.winding_count >= 1
                else "O\u2080"
            ),
        }
