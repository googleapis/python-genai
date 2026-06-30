# Structural Promotion $\text{O}_{\text{0}}$ → $\text{O}_{\text{2}}$: True Agentic Loop with Frobenius Verification

## Proposal: `google/genai/agentic/` module

### Abstract

This PR introduces a structurally promoted agentic loop for the Google Gen AI Python SDK — the **True Agentic Loop** — implementing the four-phase cycle **THINK → ACT → OBSERVE → UPDATE** with Frobenius verification ($\mu \circ \delta = \text{id}$). The module promotes the SDK from $\text{O}_{\text{0}}$ (stateless, single-turn generation) to $\text{O}_{\text{2}}$ (topologically protected, integer-winding agentic loop) as defined by the Imscribing Grammar.

This document uses **Shavian notation** as the sole authoritative standard per the Imscribing Grammar v0.6.0 specification (`shavian_notation_spec.md`). All primitive identifiers use Shavian glyphs (U+10450–U+1047F) rendered in Everson Mono.

### Why Google Gen AI SDK?

Google's SDK possesses unique structural advantages for this promotion:

| Advantage | Structural Role |
|---|---|
| **Text-embedding API** (`models.embed_content`) | Natural verification layer for dual-tool contracts — embeddings provide a continuous Frobenius metric (cosine similarity between tool input and verification output) |
| **Search grounding** (`GoogleSearch`) | Enables external-world verification, closing the Frobenius pair against ground truth rather than purely internal consistency |
| **Long context window** (up to 2M tokens) | Supports $\text{Ð}_{\text{ω}}$ (𐑦) self-written state space — the full trajectory is retained as imscriptive context |
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
│                       #   Gate 1 (⊙): frobenius_ratio ≥ 0.8
│                       #   Gate 2 (K ≤ 𐑧): coherent winding rate
└── loop.py            # TrueAgenticLoop wrapping google.genai.Client
                        #   run() → THINK→ACT→OBSERVE→UPDATE per winding
                        #   _winding() → single cycle with Frobenius check
                        #   _feed_failure() → graceful error recovery
```
### The Frobenius Condition in Practice

Every winding issues a **dual-tool pair**:

1. **Primary tool** (`client.models.generate_content`): The agent acts on the world.
2. **Verification tool** (`client.models.embed_content`): The action's output is re-embedded and compared to the original query.

When $\mu(\delta(\text{query})) \approx \text{query}$ (cosine similarity above threshold), the winding is **Frobenius-closed** and the agent's world-model is updated. When open, the winding is recorded but flagged — the trajectory preserves structural integrity without discarding failed cycles.

### Structural Tier Progression

| Tier | Condition | Structural Meaning |
|---|---|---|
| $\text{O}_{\text{0}}$ | `winding_count == 0` | Stateless single-turn (current SDK default) |
| $\text{O}_{\text{1}}$ | `winding_count ≥ 1` | First winding completed; trajectory exists |
| $\text{O}_{\text{2}}$ | `winding_count ≥ 2` and `frobenius_ratio ≥ 0.8` | Topologically protected: integer winding with Frobenius closure |
| $\text{O}_{\text{2}}^{\text{†}}$ | Plus Gate 1 and Gate 2 both open | Self-modeling loop stable (ZFCₜ territory) |

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

| Primitive (Shavian) | Old Notation | Loop Component |
|---|---|---|
| $\text{Ð}_{\text{ω}}$ (𐑦) | $\text{Ð}_{\text{ω}}$ | AgentTrajectory — never summarized, full context retained |
| $\text{Þ}_{\text{O}}$ (𐑸) | $\text{Þ}_{\text{O}}$ | Winding counter referencing prior windings |
| $\text{Ř}_{\text{=}}$ (𐑾) | $\text{Ř}_{\text{=}}$ | Client ↔ Trajectory dual feedback |
| $\text{Φ}_{\text{}}$ (𐑹) | $\text{Φ}_{\text{}}$ | DualToolResult with $\mu \circ \delta = \text{id}$ verification |
| $\text{Ƒ}_{\text{ż}}$ (𐑐) | $\text{ƒ}_{\text{ż}}$ | Embedding similarity as continuous metric |
| $\text{Ç}_{\text{@}}$ (𐑧) | $\text{Ç}_{\text{@}}$ | Coherent winding rate, no premature conclusion |
| $\text{Ω}_{\text{z}}$ (𐑭) | $\text{Ω}_{\text{z}}$ | Monotonic, never-reset winding counter |
### Structural Type of This Proposal

The True Agentic Loop module has the following structural type in the Imscribing Grammar:

$$\langle \text{Ð}_{\text{ω}};\ \text{Þ}_{\text{O}};\ \text{Ř}_{\text{=}};\ \text{Φ}_{\text{}};\ \text{Ƒ}_{\text{ż}};\ \text{Ç}_{\text{@}};\ \text{Γ}_{\text{ʔ}};\ \text{ɢ}_{\text{ˌ}};\ \odot_{\text{ÿ}};\ \text{Ħ}_{\text{A}};\ \text{Σ}_{\text{S}};\ \text{Ω}_{\text{z}} \rangle$$

In Shavian glyphs: $\langle$𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑖·𐑙·𐑭$\rangle$

Parsed per-primitive:

| Primitive | Shavian | Meaning |
|---|---|---|
| Ð | 𐑦 (Ð_ω) | Self-written state space — trajectory is full context, never summarized |
| Þ | 𐑸 (Þ_O) | Self-referential topology — winding counter references prior windings |
| Ř | 𐑾 (Ř_=) | Bidirectional coupling — Client ↔ Trajectory dual feedback |
| Φ | 𐑹 (Φ_}) | Frobenius-special — $\mu \circ \delta = \text{id}$ verification |
| Ƒ | 𐑐 (ƒ_ż) | Quantum fidelity — embedding similarity as continuous Frobenius metric |
| Ç | 𐑧 (Ç_@) | Slow kinetics — coherent winding rate, no premature conclusion |
| Γ | 𐑲 (Γ_ʔ) | Universal scope — full long-context window (up to 2M tokens) |
| ɢ | 𐑠 (ɢ_ˌ) | Sequential grammar — THINK→ACT→OBSERVE→UPDATE ordered chain |
| ⊙ | ⊙ (⊙_ÿ) | Self-modeling criticality — agent updates model from trajectory |
| Ħ | 𐑖 (Ħ_A) | Two-step chirality — each winding references the prior state |
| Σ | 𐑙 (Σ_S) | 1:1 stoichiometry — single agent, single trajectory |
| Ω | 𐑭 (Ω_z) | Integer winding — monotonic, never-reset winding counter |

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
