import snapshot from "../../public/data/mcp-v0.2.3.json";

export const groups = {
  local: "Local tools",
  advisory: "Consultation & search",
  workflow: "Guided investigations",
};

function step(instruction, findings, options = {}) {
  return {
    step: instruction,
    step_number: 1,
    total_steps: 2,
    next_step_required: true,
    findings,
    ...options,
  };
}
const files = ["/absolute/path/to/your-project/src/parser.py"];
const tools = {
  version: {
    group: "local",
    summary: "Check which Clink MCP server answered the call.",
    use: "Call this first after installing or changing an MCP registration. Inspect the returned server version and metadata.",
    example: {},
    next: "Use listmodels to see the configured clients and the operations each one can run.",
  },
  listmodels: {
    group: "local",
    summary:
      "Inspect configured CLIs, roles, roots and operation-specific availability.",
    use: "Call this before selecting an agent. Check the consultation verification status and the separate native-task profile for the selected client.",
    example: {},
    next: "For a script using generation, run clink generation-capabilities --json to inspect that separate profile.",
  },
  challenge: {
    group: "local",
    summary: "Turn an assertion into a prompt for critical examination.",
    use: "Supply the statement you want questioned. Clink returns instructions for your current agent to evaluate it.",
    example: {
      prompt: "Caching all responses will always improve performance.",
    },
    next: "Have the caller examine the assumptions and identify a counterexample.",
  },
  planner: {
    group: "local",
    summary: "Build, revise or branch a plan one step at a time.",
    use: "Send one planning step and estimate the total. Use is_step_revision or is_branch_point with the corresponding step or branch fields to explore alternatives.",
    example: {
      step: "Identify which clients depend on the old response format.",
      step_number: 1,
      total_steps: 3,
      next_step_required: true,
    },
    next: "Return the continuation ID with step 2. Set next_step_required to false when the plan is complete.",
  },
  docgen: {
    group: "local",
    summary:
      "Guide documentation work and track how many files the caller has documented.",
    use: "Specify the documentation style and file counters on each step. The caller inspects and edits the files and reports progress.",
    example: step(
      "Document the parser's accepted inputs.",
      "The parser accepts UTF-8 JSON.",
      {
        document_complexity: false,
        document_flow: true,
        update_existing: true,
        comments_on_complex_logic: false,
        num_files_documented: 0,
        total_files_to_document: 1,
      },
    ),
    next: "Inspect the file, make the documentation edit in your own workspace, then report the updated counts.",
  },
  tracer: {
    group: "local",
    summary: "Trace a call path or map dependencies through a codebase.",
    use: "Name the target and select precision for an execution path or dependencies for structural relationships. The caller reads the code between steps.",
    example: step(
      "Trace the entry point for a missing identifier.",
      "The request first enters the parser.",
      {
        target_description: "The parser's missing-identifier branch",
        trace_mode: "precision",
      },
    ),
    next: "Follow the next call and record the actual path and symbol in the next step.",
  },
  chat: {
    group: "advisory",
    summary:
      "Discuss a question with an advisory agent in an approved working directory.",
    use: "Replace the sample directory with a real, absolute directory inside the chosen client's roots. With the supported Codex profile you may include explicit files and local images.",
    example: {
      prompt: "What are the tradeoffs of retrying this request once?",
      working_directory_absolute_path: "/absolute/path/to/your-project",
      cli_name: "codex",
    },
    next: "For a related question, return the continuation_id from the response.",
  },
  clink: {
    group: "advisory",
    summary: "Ask a CLI for advice or explicitly start a native task.",
    use: "Use consult for advice. For a task that can run tests, edit files or use agent integrations, start with an explicit agent, project, prompt and request key. Each action has its own required fields.",
    example: {
      action: "consult",
      cli_name: "codex",
      prompt: "Suggest a diagnostic for an intermittent cache miss.",
    },
    next: "Use the native tasks guide for start, status, followup and cancel examples.",
  },
  apilookup: {
    group: "advisory",
    summary: "Research an API using the admitted CLI search capability.",
    use: "Ask a focused API question. Clink requires verified search capability and expects structured sources from the selected CLI.",
    example: {
      prompt:
        "Find the official SQLite documentation for the WAL checkpoint operation and cite the source.",
      cli_name: "codex",
    },
    next: "Inspect the returned sources and check that they support the answer before relying on it.",
  },
  consensus: {
    group: "advisory",
    summary:
      "Consult two to eight independent participants and synthesize their answers in the caller.",
    use: "Supply models on step 1. Each participant can select a CLI, role, model and stance. The resolved combination must be unique. Sequential mode consults one participant per caller step. Parallel mode returns outcomes in input order, including individual errors.",
    example: {
      step: "Assess whether to add a cache to a read-heavy endpoint.",
      step_number: 1,
      total_steps: 2,
      next_step_required: true,
      findings: "Reads repeat and staleness matters.",
      execution_mode: "parallel",
      models: [
        { cli_name: "codex", stance: "for" },
        { cli_name: "codex", stance: "against" },
      ],
    },
    next: "Read each participant's result before synthesizing. A change to a declared comparison file can invalidate the comparison.",
  },
  analyze: {
    group: "workflow",
    summary:
      "Investigate structure, performance, security or overall code quality.",
    use: "Choose an analysis type and record observations from your own inspection. Choose actionable output when you need concrete recommendations.",
    example: step(
      "Inspect how requests reuse database connections.",
      "Each handler constructs a new pool.",
      {
        relevant_files: files,
        analysis_type: "performance",
        output_format: "actionable",
      },
    ),
    next: "Measure the behavior and include the evidence in your next step.",
  },
  codereview: {
    group: "workflow",
    summary: "Review a change for correctness, security or performance.",
    use: "Select the review focus and report what you inspected. Collect concrete issues with locations and severity over successive steps.",
    example: step(
      "Review the new input validation.",
      "An empty list currently bypasses one check.",
      { relevant_files: files, review_type: "quick" },
    ),
    next: "Reproduce the issue and add the affected files before completing the review.",
  },
  debug: {
    group: "workflow",
    summary: "Test a diagnosis against observed behavior.",
    use: "Separate your current hypothesis from the findings already observed. Update both as you rule out causes.",
    example: step(
      "Reproduce the failed lookup with an empty cache.",
      "The first lookup fails and the next succeeds.",
      { hypothesis: "The first request races initialization." },
    ),
    next: "Run the discriminating check in your own environment and report its outcome.",
  },
  precommit: {
    group: "workflow",
    summary: "Review staged or unstaged changes before committing.",
    use: "Choose a Git repository and the changes to inspect. The caller reviews the findings and decides what to commit.",
    example: step(
      "Review the staged parser change.",
      "The change adds an early return.",
      {
        total_steps: 3,
        path: "/absolute/path/to/your-project",
        include_staged: true,
        include_unstaged: false,
      },
    ),
    next: "Replace the example path with the intended checkout and verify the proposed fixes before committing.",
  },
  refactor: {
    group: "workflow",
    summary: "Plan a focused refactor while preserving observable behavior.",
    use: "Identify a code smell or choose decomposition, modernization or organization. Record the behavior callers depend on.",
    example: step(
      "Find a boundary between parsing and validation.",
      "Both stages are currently inside one function.",
      { relevant_files: files, refactor_type: "decompose" },
    ),
    next: "Identify regression checks for the proposed boundary before making changes.",
  },
  secaudit: {
    group: "workflow",
    summary: "Audit a security boundary with findings tied to evidence.",
    use: "Select an audit focus such as dependencies, infrastructure, compliance or OWASP. Report the actual inputs, privileges and controls you inspected.",
    example: step(
      "Trace untrusted request fields into the database query.",
      "One filter is assembled from user input.",
      { audit_focus: "owasp" },
    ),
    next: "Document the reproduction and verify the proposed mitigation.",
  },
  testgen: {
    group: "workflow",
    summary: "Design tests for behaviors, edge cases and failure paths.",
    use: "Describe the behavior and list what the existing tests demonstrate. The caller can use the resulting guidance to implement and run tests.",
    example: step(
      "Identify failure cases for parsing a request.",
      "The suite covers valid JSON and empty input.",
      { relevant_files: files },
    ),
    next: "Add the missing cases and report which assertions pass.",
  },
  thinkdeep: {
    group: "workflow",
    summary:
      "Investigate a design decision over several evidence-gathering steps.",
    use: "Describe the decision, record known facts, then investigate the next uncertainty between calls.",
    example: step(
      "Evaluate whether a shared cache is worthwhile.",
      "Requests often repeat within a minute.",
      { problem_context: "Latency-sensitive service with bounded memory." },
    ),
    next: "Bring measurements back on the same continuation and request expert input on completion if needed.",
  },
};

export const directory = snapshot.tools.map((wire) => {
  if (!tools[wire.name]) throw new Error("Missing tool guide for " + wire.name);
  return { ...wire, ...tools[wire.name] };
});
if (Object.keys(tools).length !== directory.length)
  throw new Error("Tool guides differ from the release snapshot");
export const prompts = snapshot.prompts;
