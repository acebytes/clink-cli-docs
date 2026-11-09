"""Call the custom tool over real stdio with a synthetic generation executable."""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class RepositoryMCP(unittest.TestCase):
    def test_discovery_and_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp).resolve()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "README.md").write_text("Stored in SQLite.\n")
            subprocess.run(["git", "-C", tmp, "add", "README.md"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    tmp,
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.invalid",
                    "-c",
                    "commit.gpgsign=false",
                    "commit",
                    "-qm",
                    "fixture",
                ],
                check=True,
            )
            fake = repo / "synthetic-clink"
            fake.write_text(
                "#!"
                + sys.executable
                + "\n"
                + """
import json, sys, time
from clink.native_generation_contracts import parse_native_request, terminal_native_result
assert sys.argv[1:] == ["generate", "--request-json", "-"]
request = parse_native_request(sys.stdin.buffer.read())
packet = json.loads(request.input)
assert packet["question"] == "Where is it stored?"
reply = {"answer": "SQLite.", "citations": [{"line": 1, "quote": "Stored in SQLite."}]}
result = terminal_native_result(started_at=time.monotonic(), request=request, status="completed", output=json.dumps(reply))
result["execution"]["admission"] = "verified"
print(json.dumps(result))
"""
            )
            fake.chmod(0o700)
            revision = subprocess.check_output(["git", "-C", tmp, "rev-parse", "HEAD"], text=True).strip()
            asyncio.run(self.exercise(repo, fake, revision))

    async def exercise(self, repo, fake, revision):
        env = {"HOME": str(repo), "PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}
        public = StdioServerParameters(
            command=sys.executable,
            args=[str(EXAMPLES / "repo_server.py"), "--repo", str(repo), "--file", "README.md"],
            env=env,
        )
        async with stdio_client(public) as streams, ClientSession(*streams) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            self.assertEqual([t.name for t in tools], ["ask_repo"])
            self.assertEqual(set(tools[0].inputSchema["properties"]), {"question"})
        bootstrap = "import sys;sys.path.insert(0,sys.argv[1]);from repo_server import make_server;make_server(sys.argv[2],'README.md',1,24,sys.argv[3]).run(transport='stdio')"
        synthetic = StdioServerParameters(
            command=sys.executable, args=["-c", bootstrap, str(EXAMPLES), str(repo), str(fake)], env=env
        )
        async with stdio_client(synthetic) as streams, ClientSession(*streams) as session:
            await session.initialize()
            result = await session.call_tool("ask_repo", {"question": "Where is it stored?"})
            self.assertFalse(result.isError, result.content)
            data = json.loads(result.content[0].text)
            self.assertEqual(
                data,
                {
                    "answer": "SQLite.",
                    "citations": [
                        {"revision": revision, "path": "README.md", "line": 1, "quote": "Stored in SQLite."}
                    ],
                },
            )


if __name__ == "__main__":
    unittest.main()
