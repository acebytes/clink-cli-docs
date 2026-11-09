"""Serve the accompanying ask_repo.py as one local stdio MCP tool."""

import argparse
import sys
from pathlib import Path

from ask_repo import ask_repo as answer_from_file
from mcp.server.fastmcp import FastMCP


def make_server(repo, file, first, count, clink):
    server = FastMCP("repository-questions")

    @server.tool()
    def ask_repo(question: str) -> dict:
        """Answer a question from the configured committed file, with exact line citations."""
        return answer_from_file(repo, file, question, first=first, count=count, clink=clink)

    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--file", required=True)
    parser.add_argument("--first-line", type=int, default=1)
    parser.add_argument("--count", type=int, default=24)
    args = parser.parse_args()
    # Use the Clink installed in this server's virtual environment, independent of the host's PATH.
    executable = Path(sys.executable).with_name("clink")
    make_server(args.repo.resolve(strict=True), args.file, args.first_line, args.count, executable).run(
        transport="stdio"
    )
