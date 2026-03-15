# Discovery Index: amplifier-bundle-dot-graph

> **Project:** amplifier-bundle-dot-graph
> **Date:** 2026-03-13
> **Purpose:** Master navigation document for the multi-agent discovery effort that bootstrapped the DOT/Graphviz capability bundle for the Amplifier ecosystem

---

## Executive Summary

This discovery effort dispatched 7 specialized agents across two workspaces to answer one question: *How should DOT/Graphviz capabilities be formalized into a dedicated Amplifier bundle?* The agents scanned ~6,240 sessions (March 1-13, 2026), cataloged 70+ existing DOT artifacts across the ecosystem, identified 9 distinct use cases, researched the external DOT/Graphviz ecosystem, performed a deep comparison of two competing DOT dialects, extracted hard-won lessons from the Attractor pipeline engine, and synthesized everything into a phased implementation blueprint. The result: a complete design for `amplifier-bundle-dot-graph` -- a thin bundle providing expert DOT authoring agents, validation tooling, pattern libraries, and quality standards that serve every DOT use case in the Amplifier ecosystem.

---

## Document Map

| # | Document | Lines | What It Contains | When to Read It |
|---|----------|-------|-----------------|-----------------|
| 1 | [`SESSION-INDEX.md`](SESSION-INDEX.md) | 469 | Comprehensive index of all sessions using DOT/Graphviz (March 1-13), classified into 5 relevance tiers across 38 root sessions. Cross-session analysis of DOT usage patterns. | When you need to trace a specific DOT decision back to its origin session. |
| 2 | [`DOT-CONCEPTS-DEEP-DIVE.md`](DOT-CONCEPTS-DEEP-DIVE.md) | 674 | Conceptual visions, technical patterns, design decisions, and unresolved questions extracted from 11 root sessions and ~1,200 turns. Includes the 7 use-case taxonomy, evolution timeline, and key quotes. | When you want to understand *why* DOT matters and how the thinking evolved. |
| 3 | [`BUNDLE-GUIDANCE.md`](BUNDLE-GUIDANCE.md) | 1,407 | Complete bundle authoring blueprint derived from foundation documentation. Thin bundle pattern, behavior composition, agent definitions, context sink architecture, namespace rules, anti-patterns, and 4-phase roadmap. | When you're ready to build -- this is the implementation manual. |
| 4 | [`DOT-ARTIFACTS-CATALOG.md`](DOT-ARTIFACTS-CATALOG.md) | 806 | Every DOT concept, pattern, convention, validation rule, and quality standard across the ecosystem. Three dialects documented (Attractor pipeline, architecture documentation, resolve node_type). Cross-dialect comparison matrix. | When you need the authoritative reference on what DOT attributes and patterns exist. |
| 5 | [`DOT-ECOSYSTEM-RESEARCH.md`](DOT-ECOSYSTEM-RESEARCH.md) | 876 | External DOT/Graphviz ecosystem research: language specification, 10 layout engines, 35+ output formats, Python library comparison (graphviz vs pydot vs pygraphviz vs networkx), validation approaches, AI/LLM usage patterns, alternatives comparison (Mermaid, PlantUML, D2). | When you need to make technology choices or understand DOT's position in the broader ecosystem. |
| 6 | [`DOT-DIALECT-COMPARISON.md`](DOT-DIALECT-COMPARISON.md) | 765 | Side-by-side analysis of the two pipeline DOT dialects: `node_type` attribute-based (consensus_task.dot, semport.dot) vs Attractor shape-based. Syntax, execution model, expressiveness, LLM-friendliness, token efficiency, and unification recommendations. | When you need to understand the dialect split or make standardization decisions. |
| 7 | [`ATTRACTOR-DOT-EXPERTISE.md`](ATTRACTOR-DOT-EXPERTISE.md) | 720 | Every hard-won lesson from Attractor's DOT usage: shape-to-handler mapping rationale, LLM generation patterns and common mistakes, model stylesheet deep dive, validation gaps, what should be generalized vs kept Attractor-specific, progressive disclosure layering, anti-patterns. | When you need Attractor-specific DOT expertise or want to understand what to generalize. |
| 8 | [`BOOTSTRAP-SYNTHESIS.md`](BOOTSTRAP-SYNTHESIS.md) | 901 | Final synthesis: 9 use-case taxonomy with maturity ratings, capability map (7 capabilities), architecture recommendation (bundle structure + config), 4-phase implementation plan with success criteria, 8 open design questions, and complete existing asset inventory with reuse actions. | When you need the actionable plan -- this is the decision document. |

**Total discovery output:** 6,618 lines across 8 documents.

---

## Discovery Statistics

| Metric | Count |
|--------|-------|
| Specialized agents dispatched | 7 (session-analyst, foundation-expert, workspace-explorer, ecosystem-researcher, dialect-comparator, attractor-expert, synthesis-agent) |
| Sessions scanned | ~6,240 (all Amplifier sessions, March 1-13, 2026) |
| Sessions with DOT/Graphviz matches | 1,424 unique sessions |
| Root sessions with substantive DOT activity | 38 |
| Existing DOT artifacts cataloged | 70+ files across the ecosystem |
| Use cases identified | 9 (grouped by maturity: production, validated, proven, designed, emerging) |
| DOT dialects documented | 3 (Attractor shape-based, architecture documentation, resolve node_type) |
| Open design questions flagged | 8 (in BOOTSTRAP-SYNTHESIS.md Section 5) |
| Unresolved technical questions | 8 (in DOT-CONCEPTS-DEEP-DIVE.md Section 7) |
| Source files analyzed in detail | 19 (listed in DOT-ARTIFACTS-CATALOG.md Section 12) |
| Key quotes captured | 12 (in DOT-CONCEPTS-DEEP-DIVE.md Section 8) |

---

## The Five DOT Usage Patterns

Five distinct patterns for DOT usage emerged from cross-session analysis of 38 root sessions:

### 1. DOT as Pipeline DSL (Attractor)
**Sessions:** 12+ | **Maturity:** Production | **Artifacts:** 54+ DOT files

The Attractor pipeline engine uses Graphviz DOT as its **native runtime format**. Each `.dot` file is an executable AI workflow: nodes are LLM tasks, edges define flow, shapes determine handler types (10-shape vocabulary). The `model_stylesheet` enables CSS-like multi-provider model routing. This is the highest-volume and most technically deep DOT usage in the ecosystem.

### 2. DOT as Architecture Documentation
**Sessions:** 4 | **Maturity:** Validated | **Artifacts:** 4 production DOT files, 247 tests

Every Parallax Discovery investigation produces `diagram.dot` files as standard output -- architecture maps, integration diagrams, state machines. These use a **different shape vocabulary** than pipeline DOT (box=module, cylinder=store, diamond=decision). Working tooling generates, synthesizes, and validates these artifacts with quality gates (150-250 line targets, rendered legends, cluster naming).

### 3. DOT as Event/System Specification
**Sessions:** 2 | **Maturity:** Proven | **Artifacts:** 13+ numbered DOT files

DOT files created as formal specifications for the Amplifier event system: session state machines, event flows, orchestrator variants, delegation trees. Key finding: a DOT diagram **revealed a cancellation gap** that was "invisible because no diagram showed all exit paths." Proposed module-level `events.dot` convention was rejected for hand-maintenance but remains viable if generated from source.

### 4. DOT as Skill/Process Visualization
**Sessions:** 14+ | **Maturity:** Production | **Artifacts:** Embedded in skill files

DOT syntax embedded in Amplifier skill markdown files (`digraph brainstorming`, `digraph process`, `digraph when_to_use`). Appears in every session loading the brainstormer or superpowers skills. Demonstrates DOT is already a natural documentation format within the skill ecosystem.

### 5. DOT as LLM-Readable Architecture (Dotfiles Vision)
**Sessions:** 2 | **Maturity:** Designed | **Artifacts:** Design documents + prototypes

The emerging vision of DOT as a **dual-purpose format** -- simultaneously human-renderable AND agent-scannable. Per-person, per-repo architecture files (`/dotfiles/<handle>/<repo>/`) with progressive disclosure: `overview.dot` (~200 lines) at the top, detail files by topic, raw investigation artifacts at the bottom. An LLM reads ONE file and knows the shape of the system.

---

## Bundle Design Summary

*Distilled from [BOOTSTRAP-SYNTHESIS.md](BOOTSTRAP-SYNTHESIS.md)*

### Identity

| Aspect | Value |
|--------|-------|
| **Bundle name (namespace)** | `dot-graph` |
| **Repo name** | `amplifier-bundle-dot-graph` |
| **Pattern** | Thin bundle + behavior (following `amplifier-bundle-recipes` exemplar) |
| **Root bundle.md** | ~15 lines YAML -- includes foundation + own behavior |

### Bundle Structure

```
amplifier-bundle-dot-graph/
├── bundle.md                          # Thin root (~15 lines YAML)
├── behaviors/
│   └── dot-graph.yaml                 # Reusable behavior (agents + context)
├── agents/
│   ├── dot-author.md                  # DOT authoring expert (context sink)
│   └── diagram-reviewer.md            # DOT quality reviewer (context sink)
├── context/
│   ├── dot-graph-awareness.md         # Thin pointer for root sessions (~30 lines)
│   └── dot-graph-instructions.md      # Consolidated instructions (~50 lines)
├── docs/
│   ├── DOT_SYNTAX_REFERENCE.md        # Complete DOT language reference
│   ├── DOT_PATTERNS.md                # Common patterns with templates
│   ├── DOT_BEST_PRACTICES.md          # Layout tips, anti-patterns, conventions
│   ├── PIPELINE_DOT_GUIDE.md          # Attractor pipeline dialect guide
│   └── ARCHITECTURE_DOT_GUIDE.md      # Architecture documentation dialect guide
├── skills/
│   ├── dot-graph-syntax/SKILL.md      # Quick-reference syntax lookup
│   └── dot-graph-patterns/SKILL.md    # Copy-paste pattern templates
├── modules/                           # Tool modules (Phase 2+)
│   └── tool-dot-graph/
│       ├── pyproject.toml
│       └── tool_dot_graph/
│           ├── tool.py                # Validate + info operations
│           ├── validate.py            # Three-tier validation
│           ├── render.py              # SVG/PNG/PDF rendering (Phase 3)
│           └── analyze.py             # NetworkX graph analysis (Phase 3)
├── README.md
└── LICENSE
```

### Implementation Roadmap

| Phase | Scope | Effort | Value |
|-------|-------|--------|-------|
| **Phase 1** | Agents + context + skills + docs (no custom tool) | Medium | Immediate -- centralizes DOT expertise |
| **Phase 2** | Validation tool (`dot_graph validate`) | Low-Medium | High -- enables novel workflow gates |
| **Phase 3** | Rendering + graph analysis tools | Medium | Medium -- adds structured rendering and NetworkX analysis |
| **Phase 4** | Dialect unification, source-to-DOT generation, discovery pipeline integration | High | Strategic -- ecosystem-wide DOT standardization |

### Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Context strategy | Context sink pattern | Heavy docs (~1500 lines) load only when expert agents spawn; root sessions get ~80 lines |
| Dialect handling | Two separate guides + shared syntax reference | Pipeline DOT and architecture DOT serve fundamentally different purposes |
| DOT ownership | Layered -- dot-graph owns the language, Attractor owns pipeline runtime semantics | Avoids coupling general DOT expertise to a specific execution engine |
| Phase 1 tooling | None -- agents use `bash` + `dot` CLI | Simplest thing that works; validation tool adds novel value in Phase 2 |
| Primary dialect | Attractor shape-based with node_type as compatibility alias | More expressive, 3-4x more token-efficient, lower LLM error surface |

---

## Key Insights

The ten most important insights distilled across all eight documents:

1. **DOT is the only format spanning all five ecosystem layers** -- pipeline execution, architecture documentation, event specification, process visualization, and recipe visualization. No other format (YAML, Markdown, Python) captures structure and relationships in a way that is simultaneously machine-parseable, human-renderable, and LLM-interpretable. *(DOT-CONCEPTS-DEEP-DIVE, Section 1.2)*

2. **"DOT diagrams are discovery tools, not just documentation."** The act of creating a DOT diagram forces commitment to specific nodes, edges, and relationships -- preventing vague analysis. A DOT diagram revealed a cancellation gap that was invisible in prose. *(DOT-CONCEPTS-DEEP-DIVE, Section 1.3; SESSION-INDEX, Session c95ce204)*

3. **Two dialects exist and must not be conflated.** The Attractor pipeline dialect uses shapes as semantic dispatch keys (diamond = "conditional router, NO LLM call"). The architecture documentation dialect uses shapes as component types (diamond = "decision/transform"). The same shape means different things in different contexts. *(DOT-DIALECT-COMPARISON; ATTRACTOR-DOT-EXPERTISE, Appendix A)*

4. **The Attractor dialect is 3-4x more token-efficient than the node_type dialect.** A typical work node takes ~50 tokens in Attractor vs ~180 tokens in node_type. The model stylesheet eliminates per-node model configuration repetition. Convention over configuration wins. *(DOT-DIALECT-COMPARISON, Section 6.3)*

5. **The 150-250 line sweet spot is empirically validated.** The 158-line state-machine diagram was "the gem" -- renders beautifully, agent-scannable in minimal tokens. The 411 and 587-line outputs were "forensically thorough but would never render as a readable image." *(DOT-CONCEPTS-DEEP-DIVE, Section 8)*

6. **"Hand-maintained DOT files won't be maintained. Generate from source."** Three independent experts rejected hand-maintained DOT conventions. The bundle should emphasize LLM-synthesized DOT for architecture, generated-from-source DOT for structural relationships, and recognize pipeline DOT as inherently authored. *(DOT-CONCEPTS-DEEP-DIVE, Section 7.1; ATTRACTOR-DOT-EXPERTISE, Appendix C)*

7. **LLMs already know DOT.** DOT has been in training corpora since 1991. LLMs generate syntactically valid DOT far more reliably than alternatives. The formal BNF grammar means there's an unambiguous "right answer" for every construct. DOT's custom attribute system lets domain-specific metadata ride for free. *(DOT-ECOSYSTEM-RESEARCH, Section 6; ATTRACTOR-DOT-EXPERTISE, Section 1.1)*

8. **The context sink pattern is essential for DOT.** Heavy DOT documentation (~1500+ lines) must live in specialist agents, not root sessions. Root sessions get only a thin awareness pointer (~30 lines): "DOT capabilities exist, delegate to these agents." This is the difference between 80 lines of DOT context and 1500+. *(BUNDLE-GUIDANCE, Section 10; BOOTSTRAP-SYNTHESIS, Section 3)*

9. **70+ DOT files already exist across the ecosystem, but with no shared standards.** Tutorial pipelines, practical templates, architecture diagrams, event specifications, recipe visualizations -- all authored independently with ad-hoc conventions. The bundle's primary value is centralizing this fragmented expertise. *(ATTRACTOR-DOT-EXPERTISE, Appendix B; SESSION-INDEX, Summary Statistics)*

10. **Custom domain-specific validation is the biggest opportunity.** No existing tool validates DOT for workflow semantics, architecture quality standards, or dialect-specific conventions. A bundle that validates start/exit nodes, shape vocabularies, line count targets, rendered legends, and cluster naming would be genuinely novel. *(DOT-ECOSYSTEM-RESEARCH, Section 5; ATTRACTOR-DOT-EXPERTISE, Section 4)*

---

## Recommended Reading Order

For someone starting fresh with this discovery effort:

| Order | Document | Time | Why This Order |
|-------|----------|------|----------------|
| **1** | **This document** (`DISCOVERY-INDEX.md`) | 5 min | Orientation -- understand what exists and where to find it |
| **2** | [`BOOTSTRAP-SYNTHESIS.md`](BOOTSTRAP-SYNTHESIS.md) | 20 min | The actionable plan -- use cases, capabilities, architecture, phases, open questions |
| **3** | [`DOT-CONCEPTS-DEEP-DIVE.md`](DOT-CONCEPTS-DEEP-DIVE.md) | 15 min | The "why" -- understand the vision, evolution, and philosophical principles |
| **4** | [`DOT-DIALECT-COMPARISON.md`](DOT-DIALECT-COMPARISON.md) | 10 min | The critical dialect split -- essential context before writing any DOT guidance |
| **5** | [`BUNDLE-GUIDANCE.md`](BUNDLE-GUIDANCE.md) | 15 min | The implementation manual -- read when you're ready to create files |
| **6** | [`ATTRACTOR-DOT-EXPERTISE.md`](ATTRACTOR-DOT-EXPERTISE.md) | 10 min | Hard-won lessons -- read before writing pipeline DOT documentation |
| **7** | [`DOT-ARTIFACTS-CATALOG.md`](DOT-ARTIFACTS-CATALOG.md) | 10 min | The authoritative catalog -- reference as needed during implementation |
| **8** | [`DOT-ECOSYSTEM-RESEARCH.md`](DOT-ECOSYSTEM-RESEARCH.md) | 10 min | External ecosystem -- reference when making technology choices |
| **9** | [`SESSION-INDEX.md`](SESSION-INDEX.md) | 5 min | Session provenance -- skim for context, deep-read only to trace specific decisions |

**Shortcut for the impatient:** Read documents 1-3 (this index, synthesis, concepts). That's 80% of the value in 40 minutes.

---

## Next Steps

Moving from discovery to implementation:

### Immediate (Pre-Phase 1)

- [ ] **Resolve Q1 (Dialect Documentation Strategy):** Confirm Option B (separate pipeline + architecture guides with shared syntax reference) before content authoring begins
- [ ] **Resolve Q2 (Attractor DOT Ownership):** Confirm Option C (layered ownership -- dot-graph owns the language, Attractor owns pipeline runtime) before writing docs
- [ ] **Resolve Q5 (Hand-Maintained vs Generated Position):** Confirm Option C (pragmatic per-use-case guidance) before writing DOT_BEST_PRACTICES.md
- [ ] **Resolve Q6 (Registration Strategy):** Confirm Option B (standalone first, foundation-included after proving value) before creating bundle.md

### Phase 1: Minimal Viable Bundle

- [ ] Create `bundle.md` (thin root, ~15 lines YAML)
- [ ] Create `behaviors/dot-graph.yaml` (agents + thin context, no tools)
- [ ] Write `agents/dot-author.md` (context sink with heavy doc references)
- [ ] Write `agents/diagram-reviewer.md` (quality review specialist)
- [ ] Write `context/dot-graph-awareness.md` (~30 lines, thin pointer)
- [ ] Write `context/dot-graph-instructions.md` (~50 lines, consolidated)
- [ ] Write `docs/DOT_SYNTAX_REFERENCE.md` (adapt from existing DOT-SYNTAX.md + ecosystem research)
- [ ] Write `docs/DOT_PATTERNS.md` (synthesize patterns from all 70+ existing DOT files)
- [ ] Write `docs/DOT_BEST_PRACTICES.md` (adapt from dot-quality-standards.md + anti-patterns)
- [ ] Write `docs/PIPELINE_DOT_GUIDE.md` (adapt from DOT-AUTHORING-GUIDE.md)
- [ ] Write `docs/ARCHITECTURE_DOT_GUIDE.md` (adapt from synthesis-prompt.md + quality standards)
- [ ] Create `skills/dot-graph-syntax/SKILL.md` (adapt from dot-reference.md)
- [ ] Create `skills/dot-graph-patterns/SKILL.md` (copy-paste pattern templates)
- [ ] Validate bundle loads correctly with `amplifier run --bundle .`
- [ ] Test agent delegation flow (root session delegates to dot-author)

### Phase 2: Validation Tool

- [ ] Resolve Q3 (Tool Scope) and Q4 (node_type Compatibility)
- [ ] Adapt `dot_validation.py` (216 lines) into `modules/tool-dot-graph/validate.py`
- [ ] Implement `mount()` entry point with `validate` and `info` operations
- [ ] Add dialect auto-detection (Attractor vs node_type vs architecture)
- [ ] Test against existing DOT artifacts (54+ pipeline files, 4 architecture files)

### Future Phases

- [ ] Phase 3: Add rendering wrapper and NetworkX-based graph analysis
- [ ] Phase 4: Dialect unification support, source-to-DOT generation, discovery pipeline integration

---

*This document was created as part of the dot-graph-bundle bootstrap effort (session `a31d8d0c`). All source material is in the files listed in the Document Map above.*
