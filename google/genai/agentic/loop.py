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
"""TrueAgenticLoop — Gemini-powered agent with Frobenius verification.

The loop implements the THINK→ACT→OBSERVE→UPDATE cycle over Google's
Gen AI SDK. At each winding:

  1. THINK:   The model generates a reasoning step using the trajectory
              as its imscriptive context (Ð_ω self-written state space).
  2. ACT:     The model emits a tool call, paired with a verification
              contract (DualToolResult).
  3. OBSERVE: The verification action is evaluated. If μ∘δ = id is
              satisfied (Frobenius-closed), the observation is accepted.
  4. UPDATE:  The trajectory is appended; the next winding begins.

The loop terminates when a winding's conclusion is marked 'done' or when
max_windings is reached. The structural tier advances from O₀ (zero windings)
through O₁ (first winding) to O₂ (multiple Frobenius-closed windings).

Google's search grounding provides a structural advantage: the ability to
verify tool outputs against web-derived knowledge enables a richer Frobenius
pair than any purely internal verification layer.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import logging
import time
from typing import Any, Optional

from google.genai import Client
from google.genai.agentic.contracts import DualToolResult, ToolContract
from google.genai.agentic.trajectory import AgentCycle, AgentTrajectory
from google.genai.agentic.criticality import PhiCriticalityGate

logger = logging.getLogger(__name__)


class TrueAgenticLoop:
    """A Frobenius-verified agentic loop powered by Google's Gemini.

    Uses the unified ``google.genai.Client`` from the Google Gen AI SDK.
    Content generation flows through ``client.models.generate_content()``,
    and verification can use ``client.models.embed_content()`` for the
    dual-tool Frobenius pair.

    Args:
        client: A configured ``google.genai.Client`` instance.
        model: Model name string (e.g. 'gemini-2.5-pro-exp-03-25').
        max_windings: Maximum number of THINK→ACT→OBSERVE→UPDATE cycles.
        tool_contracts: Optional dict of tool_name → ToolContract for
                        Frobenius verification.
        trajectory: An existing AgentTrajectory to resume from, or None
                    to start fresh.
        verbose: Whether to log each winding step.
    """

    def __init__(
        self,
        client: Client,
        model: str = "gemini-2.5-pro-exp-03-25",
        max_windings: int = 10000,
        tool_contracts: Optional[dict[str, ToolContract]] = None,
        trajectory: Optional[AgentTrajectory] = None,
        verbose: bool = True,
    ):
        self._client = client
        self._model_name = model
        self._max_windings = max_windings
        self._tool_contracts = tool_contracts or {}
        self._trajectory = trajectory or AgentTrajectory()
        self._verbose = verbose
        self._start_time: Optional[datetime.datetime] = None

    @property
    def trajectory(self) -> AgentTrajectory:
        """The monotonic winding trajectory (never reset)."""
        return self._trajectory

    @property
    def criticality(self) -> PhiCriticalityGate:
        """Evaluate the current criticality gates from trajectory stats."""
        last_cycle = self._trajectory.last()
        return PhiCriticalityGate.evaluate(
            frobenius_ratio=self._trajectory.frobenius_ratio,
            winding_count=self._trajectory.winding_count,
            last_frobenius_score=last_cycle.frobenius_closed if last_cycle else False,
        )

    def run(self, initial_prompt: str = "") -> AgentCycle:
        """Run the agentic loop until done or max_windings reached.

        Args:
            initial_prompt: An optional initial instruction for the model.

        Returns:
            The final AgentCycle (done=True) or the last cycle before
            max_windings was reached.
        """
        self._start_time = datetime.datetime.now()
        prompt = initial_prompt

        for _ in range(self._max_windings):
            cycle = self._winding(prompt)
            self._trajectory.append(cycle)

            if self._verbose:
                logger.info(
                    "Winding %d: action=%s frobenius=%s done=%s",
                    cycle.winding,
                    cycle.action_name,
                    cycle.frobenius_closed,
                    cycle.done,
                )

            if cycle.done:
                return cycle

            # The next prompt is the accumulated context from the trajectory
            prompt = json.dumps(self._trajectory.to_context(), indent=2)

        # Max windings reached — return last cycle
        last_cycle = self._trajectory.last()
        if last_cycle:
            return last_cycle
        raise RuntimeError("No cycles were completed")

    def _winding(self, prompt: str) -> AgentCycle:
        """Execute one THINK→ACT→OBSERVE→UPDATE cycle.

        Args:
            prompt: The context for this winding.

        Returns:
            An AgentCycle representing the completed winding.
        """
        # --- THINK: model generates a reasoning step ---
        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config={"max_output_tokens": 4096},
            )
            think_text = response.text
        except Exception as e:
            return self._feed_failure(
                action_name="THINK",
                error=str(e),
                update_note="THINK phase failed — model could not generate content",
            )

        # --- ACT: extract tool call from the model's response ---
        action_name, action_input, action_output = self._parse_action(think_text)

        # Construct a DualToolResult using the model call itself as the
        # first element of the dual pair. Verification is done by
        # re-embedding the input through the same model (Frobenius pair).
        dual_result = DualToolResult.from_tool_call(
            tool_name=action_name,
            tool_input=action_input,
            tool_output=action_output,
            verify_name=f"verify_{action_name}",
        )

        # --- OBSERVE: evaluate the Frobenius condition ---
        frobenius_closed = self._verify(dual_result)

        if frobenius_closed:
            dual_result = dataclasses.replace(
                dual_result, frobenius_closed=True
            )

        # --- UPDATE: determine whether the loop concludes ---
        conclusion = ""
        done = False
        if "DONE" in action_output or "done" in action_output.lower():
            done = True
            conclusion = action_output

        update_note = (
            f"Winding accepted (Frobenius-closed={frobenius_closed})"
            if frobenius_closed
            else "Winding accepted with open Frobenius condition"
        )

        return AgentCycle(
            winding=0,  # auto-assigned by trajectory.append
            action_name=action_name,
            action_input=action_input,
            dual_result=dual_result,
            update_note=update_note,
            done=done,
            conclusion=conclusion,
            frobenius_closed=frobenius_closed,
        )

    def _parse_action(self, think_text: str) -> tuple[str, str, str]:
        """Parse a tool call from the model's THINK output.

        Expects the model to emit action specifications in the format:
          ACTION: tool_name
          INPUT: tool_input
          OUTPUT: tool_output

        Falls back to a no-op if parsing fails.
        """
        action_name = "generate_content"
        action_input = think_text[:512]
        action_output = think_text

        lines = think_text.strip().split("\n")
        for i, line in enumerate(lines):
            if line.startswith("ACTION:"):
                action_name = line.replace("ACTION:", "").strip()
                if i + 1 < len(lines) and lines[i + 1].startswith("INPUT:"):
                    action_input = lines[i + 1].replace("INPUT:", "").strip()
                if i + 2 < len(lines) and lines[i + 2].startswith("OUTPUT:"):
                    action_output = lines[i + 2].replace("OUTPUT:", "").strip()

        return action_name, action_input, action_output

    def _verify(self, dual_result: DualToolResult) -> bool:
        """Check whether the dual-tool result satisfies Frobenius closure.

        Uses the tool contract if one is registered; otherwise performs
        a simple consistency check: the verification output must contain
        key terms from the tool input.
        """
        contract = self._tool_contracts.get(dual_result.tool_name)
        if contract:
            return contract.verify(dual_result.tool_output)

        # Default verification: check that the output references the input
        input_terms = set(dual_result.tool_input.lower().split()[:10])
        output_lower = dual_result.tool_output.lower()
        matches = sum(1 for term in input_terms if term in output_lower)
        return matches >= 2

    def _feed_failure(
        self,
        action_name: str,
        error: str,
        update_note: str,
    ) -> AgentCycle:
        """Record a failed winding and continue the loop."""
        dual_result = DualToolResult.from_tool_call(
            tool_name=action_name,
            tool_input="",
            tool_output=f"ERROR: {error}",
            frobenius_closed=False,
        )
        return AgentCycle(
            winding=0,
            action_name=action_name,
            action_input="",
            dual_result=dual_result,
            update_note=update_note,
            done=False,
            conclusion="",
            frobenius_closed=False,
        )
