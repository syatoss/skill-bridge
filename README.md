# Anthropic Skills MCP Bridge

An MCP (Model Context Protocol) server that allows models that do not natively support Anthropic Agent Skills to discover and use them.

## Features

- **Bridging Skills**: Exposes Anthropic Agent Skills (`SKILL.md` files) as standard MCP Resources and Tools.
- **Auto-Discovery**: Recursively scans a directory for skills on startup.
- **Resource discovery**: Provides a list of all available skill frontmatters (names, descriptions, triggers) via the `skills://frontmatter` resource.
- **Tool: list_skills**: Lists all available skills with names, descriptions, and triggers — the primary discovery mechanism for VS Code Copilot.
- **Tool: get_skill**: Fetches the full content and frontmatter of a specific skill.
- **Tool: get_skill_reference**: Retrieves reference files from a skill's subdirectory (e.g., `references/advanced-types.md`).
- **Tool: reload_skills**: Hot-reloads skills from disk without restarting the server.
- **Dual Transport**: Supports both `STDIO` (for local use) and `SSE` (HTTP-based) transports.

## Installation

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone <repo-url>
cd anthropic-skills-mcp

# Install dependencies
uv sync
```

## Usage

### Environment Variable

The server requires the `ANTHROPIC_SKILLS_DIR` environment variable to be set to the absolute path of the directory containing your skills.

```bash
export ANTHROPIC_SKILLS_DIR="/path/to/your/skills"
```

### Running with STDIO (Default)

```bash
uv run python -m anthropic_skills_mcp
```

### Running with SSE (HTTP)

```bash
uv run python -m anthropic_skills_mcp --transport sse --port 8000
```

## How it works

1. **Initialization**: On startup, the server scans the `ANTHROPIC_SKILLS_DIR` recursively.
2. **Parsing**: It identifies every `SKILL.md` file and parses its YAML frontmatter.
3. **Resource**: It exposes `skills://frontmatter`. When an LLM reads this resource, it receives a JSON list of all skill metadata, helping it decide which skill is relevant to the current task.
4. **Tools**:
   - `list_skills` — Returns a JSON array of all skills with `name`, `description`, and `triggers`. This is the primary discovery mechanism for MCP clients like VS Code Copilot.
   - `get_skill` — Returns both the YAML frontmatter (as JSON) and the full markdown body of a skill.
   - `get_skill_reference` — Fetches auxiliary files (e.g., `references/patterns.md`) from within a skill's directory. Includes path traversal protection.
   - `reload_skills` — Re-scans the skills directory and refreshes the internal cache without restarting the server.

## Skill Format

The skills must follow the Anthropic format:

```markdown
---
name: my-skill
description: Use when the user asks for X.
---

# My Skill
Detailed instructions here...
```

The file MUST be named `SKILL.md` and reside in its own subdirectory within the `ANTHROPIC_SKILLS_DIR`.
