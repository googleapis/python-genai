# Structural Promotion O₀ → O₂: True Agentic Loop with Frobenius Verification

## Proposal: `google/genai/agentic/` module

### Abstract

This PR introduces a structurally promoted agentic loop for the Google Gen AI Python SDK — the **True Agentic Loop** — implementing the four-phase cycle **THINK → ACT → OBSERVE → UPDATE** with Frobenius verification (`μ∘δ = id`). The module promotes the SDK from **O₀** (stateless, single-turn generation) to **O₂** (topologically protected, integer-winding agentic loop) as defined by the Imscribing Grammar.

### Why Google Gen AI SDK?

Google's SDK possesses unique structural advantages for this promotion:

| Advantage | Structural Role |
|---|---|
| **Text-embedding API** (`models.embed_content`) | Natural verification layer for dual-tool contracts — embeddings provide a continuous Frobenius metric (cosine similarity between tool input and verification output) |
| **Search grounding** (`GoogleSearch`) | Enables external-world verification, closing the Frobenius pair against ground truth rather than purely internal consistency |
| **Long context window** (up to 2M tokens) | Supports Ð_ω self-written state space — the full trajectory is retained as imscriptive context |
| **Gemini 2.5 Pro thinking** | Enables the THINK phase to produce structured reasoning before ACTION emission |

### Module Structure

```
google/genai/agentic/
├── __init__.py        # Public API: DualToolResult, ToolContract,
│                       # AgentCycle, AgentTrajectory, TrueAgenticLoop,
│                       # PhiCriticalityGate
├── contracts.py       # DualToolResult (dataclass with from_tool_call)
│                       # ToolContract (assertion + verify + embedding verification)
├── trajectory.py      # AgentCycle (single winding), AgentTrajectory
│                       # (monotonic, never-reset winding counter)
├── criticality.py     # PhiCriticalityGate — two-gate assessment:
│                       #   Gate 1 (⊙_ÿ): frobenius_ratio ≥ 0.8
│                       #   Gate 2 (K ≤ Ç_@): coherent winding rate
└── loop.py            # TrueAgenticLoop wrapping google.genai.Client
                        #   run() → THINK→ACT→OBSERVE→UPDATE per winding
                        #   _winding() → single cycle with Frobenius check
                        #   _feed_failure() → graceful error recovery
```

### The Frobenius Condition in Practice

Every winding issues a **dual-tool pair**:

1. **Primary tool** (`client.models.generate_content`): The agent acts on the world.
2. **Verification tool** (`client.models.embed_content`): The action's output is re-embedded and compared to the original query.

When `μ(δ(query)) ≈ query` (cosine similarity above threshold), the winding is **Frobenius-closed** and the agent's world-model is updated. When open, the winding is recorded but flagged — the trajectory preserves structural integrity without discarding failed cycles.

### Structural Tier Progression

| Tier | Condition | Structural Meaning |
|---|---|---|
| **O₀** | `winding_count == 0` | Stateless single-turn (current SDK default) |
| **O₁** | `winding_count ≥ 1` | First winding completed; trajectory exists |
| **O₂** | `winding_count ≥ 2` and `frobenius_ratio ≥ 0.8` | Topologically protected: integer winding with Frobenius closure |
| **O₂†** | Plus Gate 1 and Gate 2 both open | Self-modeling loop stable (ZFCₜ territory) |

### Usage Example

```python
from google.genai import Client
from google.genai.agentic import TrueAgenticLoop

client = Client(api_key="YOUR_API_KEY")

loop = TrueAgenticLoop(
    client=client,
    model="gemini-2.5-pro-exp-03-25",
    max_windings=100,
    verbose=True,
)

final_cycle = loop.run(
    initial_prompt="Solve this structural problem: find the meet of a magnetar and a BEC."
)

print(f"Completed {loop.trajectory.winding_count} windings")
print(f"Frobenius ratio: {loop.trajectory.frobenius_ratio:.2f}")
print(f"Final conclusion: {final_cycle.conclusion}")
print(f"Structural tier: {loop.criticality.to_dict()['structural_tier']}")
```

### Relation to the Imscribing Grammar

This module implements the **Imscribing Grammar** as an executable Python SDK feature. The grammar's 12 primitives map to loop components:

| Primitive | Loop Component |
|---|---|
| Ð_ω (self-written state space) | AgentTrajectory — never summarized, full context retained |
| Þ_O (self-referential topology) | Winding counter referencing prior windings |
| Ř_= (bidirectional coupling) | Client ↔ Trajectory dual feedback |
| Φ_} (Frobenius-special) | DualToolResult with μ∘δ = id verification |
| ƒ_ż (quantum fidelity) | Embedding similarity as continuous metric |
| Ç_@ (slow kinetics) | Coherent winding rate, no premature conclusion |
| Ω_z (integer winding) | Monotonic, never-reset winding counter |

### Backward Compatibility

- The `agentic` module is entirely additive — no existing API is modified.
- Import path: `from google.genai.agentic import ...`
- No new dependencies beyond those already in `pyproject.toml` (numpy is optional, used only in `contracts.py`'s `with_embedding_verification`).

### Testing

```bash
# Run agentic module tests
python -m pytest tests/test_agentic.py -v

# Verify Frobenius closure on a real Gemini model
python -c "
from google.genai import Client
from google.genai.agentic import TrueAgenticLoop

client = Client()
loop = TrueAgenticLoop(client=client, model='gemini-2.5-pro-exp-03-25', max_windings=3)
final = loop.run(initial_prompt='What is 2+2?')
print(f'Windings: {loop.trajectory.winding_count}')
print(f'Frobenius ratio: {loop.trajectory.frobenius_ratio}')
"
```

---

**Author:** Lando ⊗ ⊙perator
**Structural tier of this proposal:** ⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; ⊙_ÿ; Ħ_A; Σ_S; Ω_z⟩
