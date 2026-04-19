# OmnethDB

[![CI](https://github.com/ubcent/omnethdb/actions/workflows/ci.yml/badge.svg)](https://github.com/ubcent/omnethdb/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/ubcent/omnethdb)](https://github.com/ubcent/omnethdb/releases)
[![Go Version](https://img.shields.io/badge/go-1.24%2B-00ADD8)](https://go.dev/)
[![License](https://img.shields.io/github/license/ubcent/omnethdb)](LICENSE)

```text
   ____                       __  __    ____  ____
  / __ \____ ___  ____  ___  / /_/ /_  / __ \/ __ )
 / / / / __ `__ \/ __ \/ _ \/ __/ __ \/ / / / __  |
/ /_/ / / / / / / / / /  __/ /_/ / / / /_/ / /_/ /
\____/_/ /_/ /_/_/ /_/\___/\__/_/ /_/_____/_____/
```

OmnethDB is an embedded, versioned memory database for autonomous agents.

It is not a vague "AI memory layer", not a flat vector store, and not a chat-history cache.
It is a serious memory primitive for project knowledge: explicit lineage, typed relations, governed writes, auditable history, and retrieval that prefers current truth over stale-but-similar text.

## Why This Exists

LLMs forget everything between runs.
Real work does not.

Agents working on a codebase keep rediscovering the same facts:

- why a weird config is intentional
- which architecture rule is non-negotiable
- what incident already happened before
- which old statement is now obsolete

Most "memory" systems store all of that in one blob and hope retrieval sorts it out later.
That creates a dangerous failure mode: the agent remembers the wrong thing with high confidence.

OmnethDB exists to solve that semantic problem, not just the storage problem.

## What Makes OmnethDB Different

- `Updates` is a real state transition, not a loose tag. When one memory supersedes another, retrieval sees the new truth.
- `Static`, `Episodic`, and `Derived` mean different things and are governed differently.
- `Forget` does not delete history. It records lifecycle explicitly.
- relations are typed and auditable
- write policy is explicit
- trust is policy-driven
- retrieval and inspection are separate jobs

If you want the full contract, read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Start Here

If you are new to the repo:

1. Read [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
2. Read [docs/CONCEPTS.md](docs/CONCEPTS.md)
3. Use [docs/SETUP.md](docs/SETUP.md) to configure a real workspace
4. Use [docs/RELEASING.md](docs/RELEASING.md) if you want to ship binaries and publish releases
5. Use [docs/INDEX.md](docs/INDEX.md) when you need the full planning and architecture stack

## Install

Install the published binaries and put these executables on your `PATH`:

- `omnethdb`
- `omnethdb-mcp`

Quick install:

```bash
curl -fsSL https://raw.githubusercontent.com/ubcent/omnethdb/main/scripts/install.sh | sh
```

Install a specific version:

```bash
curl -fsSL https://raw.githubusercontent.com/ubcent/omnethdb/main/scripts/install.sh | VERSION=v0.1.0 sh
```

The script installs to `~/.local/bin` by default. Override with `INSTALL_DIR=/your/bin/dir`.

## Five-Minute Quickstart

See the full walkthrough in [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

Ask the CLI what it can do:

```bash
omnethdb help
```

Create a workspace config:

```toml
[spaces."repo:company/app"]
default_weight = 1.0
half_life_days = 30
max_static_memories = 500
max_episodic_memories = 10000
profile_max_static = 20
profile_max_episodic = 10

[spaces."repo:company/app".embedder]
model_id = "builtin/hash-embedder-v1"
dimensions = 256
```

Bootstrap the space:

```bash
omnethdb init \
  --workspace . \
  --space repo:company/app
```

Write a stable fact:

```bash
omnethdb remember \
  --workspace . \
  --space repo:company/app \
  --kind static \
  --actor-id user:alice \
  --actor-kind human \
  --content "payments use cursor pagination"
```

Recall current live knowledge:

```bash
omnethdb recall \
  --workspace . \
  --spaces repo:company/app \
  --query pagination \
  --top-k 5
```

## Daily Workflow

The normal loop is simple:

1. `profile` or `recall` before work
2. `lineage` before updating an existing fact
3. `remember --update ...` when reality changed
4. `related` when you need to inspect explicit graph links
5. `audit` when you need the change trail

If you are using OmnethDB as a real operating memory for agents, this is the habit to build:

- read before writing
- update instead of duplicating
- write only durable facts or meaningful incidents
- derive only from multiple current sources with a rationale

## CLI Surface

Main commands:

- `init`: bootstrap a space
- `remember`: write a memory
- `lint-remember`: preview duplicate/update warnings before writing
- `recall`: query live memories
- `profile`: build a layered memory profile
- `forget`: forget a memory without deleting history
- `revive`: revive an inactive lineage
- `lineage`: inspect version history
- `related`: traverse explicit relations
- `candidates`: raw candidate search for curation and authoring
- `quality`, `quality-plan`, `quality-report`: inspect memory quality and cleanup opportunities
- `synthesis-candidates`, `promotion-suggestions`: curator-facing advisory review flows
- `audit`: inspect audit history
- `export`: render snapshot, markdown summary, or Mermaid graph
- `migrate`: migrate a space to a new embedder
- `space`, `space validate-config`, `space diff-config`, `space apply-config`: inspect and reconcile persisted config
- `config`: print workspace layout and loaded runtime config
- `serve`: run the HTTP API
- `serve-grpc`: run the gRPC API

## Interfaces

### Embedded Go library

The root package `omnethdb` is the supported public facade.

### CLI

The main operator entrypoint is `cmd/omnethdb`.

### MCP

OmnethDB ships with a local stdio MCP server:

```bash
omnethdb-mcp --workspace .
```

A Claude Code starter pack lives in [examples/claude-code/README.md](examples/claude-code/README.md).

### HTTP API

Run:

```bash
omnethdb serve --workspace . --addr :8080
```

### gRPC API

Run:

```bash
omnethdb serve-grpc --workspace . --addr :9090
```

Proto contract:

- [proto/omnethdb/v1/omnethdb.proto](proto/omnethdb/v1/omnethdb.proto)

## Repo Layout

- `cmd/omnethdb/`: CLI
- `cmd/omnethdb-mcp/`: MCP server
- `internal/memory/`: domain model and validation
- `internal/policy/`: governance and trust resolution
- `internal/store/bolt/`: bbolt-backed storage and transactional semantics
- `internal/httpapi/`: HTTP transport
- `internal/grpcapi/`: gRPC transport
- `internal/mcp/`: MCP tool surface
- `embedders/hash/`: built-in deterministic embedder
- `examples/`: runnable examples and integration samples
- `docs/`: architecture, planning stack, onboarding, and operator docs

## Planning And Architecture

The full planning stack lives in [docs/INDEX.md](docs/INDEX.md).

Most important source-of-truth docs:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/SPEC_MAP_V1.md](docs/SPEC_MAP_V1.md)
- [docs/CAPABILITY_MAP_V1.md](docs/CAPABILITY_MAP_V1.md)
- [docs/UAT_MAP_V1.md](docs/UAT_MAP_V1.md)
- [docs/BACKLOG_V1.md](docs/BACKLOG_V1.md)
- [docs/MILESTONE_PLAN_V1.md](docs/MILESTONE_PLAN_V1.md)
- [docs/RELEASING.md](docs/RELEASING.md)

## Working Standard

The bar in this repo is intentionally high:

- semantic correctness over fuzzy convenience
- explicit behavior over hidden magic
- inspectable state transitions over "it probably works"
- operator simplicity without product compromise
- docs that help the next person move faster instead of reverse-engineering intent

That standard applies to the documentation too.
