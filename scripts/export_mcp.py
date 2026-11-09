"""Export the released stdio server's default tools and prompts for this site."""

import asyncio
import json
import sys
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

RELEASE = "0.2.3"
DESTINATION = Path(__file__).resolve().parents[1] / "public" / "data" / "mcp-v0.2.3.json"


async def collect():
    if version("clink-cli") != RELEASE:
        raise RuntimeError(f"Install clink-cli=={RELEASE} in the exporting environment.")
    binary = Path(sys.executable).parent / "clink-mcp-server"
    with TemporaryDirectory() as isolated:
        server = StdioServerParameters(
            command=str(binary),
            cwd=isolated,
            env={"HOME": isolated, "PATH": str(binary.parent), "DISABLED_TOOLS": ""},
        )
        async with stdio_client(server) as (reader, writer), ClientSession(reader, writer) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            prompts = (await session.list_prompts()).prompts
    return {
        "release": RELEASE,
        "tools": [
            tool.model_dump(mode="json", exclude_none=True) for tool in sorted(tools, key=lambda t: t.name)
        ],
        "prompts": [
            p.model_dump(mode="json", exclude_none=True) for p in sorted(prompts, key=lambda p: p.name)
        ],
    }


if __name__ == "__main__":
    snapshot = asyncio.run(collect())
    if len(snapshot["tools"]) != 18 or len(snapshot["prompts"]) != 19:
        raise RuntimeError("Unexpected inventory. Check the release and configuration before publishing.")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
