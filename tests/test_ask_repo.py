import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from clink.native_generation_contracts import (
    parse_native_request,
    terminal_native_result,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))
import ask_repo as guide


class RepositoryExample(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name).resolve()

        def git(*args):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

        git("init", "-q")
        (self.repo / "README.md").write_bytes("# Library\r\nSaved prompts use SQLite — locally.\r\n".encode())
        (self.repo / "alias.md").symlink_to("README.md")
        git("add", "README.md", "alias.md")
        git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-m",
            "fixture",
        )
        self.quote = "Saved prompts use SQLite — locally."
        self.root, self.packet = guide.capture(self.repo, "README.md", "Where is storage?", 2, 5)
        self.request = guide.make_request(self.root, self.packet)
        self.reply = {"answer": "It uses SQLite.", "citations": [{"line": 2, "quote": self.quote}]}

    def envelope(self, request, reply):
        # Use the released encoder and parser for hashes and identity, independent of the example.
        parsed = parse_native_request(json.dumps(request).encode())
        result = terminal_native_result(
            started_at=time.monotonic(), request=parsed, status="completed", output=json.dumps(reply)
        )
        result["execution"]["admission"] = "verified"
        return result

    def test_committed_lines_ignore_working_changes(self):
        (self.repo / "README.md").write_text("uncommitted\n")
        root, packet = guide.capture(self.repo, "README.md", "Where is storage?", 2, 5)
        self.assertEqual((root, packet), (self.root, self.packet))
        self.assertEqual(packet["lines"], [{"line": 2, "text": self.quote}])

    def test_rejects_paths_and_empty_ranges(self):
        for file in ("alias.md", "../README.md", str(self.repo / "README.md"), "untracked", "./README.md"):
            with self.subTest(file=file), self.assertRaises(guide.AskError):
                guide.capture(self.repo, file, "Question?")
        for first, count in ((0, 1), (8, 2), (1, 49)):
            with self.subTest(first=first, count=count), self.assertRaises(guide.AskError):
                guide.capture(self.repo, "README.md", "Question?", first, count)

    def test_real_helper_sends_one_request(self):
        actual_run = subprocess.run
        sent = []

        def run(argv, **kwargs):
            if argv[0] == "git":
                return actual_run(argv, **kwargs)
            sent.append(argv)
            req = json.loads(kwargs["input"])
            self.assertEqual(json.loads(req["input"]), self.packet)
            return subprocess.CompletedProcess(argv, 0, json.dumps(self.envelope(req, self.reply)).encode())

        with patch.object(guide.subprocess, "run", side_effect=run):
            answer = guide.ask_repo(self.repo, "README.md", "Where is storage?", first=2, count=5)
        self.assertEqual(sent, [["clink", "generate", "--request-json", "-"]])
        self.assertEqual(
            answer["citations"],
            [{"revision": self.packet["revision"], "path": "README.md", "line": 2, "quote": self.quote}],
        )

    def test_explicit_abstention(self):
        reply = {"answer": None, "citations": []}
        self.assertEqual(
            guide.verify_result(self.request, self.packet, 0, self.envelope(self.request, reply)), reply
        )

    def test_refuses_unmatched_responses(self):
        valid = self.envelope(self.request, self.reply)
        for key, value in (
            ("status", "incomplete"),
            ("truncated", True),
            ("schema_version", 2),
            ("input_sha256", ""),
            ("instructions_sha256", ""),
            ("request_sha256", ""),
            ("request_id", ""),
            ("execution", {}),
            ("output", "unstructured"),
        ):
            with self.subTest(key=key), self.assertRaises(guide.AskError):
                guide.verify_result(self.request, self.packet, 0, {**valid, key: value})
        with self.assertRaises(guide.AskError):
            guide.verify_result(self.request, self.packet, 1, valid)

    def test_rejects_wrong_duplicate_and_missing_quotes(self):
        for citations in (
            [],
            [{"line": 3, "quote": self.quote}],
            [{"line": 2, "quote": "invented"}],
            [{"line": True, "quote": self.quote}],
            self.reply["citations"] * 2,
        ):
            with self.subTest(citations=citations), self.assertRaises(guide.AskError):
                reply = {**self.reply, "citations": citations}
                guide.verify_result(self.request, self.packet, 0, self.envelope(self.request, reply))

    def test_cli_preview(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "examples/ask_repo.py"),
                "--show-packet",
                "--repo",
                str(self.repo),
                "--file",
                "README.md",
                "Question?",
            ],
            capture_output=True,
            check=True,
        )
        self.assertEqual(json.loads(proc.stdout)["lines"][1]["text"], self.quote)


if __name__ == "__main__":
    unittest.main()
