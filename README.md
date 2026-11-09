# Clink CLI documentation

The public site at [clinkcli.org](https://clinkcli.org) documents the two commands installed by [clink-cli](https://github.com/acebytes/clink-cli). This edition covers [v0.2.3](https://github.com/acebytes/clink-cli/tree/v0.2.3), commit `7b2e257adf0ee9efe3f903044b40e91acf63e392`.

- [CLI usage and programmatic generation](https://clinkcli.org/cli/)
- [MCP setup](https://clinkcli.org/mcp/) and [18 tool guides](https://clinkcli.org/mcp/tools/)
- [Build ask_repo](https://clinkcli.org/extensions/ask-repo/) and [other extension options](https://clinkcli.org/extensions/)

## Develop

Install a Node.js version supported by the pinned Astro and Wrangler packages. Run `npm ci` and `npm run dev`. To check the static output locally:

```sh
npm run build
npm run preview
```

Source pages live under `src/pages`. Shared navigation lives in `src/data/navigation.js`. Each tool’s curated example lives in `src/data/tools.js`. Its advertised arguments come from the checked-in release snapshot. The two Python files in `examples/` are served verbatim as downloads.

## Verify a release update

Use a disposable environment with the exact upstream release under review. Update the release pins and source links together. The exporter reads tool and prompt metadata over stdio. Previewing evidence and running the tests below require no agent login or model call.

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python clink-cli==0.2.3
.venv/bin/python scripts/export_mcp.py
npm run build
.venv/bin/python scripts/check_guides.py
.venv/bin/python -m unittest discover -s tests -v
```

Review changes to the generated snapshot. Recheck operation-specific compatibility against the pinned upstream source. The example tests use a disposable Git checkout and the released generation encoder. Check the native agent’s current availability separately before making a real request.

## Publish

The site is static. `wrangler.jsonc` binds the Cloudflare Worker to `clinkcli.org`. Run `npm run deploy` from an authorized Cloudflare account. Verify the CLI guide, MCP directory, downloadable examples and the missing-page response on the public domain.

## License

Apache License 2.0. Documentation and examples are based on Clink CLI, derived from PAL MCP Server. Copyright 2025 Beehive Innovations. See [LICENSE](LICENSE).
