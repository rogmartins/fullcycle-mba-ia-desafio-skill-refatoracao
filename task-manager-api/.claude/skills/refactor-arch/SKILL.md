---
name: refactor-arch

description: >
  Analyzes and refactors a codebase architecture to the MVC pattern
  (Model-View-Controller). Use this skill whenever the user runs the
  /refactor-arch command, requests a code architecture audit, asks to
  identify anti-patterns or code smells with exact location (file and line),
  wants a structured report of architectural issues, needs to refactor a
  project for separation of concerns (MVC, SOLID), or requests validation
  that the application keeps working after structural changes. The skill runs
  a complete four-phase pipeline: (1) codebase scan classifying issues by
  severity — CRITICAL, HIGH, MEDIUM, or LOW — with exact file and line; (2)
  generation of a structured audit report with all findings; (3) guided
  refactoring to MVC, eliminating the found issues; (4) post-refactoring
  validation ensuring the application continues to work. Also trigger when
  the user mentions "God Class", tight coupling, business logic in
  controllers, N+1 queries, hardcoded credentials, or any violation of
  separation of concerns.

slash_command: /refactor-arch

compatibility:
  tools:
    - bash
    - view
    - str_replace
    - create_file
  notes: >
    Requires read access to the full project codebase. For projects with
    automated tests, the test runner command must be accessible via bash
    for the validation phase.
---

# Refactor Arch

Runs a complete architectural audit and refactoring pipeline on a codebase
targeting the MVC pattern, eliminating anti-patterns and code smells with
severity classification and result validation.

---

## Preconditions

Before starting the pipeline, verify:

1. **Map the project**: use `view` on the root directory to understand the folder
   structure and identify the main language and framework.
2. **Identify the entry point**: locate the main application file
   (e.g. `app.py`, `index.php`, `application.rb`, `main.go`).
3. **Load the severity scale**: read `references/severity-scale.md` now —
   it is required throughout Phase 1 and Phase 2.
4. **Record the current test state**: if a runner is configured, execute it and
   save the result to `audit/baseline-tests.txt` before any changes.

```bash
# Example: capture test baseline
<test-runner> [options] > audit/baseline-tests.txt 2>&1
```

---

## Phase 1 — Codebase Scan

**Goal**: identify all anti-patterns and code smells with exact location,
classifying each finding using the severity scale defined in
`references/severity-scale.md`.

### 1.1 Systematic reading

Traverse the project using `view` on each relevant file. Prioritise:

- Entry point and routing files
- Files longer than 200 lines (God Class candidates)
- Files with direct database access
- Configuration files with potentially exposed credentials

### 1.2 Detection checklist by category

**CRITICAL violations**
- [ ] Hardcoded credentials or tokens (passwords, API keys, connection strings)
- [ ] SQL queries built via string concatenation (SQL Injection)
- [ ] A single file concentrating database, logic, and routing (full God Class)

**HIGH violations**
- [ ] Complex business logic inside controllers or views
- [ ] Complete absence of a Model layer (raw queries scattered across the codebase)
- [ ] Tight coupling without dependency injection
- [ ] Mutable global state shared across components

**MEDIUM violations**
- [ ] N+1 queries (loops with a database call at each iteration)
- [ ] Logic duplication across controllers or files in the same layer
- [ ] Missing input validation on routes
- [ ] Middlewares used for domain logic

**LOW violations**
- [ ] Magic numbers or strings without named constants
- [ ] Meaningless variable, function, or class names
- [ ] Outdated comments or dead code (commented-out blocks)

### 1.3 Recording findings

For each finding, record it immediately in the format below before moving to
the next file:

```
[SEVERITY] path/to/file.ext : line N
Description: what the problem represents
Impact: why it is problematic in this context
```

Group by severity: CRITICAL first, then HIGH, MEDIUM, LOW.

**SQL Injection reporting rule**: for every SQL Injection finding, identify the query
operation type (SELECT, INSERT, UPDATE, DELETE, or dynamic WHERE builder) and state
only the risks enabled by that specific operation — do not generalise. If a technical
security term is used, always define it in plain language in the same sentence.

---

## Phase 2 — Audit Report

**Goal**: consolidate all Phase 1 findings into a structured report, print it
to the terminal in a standardised format, save it to disk, and ask the user
whether to proceed to Phase 3.

### 2.1 Terminal output format

Print the full report to the terminal using this exact structure:

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: {project-name}
Stack:   {language} + {framework}
Files:   {N} analyzed | ~{LOC} lines of code

Summary
CRITICAL: {n} | HIGH: {n} | MEDIUM: {n} | LOW: {n}

Findings

[CRITICAL] {Issue Title}
File: {path/to/file.ext}:{line}
Description: {what the problem represents}
Impact:      {why it is problematic in this context}
Recommendation: {concrete action to fix it}

[HIGH] {Issue Title}
File: {path/to/file.ext}:{line}
Description: {what the problem represents}
Impact:      {why it is problematic in this context}
Recommendation: {concrete action to fix it}

... (repeat for all findings, grouped CRITICAL → HIGH → MEDIUM → LOW)

================================
Total: {N} findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Rules for the terminal output:
- Always group findings by severity: CRITICAL first, then HIGH, MEDIUM, LOW.
- Within the same severity group, order by file name alphabetically.
- Multi-line `Description`, `Impact`, and `Recommendation` values must be
  indented to align with the first character after the label (see example above).
- The separator line is exactly 32 `=` characters.
- **Language**: write the *content* of `Description`, `Impact`, and
  `Recommendation` fields in **Brazilian Portuguese**. All labels, headers,
  severity tags, file paths, and any other fields must remain in English.

### 2.2 Save the report to disk

After printing, write the same content to:

```
../reports/audit-project-3.md
```

Create the `reports/` directory if it does not exist:

```bash
mkdir -p ../reports
```

Wrap the terminal block in a fenced code block inside the Markdown file so the
fixed-width formatting is preserved.

### 2.3 Proceed to Phase 3

Wait for the user's response to `Proceed with refactoring (Phase 3)? [y/n]`:

- **`y`**: confirm with `Starting Phase 3 — MVC Refactoring.` and continue.
- **`n`**: confirm with `Audit saved to ../reports/audit-project-3.md. Refactoring cancelled.` and stop.
- Any other input: repeat the prompt once, then stop if still invalid.

---

## Phase 3 — MVC Refactoring

**Goal**: restructure the codebase to the MVC pattern, eliminating the
identified issues in the priority order defined in the report.

Load `references/mvc-patterns.md` to consult patterns and examples specific
to the framework identified in the preconditions.

### 3.1 Execution order

Always follow this sequence to minimise regression risk:

1. **CRITICAL first**: fix exposed credentials and God Classes before any
   structural refactoring. These issues can invalidate the entire codebase.
2. **MVC directory structure**: create the new architecture folders before
   moving code (`models/`, `views/`, `controllers/`).
3. **Model extraction**: move all data access logic and business rules to the
   Model layer.
4. **Controller clean-up**: controllers should only orchestrate — receive the
   request, call the Model, return the response.
5. **View isolation**: remove presentation logic mixed with business logic.
6. **HIGH and MEDIUM**: eliminate coupling, fix N+1 queries, add missing
   validations.
7. **LOW last**: renaming, constant extraction, dead code removal.

### 3.2 Rules during refactoring

- Make one change at a time. Never move multiple responsibilities in a single
  step without intermediate validation.
- Preserve the public interface of components (routes, API contracts) to avoid
  breaking existing integrations.
- Add a `REFACTORED: [reason]` inline comment (using the language's comment
  syntax) on changed lines for traceability.

### 3.3 Change log

Maintain a log of changes in `audit/refactoring-log.md`:

```
## [SEVERITY] Issue name
- Original file: path/original.ext : line N
- Target file:   path/new.ext
- Action: [moved | extracted | renamed | removed | fixed]
- Reason: brief description
```

---

## Phase 4 — Validation

**Goal**: ensure the application continues to work correctly after all changes
made in Phase 3.

### 4.1 Validation with automated tests

If tests are configured, run the runner and compare with the baseline:

```bash
# Run and save result
<test-runner> [options] > audit/post-refactor-tests.txt 2>&1

# Compare with baseline
diff audit/baseline-tests.txt audit/post-refactor-tests.txt
```

Any test that passed in the baseline and fails after refactoring is a
regression — it must be fixed before closing.

### 4.2 Validation without automated tests

If no tests exist, perform a structural check:

- [ ] The application starts without errors (use the project's standard startup command)
- [ ] Main routes respond with the expected HTTP status
- [ ] No `import`, `require`, or `use` references files that were moved without
  path updates
- [ ] No environment variable or credential was removed without a replacement

### 4.3 Closing checklist

- [ ] All CRITICAL and HIGH findings have been resolved
- [ ] `audit/refactoring-log.md` is complete
- [ ] `audit/architecture-report.md` updated with final status
- [ ] Post-refactoring test results documented

---

## References

| File                             | When to load                                          |
|----------------------------------|-------------------------------------------------------|
| `references/severity-scale.md`   | Start of Phase 1 — severity scale and examples        |
| `references/report-template.md`  | Start of Phase 2 — audit report template              |
| `references/mvc-patterns.md`     | Start of Phase 3 — MVC patterns by framework          |
