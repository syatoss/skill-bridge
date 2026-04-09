import argparse
import asyncio
import os
import sys
from .server import AnthropicSkillsServer

def main():
    parser = argparse.ArgumentParser(description="Anthropic Skills MCP Bridge Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="stdio",
        help="The transport to use (default: stdio)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="The host to bind for SSE transport (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="The port to bind for SSE transport (default: 8000)"
    )
    parser.add_argument(
        "--skills-dir",
        default=os.environ.get("ANTHROPIC_SKILLS_DIR"),
        help="The directory containing the skills (default: ANTHROPIC_SKILLS_DIR env var)"
    )

    args = parser.parse_args()

    if not args.skills_dir:
        print("Error: Skills directory not specified. Use --skills-dir or set ANTHROPIC_SKILLS_DIR.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.skills_dir):
        print(f"Error: Skills directory '{args.skills_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    server = AnthropicSkillsServer(args.skills_dir)
    
    try:
        asyncio.run(server.run(transport=args.transport, host=args.host, port=args.port))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
