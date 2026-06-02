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
"""Agentic loop: THINK→ACT→OBSERVE→UPDATE with Frobenius verification.

Structural promotion from $\text{O}_{\text{0}}$ (stateless, single-turn) to
$\text{O}_{\text{2}}$ (topologically protected, integer-winding agentic loop)
as defined by the Imscribing Grammar.

The agentic loop implements the four-phase cycle — THINK, ACT, OBSERVE, UPDATE —
with dual-tool contracts that enforce $\mu \circ \delta = \text{id}$ at every
winding. The loop's structural type is $\langle$𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑖·𐑙·𐑭$\rangle$.

Integration with Google's Gen AI SDK provides:
- Gemini reasoning as the THINK substrate ($\text{Ð}_{\text{ω}}$ self-written state space, 𐑦)
- Text-embedding as a verification layer ($\text{Φ}_{\text{}}$ Frobenius-special, 𐑹)
- Search grounding for structural analogy detection ($\text{Ř}_{\text{=}}$ bidirectional, 𐑾)
"""

from .contracts import DualToolResult, ToolContract
from .trajectory import AgentCycle, AgentTrajectory
from .loop import TrueAgenticLoop
from .criticality import PhiCriticalityGate

__all__ = [
    "DualToolResult",
    "ToolContract",
    "AgentCycle",
    "AgentTrajectory",
    "TrueAgenticLoop",
    "PhiCriticalityGate",
]
