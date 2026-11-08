# Clink CLI documentation

Source for the public documentation site at https://clinkcli.org. The upstream [Clink CLI project](https://github.com/acebytes/clink-cli) owns the Python distribution, programmatic generation contract and MCP server. Commands and compatibility on this site were checked against upstream commit `7b2e257adf0ee9efe3f903044b40e91acf63e392`, release 0.2.3.

## Develop the site

Use a Node.js version supported by the pinned Astro and Wrangler packages. Install dependencies and start the local development server:

```sh
npm ci
npm run dev
```

Build all documentation pages with `npm run build`. Inspect the generated site with `npm run preview`. The custom domain is declared in `wrangler.jsonc`. Deploy to the configured Cloudflare Worker with `npm run deploy` from an authorized account.

Edit content in `src/pages`, shared navigation in `src/data/navigation.js` and the accessible copy control in `src/components/Code.astro`. Keep MCP tool arguments distinct from shell commands. Check examples against the corresponding public upstream release before updating the compatibility table.

## License

Distributed under the Apache License 2.0. Documentation and examples are based on Clink CLI, derived from PAL MCP Server. Copyright 2025 Beehive Innovations. See [LICENSE](LICENSE).
