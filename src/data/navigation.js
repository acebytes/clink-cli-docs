export const navigation = [
  {
    label: "Start here",
    pages: [
      { href: "/", title: "Introduction" },
      { href: "/installation/", title: "Installation" },
      { href: "/quick-start/", title: "Quick start" },
      { href: "/examples/", title: "Usage examples" },
    ],
  },
  {
    label: "Command line",
    pages: [
      { href: "/cli/", title: "Commands & flags" },
      { href: "/cli/generation/", title: "Requests & results" },
    ],
  },
  {
    label: "MCP server",
    pages: [
      { href: "/mcp/", title: "Connect a client" },
      { href: "/mcp/tools/", title: "Tool directory" },
      { href: "/mcp/workflows/", title: "Workflows & context" },
      { href: "/mcp/native-tasks/", title: "Native tasks" },
    ],
  },
  {
    label: "Extend Clink",
    pages: [
      { href: "/extensions/ask-repo/", title: "Build ask_repo" },
      { href: "/extensions/", title: "Roles, tools & adapters" },
    ],
  },
  {
    label: "Operate & contribute",
    pages: [
      { href: "/configuration/", title: "Configuration" },
      { href: "/reference/", title: "Compatibility & reference" },
      { href: "/troubleshooting/", title: "Troubleshooting" },
      { href: "/contributing/", title: "Contributing" },
    ],
  },
];
export const upstream = "https://github.com/acebytes/clink-cli";
export const docsRepo = "https://github.com/acebytes/clink-cli-docs";
export const release = "0.2.3";
export const releaseSource = upstream + "/blob/v" + release + "/";
