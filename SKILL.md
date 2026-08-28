---
name: dify-workflow-dsl
description: >
  Design, explain, create, modify, review, and debug business-driven Dify Workflow/
  Chatflow DSL YAML files that can be imported into Dify. Use for workflow discovery,
  business-rule mapping, visual node diagrams, Dify app DSL, workflow YAML, advanced-chat
  YAML, graph nodes/edges, variables, tool nodes, plugin dependencies, database read/write
  tools, and import/export compatibility questions.
---

# Dify Workflow DSL

Use this skill to produce import-ready Dify DSL YAML. Dify calls the exported
workflow file a DSL; it is a YAML app definition with app metadata, dependencies,
workflow variables/features, and a ReactFlow-like graph of nodes and edges.

## Start With the Business

Before editing a nontrivial workflow, define the application brief. Read
`references/business-workflow-design.md` for file-driven, compliance-sensitive,
multi-template, or human-review workflows. Determine the user action, deliverable,
business owner for rules/templates, human-review boundary, evidence fields, exceptions,
and acceptance cases.

For a first conversation, do not lead with a long questionnaire or a dense table. Start
with 3-5 selectable business-goal options, one compact visual flow, and only the 1-3
decisions that materially change the design. Let the selected option update the proposed
scope, answer/output boundary, review path, and next question. Expand to a detailed
application brief only after the user has chosen a direction.

Make that discovery surface visually scannable: use a restrained theme-aware accent color
per option, a title plus one short supporting line, clear selected/focus state, and a
compact summary that changes with the choice. Use an 8px spacing/radius rhythm, avoid
large blocks of gray text, and stack options on narrow screens. Do not use decorative
graphics or color without a stable meaning.

Use deterministic code/configuration for mappings, code values, template schema/order,
grouping, filenames, calculations, masking, and compliance gates. Use knowledge retrieval
as evidence for maintained business documents. Use an LLM only for a defined unresolved
set and validate it against an allowlist/structured schema. Preserve valid human input;
do not silently replace or discard it because another field disagrees.

For complex workflows, show the user a compact business-stage diagram before implementation
and an updated node diagram after changes. Use Mermaid when it materially clarifies more
than a few branches or stages; do not add a diagram merely as decoration. For an existing
DSL, generate the node diagram with `scripts/render_workflow_mermaid.py`.

## Core Workflow

1. Review the application brief and convert approved business rules into a single owned
   configuration source. Do not duplicate mutable rules across prompts, code nodes, and
   knowledge bases without a synchronization plan.
2. Clarify only remaining import-blocking requirements: app mode (`workflow` or
   `advanced-chat`), required inputs, model/provider, installed plugins, knowledge bases,
   secrets, and expected outputs.
3. Choose the DSL version. For new DSL, target official Dify app DSL
   `version: "0.6.0"` unless the user explicitly asks for old-version
   compatibility. Always write `version` as a YAML string.
4. Sketch the graph by business responsibility: receive, extract/normalize, schema gate,
   deterministic rules, retrieval, constrained LLM fallback, render, output guard, and
   review/download. Consolidate nodes only when they share ownership and failure behavior.
5. Use stable string node IDs and connect every edge with matching `sourceType`,
   `targetType`, `sourceHandle`, and `targetHandle`.
6. Add `dependencies` for every plugin-backed LLM provider, tool, agent, knowledge
   feature, and model config. Support marketplace, package, and GitHub dependency
   entries; use exact exported plugin identifiers when available.
7. For any plugin/tool not covered by existing examples, follow
   `references/plugin-marketplace-tools.md`: prefer a minimal exported DSL from
   the user's Dify workspace, then plugin source/package metadata, then marketplace
   pages. Be explicit about reliability when exact tool schemas are unavailable.
8. Validate locally, run representative business regression cases, then execute the target
   Dify app/API when available. Treat missing records, blank mandatory fields, unexpected
   headers, or timeouts as failures to diagnose, not as cosmetic output issues.
   When the user supplies a specifically named import/export copy, validate that exact
   path after every edit (not a sibling "master" DSL), record its checksum, and inspect
   every dynamic tool parameter again. A Dify re-export or manual UI edit can silently
   turn a `type: variable` selector back into a `type: mixed` template literal.
9. Close the loop with real exported business data before declaring a fix complete.
   Synthetic fixtures are supplemental, not sufficient: compare the source-row count,
   normalized-row count, sendable count, review/blocked count, selected route, and
   rendered template fields against the live Dify API result.

## Reference Map

Load only the relevant reference files:

- `references/official-0.6-target.md` for official current-version rules from
  Dify source: DSL version, import/export behavior, dependency types, current node
  enum, trigger/datasource cautions, and public sample availability.
- `references/dsl-structure.md` for top-level YAML, variables, dependencies,
  edges, handles, and import/export rules.
- `references/node-schemas.md` for node-specific schemas and examples.
- `references/database-tools.md` for PostgreSQL/SQL read-write tool nodes,
  including `spance/db_client_node` and `hjlarry/database` patterns from the
  user's exported DSLs.
- `references/plugin-marketplace-tools.md` for defining new plugin tool nodes from
  Dify Marketplace, GitHub plugin repos, `.difypkg` packages, or minimal exports.
- `references/real-world-yml-study.md` for observations from 172 parsed public
  Dify app DSL files and 39 detailed representative legacy samples. These samples
  are real-world compatibility evidence, not the target version authority.
- `references/complete-examples.md` for full importable examples and graph layouts.
- `references/business-workflow-design.md` for application briefs, decision boundaries,
  rule ownership, output guards, LLM fallback constraints, visual explanations, and
  business/API regression checks.

## Required Decisions

- **Mode**: use `workflow` for one-shot runs with `end`; use `advanced-chat` for
  Chatflow, `sys.query`, `sys.files`, memory, and `answer` nodes.
- **Inputs**: in `workflow`, define start `variables`; in `advanced-chat`, keep
  start variables empty unless the app needs explicit form inputs.
- **Secrets**: do not hardcode real API keys, DB passwords, or webhook secrets.
  Prefer Dify plugin authorization, `env` variables, or clear placeholders.
- **Database access**: prefer parameterized tool calls (`$arg0`, `$arg1`, ...)
  over interpolated SQL. For LLM-generated SQL, restrict to SELECT unless the
  user explicitly asks for writes and accepts the risk.
- **Model/provider**: keep provider names exactly as Dify exports them, for example
  `langgenius/tongyi/tongyi`, `openai`, or a marketplace provider path.
- **New plugin tools**: do not promise import-and-run reliability from a tool name
  alone. Ask for a minimal exported DSL or plugin source/package when exact
  `provider_id`, `tool_name`, parameters, and authorization schema are unknown.
- **Rule ownership**: keep changeable business mappings, aliases, template fields, and
  standard phrases in an owned configuration source. A knowledge base may support retrieval
  but must not be the only copy of an exact code/value mapping.
- **Review boundary**: define whether unresolved, malformed, low-confidence, or
  contradictory records are blocked, held for review, or explicitly delegated. Retain their
  original fields and rationale in output; do not silently omit records.

## Authoring Rules

- For newly generated DSL, use `version: "0.6.0"` and top-level `kind: app`.
- `workflow.graph.nodes` and `workflow.graph.edges` must both exist.
- Node wrapper `type` is normally `custom`; `data.type` is the real node kind.
- Every node `id` should be a string. Do not reuse IDs.
- Edges must reference existing node IDs.
- Branch edges from `if-else` use source handles from case IDs, commonly `"true"`,
  `"false"`, or a UUID custom case ID.
- Question classifier source handles use class IDs such as `"1"`, `"2"`.
- Iteration/loop internals need `isInIteration`/`isInLoop`, parent IDs, and start
  helper nodes when exported by Dify.
- `value_selector` and `variable_selector` are arrays, for example
  `["node_id", "text"]`; prompt interpolation is `{{#node_id.field#}}`.
- When an LLM follows an `if-else` branch, do not interpolate values directly
  from nodes before that branch. Put a Code or Template payload node immediately
  after the selected branch, expose the exact LLM fields there, and reference only
  that direct predecessor in the prompt. Some Dify 1.15 builds otherwise leave
  cross-branch selectors unexpanded at runtime.
- Code nodes must explicitly declare `code_language` (`python3` for Python in
  Dify 1.15) and define the runtime entrypoint: Python uses `def main(...)`,
  JavaScript/TypeScript uses `function main(...)` or an equivalent `main`
  function. Return keys must match `outputs`.
- For `workflow` terminal `end` nodes, every `outputs[].variable` name must be
  globally unique across every end branch. Prefix branch-specific terminal fields
  (for example, `success_report`, `input_review_report`, `output_review_report`)
  instead of reusing generic names such as `report`, `metrics`, or `validation`.
- Tool nodes must include `provider_id`, `provider_name`, `provider_type`,
  `tool_name`, `tool_label`, and `tool_parameters`. `plugin_id`,
  `plugin_unique_identifier`, and `tool_node_version` are common but not universal;
  preserve them when copied from an export.
- In Dify 1.15, a tool parameter that is a direct upstream value must use
  `type: variable` with an array selector such as `value: ["node_id", "field"]`.
  Do not put `{{#node_id.field#}}` inside a `type: mixed` tool value: it can be
  passed to the plugin literally. For dynamic text that combines values and
  constants, render it first in a Template Transform or Code node, then bind the
  resulting field with `type: variable`.
- `provider_type` may be `builtin`, `api`, `workflow`, or `mcp`.
- Dependencies may use `type: marketplace` with `marketplace_plugin_unique_identifier`,
  `type: package` with `plugin_unique_identifier`, or `type: github` with
  `github_plugin_unique_identifier` plus repo/package metadata.
- `custom-note` nodes are valid canvas annotations and may have empty `data.type`.
- `agent-chat`, `chat`, and `completion` apps may be top-level `model_config`
  apps with no `workflow.graph`; do not force graph rules onto them when reviewing
  legacy exports.
- For public examples, replace tenant-specific icon URLs and credentials with
  placeholders unless they are harmless exported metadata.
- Normalize real-world multi-value separators before grouping, use stable merge keys, and
  apply output headers/field order from the selected destination template only.
- Treat uploaded spreadsheet headers as an external schema. Build and test an explicit
  alias map (for example, `网贷平台`/`对接平台`, `行内业务类别`/`投诉分类`) before any
  grouping or classification. Preserve original field values alongside normalized values
  so a missing alias cannot silently become an empty route.
- Apply row-level precedence before group-level aggregation. A group summary must not
  reuse the first row's category, platform, or review state for later rows. Test at least
  one group containing the same platform with different row classifications and verify
  each row's selected rule and template fields independently.
- Include real-data boundary fixtures: generic complaint wording with a populated human
  category, blank category requiring fallback, mixed separators (Chinese comma, ASCII
  comma, `、`), WPS/Excel-exported dates, blank/merged cells, and platform aliases. Verify
  that valid human classification is used before complaint-text LLM inference and that
  only unresolved rows reach the LLM.
- Add a record-conservation guard for file/row workflows: input records equal sendable
  records plus review/blocked records. Show blocked records in their uploaded shape.
- Keep LLM output structured and allowlisted. Reject empty, illegal, or low-confidence
  values to a visible review queue rather than converting them into a plausible default.
- Do not run LLM nodes whose output is ignored. Restrict fallback calls to unresolved cases,
  then measure real execution latency before retaining a costly node.
- Do not place chart/export tool execution exclusively behind an LLM formatting/style gate.
  Gate tools on deterministic input validity and authorization; when the LLM misses a
  writing format, compile a clearly marked deterministic, data-backed fallback report
  so the requested charts and document exports still run. Reserve a blocking review path
  for invalid source data, unsafe output, or absent required tool input.

## Validation Checklist

Before finalizing a DSL:

- YAML parses cleanly.
- `version` is a string and `app.mode` matches terminal node type.
- Dependencies cover all plugin-backed nodes.
- All graph edges resolve to existing nodes and matching data types.
- Start variables, conversation variables, and environment variables have unique
  names. Include selectors for new variables; tolerate missing conversation
  selectors when reviewing older exports.
- Every terminal `end` node output has a non-empty `outputs[].variable`, and no
  two terminal branches reuse the same output variable name. This check is
  required before import because Dify rejects duplicate terminal output names.
- Every LLM has a model and prompt template.
- For an LLM after a conditional branch, prompt selectors are supplied by a direct
  post-branch payload node; run the published app once and inspect the rendered
  result for literal `{{#...#}}` selectors.
- Every Code node has a non-empty `code_language`, an entrypoint, and declared
  return keys that match `outputs`; do not rely on an importer default.
- Every tool has required provider/tool fields and parameter values.
- Every dynamic tool parameter uses `type: variable` with a two-part selector;
  no tool parameter contains an unresolved `{{#...#}}` template literal in a
  `type: mixed` value.
- When a user will import a named DSL copy, run the validator on that exact final path
  immediately before handoff, retain a checksum, and report that path explicitly. Do
  not infer that an adjacent or earlier master file has the same tool-selector state.
- New or rare plugin tools are backed by an exported node, plugin package/source,
  or clearly labeled as a best-effort draft that still needs Dify import testing.
- SQL has no trailing comma before `)` and uses bound parameters for dynamic values.
- For input/output workflows, field mapping, template header/order, required/optional
  status, grouping key, review flag, decision source, and original evidence are explicit.
- Record conservation holds; unknown/missing/ambiguous rows are visible and retain their
  source shape instead of disappearing from the result.
- Standard code mappings and compliance phrases are deterministic; LLM outputs are
  constrained, validated, and used only inside their approved fallback boundary.
- Output guards remove model reasoning markup such as `<think>...</think>` and
  reject unresolved workflow selectors such as `{{#node.field#}}`; a report must
  not pass solely because a separately appended data table contains numbers.
- Regression cases cover valid human input, contradictory evidence, multi-value input,
  missing template, unresolved route/classification, review-required output, and sensitive
  data handling when applicable.
- At least one regression case must come from an actual user-exported workbook (or a
  byte-for-byte representative fixture) and must be executed through the target Dify API,
  not only through a local code-node harness. Record the run ID and compare every source
  row with its output/review counterpart.
- For grouped workflows, assert row-level invariants after grouping: no first-row value
  contamination, no dropped later rows, and no template fields filled from a different
  row. For each failed regression, capture the input shape, the node that first diverged,
  and the missing test dimension before adding or changing a rule.
- For a changed, deployed workflow, real Dify execution/API output has been checked for
  content, format, count, review visibility, and node latency. Keep a rollback DSL.
- For workflows with charts or document exports, confirm from a published run that every
  requested tool node actually executed; end-node output presence alone is insufficient,
  because an upstream LLM/format branch can silently skip every tool.
- The final answer tells the user which file was written and whether validation
  passed.

## Useful Commands

```bash
python3 scripts/validate_dsl.py path/to/workflow.yml
python3 scripts/validate_dsl.py examples/*.yml
python3 scripts/render_workflow_mermaid.py path/to/workflow.yml --output workflow.mmd
```

If the user only asks for a review, report import risks and behavioral bugs first,
with file/line references when possible. If the user asks to create or modify a
workflow, write or patch the YAML directly and validate it.
