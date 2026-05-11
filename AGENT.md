---
name: skill-bridge-setup
description: Use when setting up the Anthropic Skills MCP Bridge server for a new project. Handles dependency installation, configuration generation, and MCP integration.
---

# Anthropic Skills MCP Bridge - Setup Agent

## Purpose

This agent helps set up the **Anthropic Skills MCP Bridge** server so it can be plugged into any project via MCP configuration.

## Steps

### 1. Install Dependencies

Navigate to the skill-bridge project root and run:

```bash
uv sync
```

This installs all required Python dependencies into the project's `.venv`.

### 2. Prompt the User for Skills Directory

Ask the user:

> What is the **absolute path** to the directory containing your Anthropic Agent Skills (`SKILL.md` files)?

The user must provide a full absolute path (e.g., `C:\skills` or `/home/user/skills`).

### 3. Generate `mcp.example.json`

Create an `mcp.example.json` at the root of this project with the following structure. **All paths must be absolute.**

```json
{
  "servers": {
    "anthropic-skills-bridge": {
      "type": "stdio",
      "command": "<ABSOLUTE_PATH_TO_SKILL_BRIDGE>/.venv/Scripts/python.exe",
      "args": [
        "-m",
        "anthropic_skills_mcp",
        "--transport",
        "stdio"
      ],
      "env": {
        "ANTHROPIC_SKILLS_DIR": "<ABSOLUTE_PATH_TO_SKILLS_DIRECTORY>"
      }
    }
  }
}
```

Replace:
- `<ABSOLUTE_PATH_TO_SKILL_BRIDGE>` with the absolute path to the skill-bridge project root (where `pyproject.toml` lives).
- `<ABSOLUTE_PATH_TO_SKILLS_DIRECTORY>` with the absolute path the user provided in step 2.

On Linux/macOS, use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

### 4. Instruct the User

Tell the user to copy the content of `mcp.example.json` into their target project's MCP configuration file:

- **VS Code**: `.vscode/mcp.json`
- **Claude Desktop**: `claude_desktop_config.json`

The `"anthropic-skills-bridge"` server block should be merged into the existing `"servers"` (or `"mcpServers"` for Claude Desktop) object.

## Key Constraints

- The `command` field MUST use the absolute path to the `.venv` Python executable inside this project.
- The `ANTHROPIC_SKILLS_DIR` env var MUST be an absolute path to the user's skills directory.
- Never use relative paths in the generated configuration.
- The server is invoked via `python -m anthropic_skills_mcp` — the package must be installed in the venv first (`uv sync`).

## Available MCP Tools

Once configured, the server exposes the following tools to MCP clients:

| Tool | Description |
|------|-------------|
| `list_skills` | Lists all available skills with `name`, `description`, and `triggers`. Primary discovery mechanism. |
| `get_skill` | Returns a skill's full YAML frontmatter (as JSON) and markdown body by name. |
| `get_skill_reference` | Fetches auxiliary files from a skill's directory (e.g., `references/patterns.md`). Path-traversal protected. |
| `reload_skills` | Re-scans the skills directory and refreshes the cache without restarting the server. |
