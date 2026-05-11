import json
import logging
import os
from typing import Dict, Any, List

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ResourceContents,
    TextResourceContents,
)

from .parser import load_skills, Skill

# Configure logging to stderr for stdio transport
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=os.sys.stderr
)
logger = logging.getLogger(__name__)


class AnthropicSkillsServer:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self.server = Server("anthropic-skills-bridge")

        # Load skills on initialization (Pre-load on Startup)
        self._load_all_skills()
        self._setup_handlers()

    def _load_all_skills(self):
        logger.info(f"Loading skills from {self.skills_dir}...")
        self.skills = load_skills(self.skills_dir)
        logger.info(f"Successfully loaded {len(self.skills)} skills.")

    def _setup_handlers(self):
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            return [
                Resource(
                    uri="skills://frontmatter",
                    name="Available Skills Frontmatter",
                    description="Returns a JSON list of all available skill frontmatters including names and trigger descriptions.",
                    mimeType="application/json",
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: Any) -> str:
            if str(uri) == "skills://frontmatter":
                frontmatters = [skill.frontmatter for skill in self.skills.values()]
                return json.dumps(frontmatters, indent=2)
            raise ValueError(f"Resource not found: {uri}")

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="list_skills",
                    description="Lists all available Anthropic Agent Skills with their names, descriptions, and metadata triggers.",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="get_skill",
                    description="Fetches the full markdown content of an Anthropic Agent Skill by its name, including frontmatter metadata.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The unique name of the skill to fetch.",
                            }
                        },
                        "required": ["name"],
                    },
                ),
                Tool(
                    name="get_skill_reference",
                    description="Fetches the content of a reference file within a skill's directory (e.g., 'references/advanced-types.md').",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "The unique name of the skill.",
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to the file within the skill's directory.",
                            },
                        },
                        "required": ["skill_name", "file_path"],
                    },
                ),
                Tool(
                    name="reload_skills",
                    description="Re-scans the skills directory and reloads all skills. Use after adding or updating skill files.",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            if name == "list_skills":
                skills_list = [
                    {
                        "name": skill.name,
                        "description": skill.description,
                        "triggers": skill.frontmatter.get("triggers", []),
                    }
                    for skill in self.skills.values()
                ]
                return [
                    TextContent(type="text", text=json.dumps(skills_list, indent=2))
                ]

            if name == "get_skill":
                skill_name = arguments.get("name")
                if not skill_name:
                    return [
                        TextContent(type="text", text="Error: Skill name is required.")
                    ]

                skill = self.skills.get(skill_name)
                if not skill:
                    return [
                        TextContent(
                            type="text", text=f"Skill '{skill_name}' not found."
                        )
                    ]

                response = {"frontmatter": skill.frontmatter, "content": skill.content}
                return [TextContent(type="text", text=json.dumps(response, indent=2))]

            if name == "get_skill_reference":
                skill_name = arguments.get("skill_name")
                file_path = arguments.get("file_path")

                if not skill_name or not file_path:
                    return [
                        TextContent(
                            type="text",
                            text="Error: Both 'skill_name' and 'file_path' are required.",
                        )
                    ]

                skill = self.skills.get(skill_name)
                if not skill:
                    return [
                        TextContent(
                            type="text", text=f"Skill '{skill_name}' not found."
                        )
                    ]

                # Security: reject absolute paths and path traversal
                if (
                    os.path.isabs(file_path)
                    or ".." in file_path.split(os.sep)
                    or ".." in file_path.split("/")
                ):
                    return [
                        TextContent(
                            type="text",
                            text="Error: Invalid file path. Must be a relative path without '..' components.",
                        )
                    ]

                resolved_path = os.path.realpath(
                    os.path.join(skill.directory, file_path)
                )
                skill_dir_real = os.path.realpath(skill.directory)

                if (
                    not resolved_path.startswith(skill_dir_real + os.sep)
                    and resolved_path != skill_dir_real
                ):
                    return [
                        TextContent(
                            type="text",
                            text="Error: File path resolves outside the skill directory.",
                        )
                    ]

                if not os.path.isfile(resolved_path):
                    return [
                        TextContent(
                            type="text",
                            text=f"Error: File '{file_path}' not found in skill '{skill_name}'.",
                        )
                    ]

                try:
                    with open(resolved_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    return [TextContent(type="text", text=content)]
                except Exception as e:
                    return [TextContent(type="text", text=f"Error reading file: {e}")]

            if name == "reload_skills":
                self._load_all_skills()
                return [
                    TextContent(
                        type="text",
                        text=f"Skills reloaded successfully. {len(self.skills)} skills available.",
                    )
                ]

            raise ValueError(f"Tool not found: {name}")

    async def run(
        self, transport: str = "stdio", host: str = "0.0.0.0", port: int = 8000
    ):
        """Runs the MCP server using the specified transport."""
        if transport == "stdio":
            from mcp.server.stdio import stdio_server

            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
        elif transport == "sse":
            from mcp.server.sse import SseServerTransport
            from starlette.applications import Starlette
            from starlette.routing import Route
            import uvicorn

            sse = SseServerTransport("/messages")

            async def handle_sse(request):
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        self.server.create_initialization_options(),
                    )

            async def handle_messages(request):
                await sse.handle_post_message(
                    request.scope, request.receive, request._send
                )

            app = Starlette(
                routes=[
                    Route("/sse", endpoint=handle_sse),
                    Route("/messages", endpoint=handle_messages, methods=["POST"]),
                ]
            )

            config = uvicorn.Config(app, host=host, port=port)
            server = uvicorn.Server(config)
            await server.serve()
        else:
            raise ValueError(f"Unsupported transport: {transport}")
