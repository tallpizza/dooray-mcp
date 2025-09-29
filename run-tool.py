#!/usr/bin/env python3
import argparse
import asyncio
import os
import sys

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


DEFAULT_SERVER_CMD = ["uv", "run", "dooray-mcp"]
DEFAULT_ENV = {
    "DOORAY_API_TOKEN": "spuio91dvw2b:09_758iFSlKyvtcsfVa6JA",
    "DOORAY_BASE_URL": "https://api.dooray.com",
    "DOORAY_DEFAULT_PROJECT_ID": "4083027435241316930",
    "PYTHONUNBUFFERED": "1",
    "PYENV_VERSION": "3.12.2",
}


async def run_tool(server_cmd, tool_name, args_dict, list_only=False):
    # MCP 서버 실행 파라미터 구성
    env = os.environ.copy()
    env.update(DEFAULT_ENV)

    server = StdioServerParameters(
        command=server_cmd[0],
        args=server_cmd[1:],
        env=env,
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            tools_result = await client.list_tools()
            tool_names = [t.name for t in tools_result.tools]

            if list_only:
                print("🔧 Available tools:")
                for name in tool_names:
                    print(f" - {name}")
                return

            if tool_name is None:
                raise ValueError("Tool name is required when --list-tools is not specified")

            if tool_name not in tool_names:
                print(f"❌ Tool '{tool_name}' not found. Available: {tool_names}")
                return

            result = await client.call_tool(tool_name, args_dict)
            print("✅ Result:", result)

def main():
    parser = argparse.ArgumentParser(description="Run MCP tool from CLI")
    parser.add_argument("tool", nargs="?", help="Tool name to call")
    parser.add_argument(
        "--list-tools",
        dest="list_tools",
        action="store_true",
        help="List available tools and exit",
    )
    parser.add_argument(
        "params",
        nargs=argparse.REMAINDER,
        help="Arguments for tool (e.g. --action list --taskId 123)",
    )
    args = parser.parse_args()

    def coerce_value(raw: str | None):
        if raw is None:
            return None

        text = str(raw)
        if text.startswith("--"):
            return text

        integer_like = text.lstrip("-")
        if integer_like.isdigit():
            if len(integer_like) <= 9:
                try:
                    return int(text)
                except ValueError:
                    return text
            return text

        try:
            value = float(text)
        except ValueError:
            return text

        if any(sep in text for sep in (".", "e", "E")):
            return value

        return text

    params_dict = {}
    it = iter(args.params)
    for k in it:
        if k.startswith("--"):
            key = k[2:]
            val = coerce_value(next(it, None))
            params_dict[key] = val

    if args.list_tools:
        asyncio.run(run_tool(DEFAULT_SERVER_CMD, None, {}, list_only=True))
        return

    if args.tool is None:
        parser.error("tool is required unless --list-tools is supplied")

    asyncio.run(run_tool(DEFAULT_SERVER_CMD, args.tool, params_dict))

if __name__ == "__main__":
    main()
