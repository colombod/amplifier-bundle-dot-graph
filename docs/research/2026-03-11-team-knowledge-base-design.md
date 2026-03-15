# Team Knowledge Base Design

## Goal

Build a shared, agent-readable knowledge base so that every Amplifier session starts aware of what the team has already built, what patterns to follow, and who owns what — eliminating duplicated effort and making the team's work compound instead of accumulate.

## Background

### The Problem

The Amplifier team produces a lot of work, but each person's output is opaque to everyone else's agents. Reading repos and PRs is technically possible but practically impossible at volume. The result:

- **Duplicated effort** — someone builds a tool or pattern and others don't know it exists
- **No shared conventions** — each person's work is a snowflake (testing, deployment, file layout)
- **New tools require human attention to adopt** — instead of fitting into paradigms agents already understand
- **Sessions can't coordinate** — which is the same problem as team members can't coordinate, because sessions are how people work

**The motivating example:** in a brainstorm session, the agent wasn't aware of the distro server's plugin architecture or the amplifierd daemon's existence, and proposed building a new coordination server from scratch. The right answer was to *discover what exists and slot into it.* The team knowledge base makes that the default behavior.

### Why This Matters Beyond Our Team

The Vibez group research (150+ practitioners, March 2026) surfaced a universal pattern: **everyone independently builds the same three things** — a memory/state layer, a review/validation loop, and some form of orchestration. All different implementations of the same abstract architecture. None interoperate. The coordination cost problem isn't unique to us — it's structural.

The external research confirms this. WorkGraph, Trycycle, Attractor, and others all converge on **stigmergic coordination** — agents coordinating through shared state rather than direct messaging. The team knowledge base applies this pattern at the team level: agents read and write to a shared legible surface, not to each other.

## Approach

A **git-hosted repo** that serves as the team's legible landscape. Agent-readable, incrementally refreshed, containing per-person dotfiles, capability descriptions, conventions, and inventory. Wrapped by a tool/bundle that abstracts away storage so agents interact through a clean query interface.

**Why a git repo and not a database or service:**
- Zero new infrastructure to deploy or maintain
- Versioned by default — every change is tracked
- Works offline, works locally, works on every developer's machine
- The repo *is* the coordination surface (stigmergic pattern — agents coordinate through shared state, not messages)
- Backend can change later without changing the consumer interface

**Why not just extend session-sync:** Session-sync handles live/dynamic data (what's happening now). This repo handles static/consumable data (what exists, what patterns to use). They're complementary layers. Session-sync is one input that feeds the repo, and can later index the repo for richer queries.

## Architecture

### Layered Discovery (Anti-Bloat Design)

An agent NEVER loads the whole repo. Discovery is progressive:

```
Layer 0 — Manifest (~100 lines)
  Agent reads ONE file and knows the shape of the landscape.
  Lists every person, capability, convention by name + one-liner.

Layer 1 — Capability Files (10-30 lines each)
  Agent reads only the 3-4 files relevant to its current task.

Layer 2 — Full Detail (conventions, dotfiles, activity)
  Only read when the agent has decided "this is relevant."
```

This mirrors how a human navigates a new codebase: table of contents → relevant section → deep dive. Token cost for a typical query: ~200 lines read, not thousands.

### Consumer Interfaces

Agents interact with the knowledge base two ways:

**1. The Tool (programmatic query interface)**

A bundle/tool called via standard Amplifier tool invocation. Abstracts away storage completely.

| Operation | What It Does | Example |
|-----------|-------------|---------|
| `search` | Semantic search via local vector index | `search(query="plugin architecture for adding capabilities to distro")` → 3-5 ranked results |
| `lookup` | Return a specific capability file | `lookup(name="distro-plugin-system")` → full YAML |
| `list` | Return manifest entries by category | `list(category="conventions")` → names + one-liners |
| `publish` | Write a new capability, regenerate index, commit | `publish(name="coordination-plugin", content={...})` |

Today this tool reads/writes the git repo and queries a local vector index. Tomorrow the same operations could hit session-sync or a database. The interface is stable regardless of backend.

**2. Dotfiles (direct file consumption)**

The `/dotfiles/` directory serves consumers that need raw files — Brian's visualization tools, dev-machines that want a person's full repo map. Format is whatever Brian's visualization tooling expects.

## Components

### Repo Structure

```
/manifest.yaml                    # Layer 0: table of contents (~100 lines)
                                  # Lists every person, capability, convention
                                  # by name + one-liner description

/people/<github-handle>/
    profile.yaml                  # Repos, ownership, skills, team (20-30 lines)
    activity.md                   # Generated from session-sync (recent work)

/capabilities/<name>.yaml         # One file per capability (10-30 lines each)
                                  # What it does, where it lives, how to use it,
                                  # who owns it
                                  # Examples: "distro-plugin-system",
                                  # "session-sync-search",
                                  # "amplifierd-session-fork",
                                  # "tdd-recipe-pattern"

/conventions/<name>.md            # Human-curated, team-approved patterns
                                  # "how-to-write-a-distro-plugin",
                                  # "testing-standards", "deployment-model",
                                  # "file-layout"

/dotfiles/<github-handle>/        # Brian's visualization format +
                                  # per-person generated dotfiles

/index/
    vectors.bin                   # Local vector DB (regenerated by tools)
    vectors.meta.json             # Metadata for the index

/tools/
    generate-person.py            # Crawls a person's repos → writes /people/
                                  # and /dotfiles/
    sync-activity.py              # Pulls from session-sync → updates activity.md
    index-capabilities.py         # Scans for bundles/plugins/tools →
                                  # writes /capabilities/
    rebuild-index.py              # Regenerates vector index from all YAML/MD
```

### Generation Pipeline

Three tools that populate the repo, each running independently:

#### generate-person

Each person runs this against their own repos. It:

1. Reads local clones of their repos
2. Scans for bundles, plugins, tools, patterns (pyproject.toml, bundle YAML, AppManifest files, recipe YAML)
3. Writes `/people/<handle>/profile.yaml` (repos, ownership, what they've built)
4. Writes `/dotfiles/<handle>/` (visualization format)
5. Writes or updates `/capabilities/<name>.yaml` for each discovered capability
6. Runs `rebuild-index` at the end

**Incremental by design:** checks each repo for changes since the last run (git log since last timestamp, stored in the profile). Only re-scans repos that changed. A no-change run takes seconds.

#### sync-activity

Calls session-sync's existing metrics API and analysis data. Writes `/people/<handle>/activity.md` with recent session summaries. Can flag "this person built something new" for the capabilities scanner.

Uses a "since" timestamp — session-sync already tracks what's new. Inherently incremental.

#### rebuild-index

Regenerates the vector index from all YAML/MD files. Called by other tools or manually. Diffs by file hash — only re-indexes changed files. Full rebuild available but shouldn't be needed often.

### Update Model

All generation tools are incremental. Triggered at **git push time** via a post-push hook. No cron to manage.

The cycle: person finishes a feature → pushes → post-push hook runs `generate-person` → diffs what changed → commits to the shared repo → next person's agent sees it at session start or via a query mid-session.

The `/conventions/` directory is **NOT generated** — it's human-curated. Team members write "how we do things" and it's versioned like any other doc.

### The team_knowledge Bundle

Ships as `amplifier-bundle-team-knowledge`. Any session that composes this bundle automatically has access to the team landscape.

The bundle:
- Includes the tool wrapping the query interface (search, lookup, list, publish)
- Can be included in the distro bundle, amplifierd's default bundle, or any personal bundle
- On session start (Phase C), a hook reads the manifest and injects a thin context summary: *"Your team has N capabilities, M people, K conventions available. Use `team_knowledge` to query."*

That's the nudge. The agent knows the landscape exists and can query it. It doesn't dump the whole repo into context.

## Data Flow

### Read Path (agent querying the knowledge base)

```
Agent receives task
  → Reads /manifest.yaml (Layer 0, ~100 lines)
  → Identifies 2-3 relevant capability names
  → Reads /capabilities/<name>.yaml (Layer 1, 10-30 lines each)
  → If needed, reads /conventions/<name>.md (Layer 2)
  → Proceeds with task, informed by existing landscape
```

Or via the tool:

```
Agent receives task
  → Calls team_knowledge(operation="search", query="...")
  → Tool queries local vector index
  → Returns 3-5 ranked capability files
  → Agent reads the relevant ones
```

### Write Path (publishing new knowledge)

```
Human says "make sure folks know about this pattern"
  → Agent calls team_knowledge(operation="publish", name="...", content={...})
  → Tool writes /capabilities/<name>.yaml
  → Runs rebuild-index
  → Commits to repo
  → Other agents see it on next query
```

### Generation Path (automated discovery)

```
Person pushes code
  → Post-push hook runs generate-person
  → Tool scans repos for new bundles/plugins/tools/patterns
  → Writes updated /people/ and /capabilities/ files
  → Runs rebuild-index
  → Commits results to shared repo
```

## Existing Infrastructure (Hard Constraints)

This design must plug into, not replace, the existing stack:

| Component | Owner(s) | Relevance |
|-----------|----------|-----------|
| **amplifier-distro** (port 8400) | Sam, team | AppManifest plugin system, 836 tests. Phase C plugin serves query interface over HTTP. |
| **amplifierd** (port 8410) | Microsoft upstream | Entry-point plugins, session fork/lineage. Phase C plugin alternative. |
| **amplifier-session-sync** | robotdad, marklicata | Production cloud service (Azure, Cosmos DB, Rust daemon, Claude analysis, 4-vector search, metrics API). Phase B data source. |
| **session-graph/** | Architecture proposal | Graph/topology layer on session-sync. Not yet built. Complementary. |

### Team Map

| Person | Handle | Key Ownership |
|--------|--------|---------------|
| Sam Schillace | samschillace | Lead, distro overall |
| Marc Goodner | robotdad | Session-sync, bridges, cloud |
| Mark Licata | marklicata | PM, Teams, containers/cloud |
| Brian Krabach | bkrabach | Voice/web/slack, dotfile visualization |
| MJ Jabbour | michaeljabbour | Kepler desktop |
| Paul Payne | payneio | Web-ui |
| Samuel Lee | samueljklee | Bundles |
| Devis Lucato | dluc | CLI |
| Diego Colombo | colombod | Session intelligence co-author |

## Error Handling

- **No-change runs are cheap.** If `generate-person` finds nothing new, it exits in seconds. No wasted commits.
- **Missing repos.** If a person hasn't cloned a repo locally, `generate-person` skips it and logs a warning. The profile is partial, not broken.
- **Session-sync unavailable.** `sync-activity` (Phase B) degrades gracefully — the repo works without activity data. Activity files just don't update.
- **Vector index corruption.** `rebuild-index` can do a full rebuild from source files. The index is derived, not primary.
- **Merge conflicts.** Each person writes to their own `/people/<handle>/` directory. Capability files are small and rarely edited concurrently. Conflicts should be rare; when they occur, standard git merge resolution applies.
- **Stale data.** The manifest includes last-updated timestamps per entry. Agents can filter by freshness if needed.

## Testing Strategy

- **Generation tools:** unit tests with fixture repos (known directory structures → expected YAML output). Integration tests that run `generate-person` against a real repo clone and verify output.
- **Query interface:** unit tests for search, lookup, list, publish operations. Mock vector index for deterministic results.
- **Vector index:** test that rebuild-index produces consistent results for the same inputs. Test incremental behavior (change one file, verify only that file re-indexed).
- **End-to-end:** create a test repo with known capabilities, run the full pipeline (generate → index → query), verify that `search("plugin architecture")` returns the expected capability file.
- **Bundle integration:** test that composing the bundle into a session makes the `team_knowledge` tool available and functional.

## Phased Delivery

### Phase A: Smart Repo

**What ships:**
- The repo structure (manifest, /people/, /capabilities/, /conventions/, /dotfiles/, /index/)
- Generation tools: `generate-person`, `index-capabilities`, `rebuild-index`
- Local vector index committed to the repo
- The `team_knowledge` tool/bundle wrapping queries against the local repo clone
- Post-push hook running generation and committing results

**Outcome:** Any agent composing the bundle can query the team landscape. Manual push/pull keeps it fresh.

### Phase B: Session-Sync Integration

**What ships:**
- `sync-activity` tool pulling from session-sync's existing APIs
- Session-sync extended to index repo contents alongside session transcripts
- Semantic search covers both "what people did" and "what exists"

**Outcome:** Richer queries, activity summaries, cross-referencing sessions with capabilities.

**Key constraint:** Session-sync is maintained by Marc and Mark. Phase B should be a minimal extension to their system — a new data source to index, not a new service to build. The API they already expose doesn't change; the corpus it searches over gets richer.

### Phase C: Ambient Plugin

**What ships:**
- Bundle includes a hook that injects thin manifest context on session start
- Distro server and/or amplifierd plugin serves the query interface over HTTP
- `publish` operation for humans to push new knowledge conversationally

**Outcome:** Every session is landscape-aware by default. Zero configuration.

Each phase builds on the last, nothing thrown away. Phase A is the foundation — usable standalone. B and C add richness.

## Relationship to Existing Systems

```
┌─────────────────────────────────────────────────────────┐
│                   TEAM KNOWLEDGE REPO                    │
│  manifest.yaml │ /people/ │ /capabilities/ │ /dotfiles/ │
└───────┬──────────────┬──────────────┬───────────────────┘
        │              │              │
   ┌────▼────┐   ┌─────▼─────┐  ┌────▼──────────┐
   │ Bundle  │   │ Session-  │  │ Brian's       │
   │ Tool    │   │ Sync      │  │ Visualization │
   │ (query) │   │ (Phase B  │  │ (dotfiles)    │
   └────┬────┘   │  input &  │  └───────────────┘
        │        │  indexing) │
   ┌────▼────┐   └───────────┘
   │ Any     │
   │ Agent   │
   │ Session │
   └─────────┘
```

- **Session-sync:** Complementary layers. Session-sync = live/dynamic (what's happening). This repo = static/consumable (what exists, what patterns to use). Session-sync feeds the repo (Phase B input) AND indexes it for richer queries.
- **Distro server / amplifierd:** The bundle/tool plugs into either. Phase C adds an HTTP-serving plugin.
- **Brian's dotfile visualization:** `/dotfiles/` directory serves this directly.

## Open Questions

1. **Vector DB choice** — DuckDB vss, sqlite-vec, FAISS index, or something else for the local vector index? Needs to be embeddable (no server), git-friendly (binary committed to repo), and fast enough for ~500 files.

2. **Dotfile format** — What format does Brian's visualization tooling expect? The `/dotfiles/` directory needs to align with his existing work.

3. **Capability YAML schema** — Proposed fields:
   ```yaml
   name: distro-plugin-system
   description: FastAPI plugin architecture for adding capabilities to the distro server
   repo: microsoft/amplifier-distro
   path: server/apps/
   owner: samschillace
   type: plugin-system  # bundle | plugin | tool | convention | pattern
   usage: |
     Create server/apps/<name>/__init__.py with AppManifest.
     Auto-discovered at startup.
   dependencies: []
   ```
   What fields actually matter? What's missing?

4. **Bundle composition** — How does `amplifier-bundle-team-knowledge` get into everyone's default bundle? Via distro bundle? Via personal bundles? Needs to be zero-friction.

5. **generate-person as recipe vs script** — Should `generate-person` be an Amplifier recipe (runs within the agent ecosystem, benefits from LLM reasoning for capability extraction) or a plain Python script (simpler, faster, deterministic)?
