import helper from "../../../examples/ask_repo.py?raw";
import server from "../../../examples/repo_server.py?raw";

export function getStaticPaths() {
  return [
    { params: { file: "ask_repo.py" }, props: { source: helper } },
    { params: { file: "repo_server.py" }, props: { source: server } },
  ];
}

export function GET({ props }) {
  return new Response(props.source, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}
