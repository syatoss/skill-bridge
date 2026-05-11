import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def verify():
    # Set the environment variable
    skills_dir = os.path.abspath("test_skills")
    os.environ["ANTHROPIC_SKILLS_DIR"] = skills_dir

    print(f"Verifying MCP Server with skills from: {skills_dir}")

    # Parameters to run our server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "anthropic_skills_mcp"],
        env=os.environ.copy(),
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                print("Initializing session...")
                await session.initialize()

                # List Resources
                print("\nListing resources:")
                resources = await session.list_resources()
                print(resources)

                # Read Resource
                print("\nReading resource 'skills://frontmatter':")
                result = await session.read_resource("skills://frontmatter")
                print(result)

                # List Tools
                print("\nListing tools:")
                tools = await session.list_tools()
                print(tools)

                # Call list_skills
                print("\nCalling tool 'list_skills':")
                skills_list = await session.call_tool("list_skills", arguments={})
                print(skills_list)

                # Call get_skill
                print("\nCalling tool 'get_skill' for 'git-helper':")
                skill_content = await session.call_tool(
                    "get_skill", arguments={"name": "git-helper"}
                )
                print(skill_content)

                # Call get_skill_reference (expected to fail gracefully if no references exist)
                print(
                    "\nCalling tool 'get_skill_reference' for 'git-helper', file 'references/test.md':"
                )
                ref_content = await session.call_tool(
                    "get_skill_reference",
                    arguments={
                        "skill_name": "git-helper",
                        "file_path": "references/test.md",
                    },
                )
                print(ref_content)

                # Call reload_skills
                print("\nCalling tool 'reload_skills':")
                reload_result = await session.call_tool("reload_skills", arguments={})
                print(reload_result)

                print("\nVerification complete!")

    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(verify())
