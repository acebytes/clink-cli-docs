"""Check rendered examples against the public release. Run after npm run build."""

import json
import os
import tempfile
from html.parser import HTMLParser
from importlib.metadata import version
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]


class CodeBlocks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.in_pre = False

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.blocks.append("")
            self.in_pre = True

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False

    def handle_data(self, text):
        if self.in_pre:
            self.blocks[-1] += text


def main():
    if version("clink-cli") != "0.2.3":
        raise ValueError("Install clink-cli==0.2.3 to verify this catalog.")
    snapshot = json.loads((ROOT / "public/data/mcp-v0.2.3.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        os.environ.update(HOME=tmp, DISABLED_TOOLS="")
        os.environ.pop("CLI_CLIENTS_CONFIG_PATH", None)
        os.chdir(tmp)
        from server import TOOLS

        fixture = Path(tmp)
        (fixture / "src").mkdir()
        (fixture / "src/parser.py").write_text("# Fixture\n")
        assert set(TOOLS) == {t["name"] for t in snapshot["tools"]}
        for tool in snapshot["tools"]:
            name = tool["name"]
            parser = CodeBlocks()
            parser.feed((ROOT / f"dist/mcp/tools/{name}/index.html").read_text())
            example, schema = map(json.loads, parser.blocks)
            assert schema == tool["inputSchema"] == TOOLS[name].get_input_schema(), name
            validate(example, schema)
            bound = json.loads(json.dumps(example).replace("/absolute/path/to/your-project", str(fixture)))
            TOOLS[name].get_request_model()(**bound)
        print(
            f"Validated all {len(TOOLS)} rendered examples and schemas against Clink {version('clink-cli')}."
        )
    for name in ("ask_repo.py", "repo_server.py"):
        assert (ROOT / "examples" / name).read_bytes() == (ROOT / "dist/examples" / name).read_bytes(), name


if __name__ == "__main__":
    main()
