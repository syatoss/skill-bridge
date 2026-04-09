# Anthropic Skills MCP Bridge

An MCP (Model Context Protocol) server that allows models that do not natively support Anthropic Agent Skills to discover and use them.

## Features

- **Bridging Skills**: Exposes Anthropic Agent Skills (`SKILL.md` files) as standard MCP Resources and Tools.
- **Auto-Discovery**: Recursively scans a directory for skills on startup.
- **Resource discovery**: Provides a list of all available skill frontmatters (names, descriptions, triggers) via the `skills://frontmatter` resource.
- **Tool discovery**: Provides a `get_skill` tool to fetch the full markdown content of any skill.
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
4. **Tool**: It exposes the `get_skill` tool. When an LLM decides it needs a specific skill, it calls this tool with the skill's name to get the full instructions and guidelines from the `SKILL.md` file.

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
