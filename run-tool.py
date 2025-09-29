#!/usr/bin/env python3
import argparse
import asyncio
import sys

from mcp.client.stdio import stdio_client


DEFAULT_SERVER_CMD = ["uv", "run", "dooray-mcp"]


async def run_tool(server_cmd, tool_name, args_dict):
    # MCP 서버를 subprocess로 실행
    proc = await asyncio.create_subprocess_exec(
        *server_cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    async with stdio_client(proc.stdout, proc.stdin) as client:
        await client.initialize()
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]

        if tool_name not in tool_names:
            print(f"❌ Tool '{tool_name}' not found. Available: {tool_names}")
            await client.shutdown()
            return

        result = await client.call_tool(tool_name, args_dict)
        print("✅ Result:", result)

        await client.shutdown()

def main():
    parser = argparse.ArgumentParser(description="Run MCP tool from CLI")
    parser.add_argument("tool", help="Tool name to call")
    parser.add_argument(
        "params",
        nargs=argparse.REMAINDER,
        help="Arguments for tool (e.g. --action list --taskId 123)",
    )
    args = parser.parse_args()

    # params 파싱 (--a 2 → {"a": 2})
    params_dict = {}
    it = iter(args.params)
    for k in it:
        if k.startswith("--"):
            key = k[2:]
            val = next(it, None)
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    pass
            params_dict[key] = val

    asyncio.run(run_tool(DEFAULT_SERVER_CMD, args.tool, params_dict))

if __name__ == "__main__":
    main()
