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
  a complete three-phase pipeline: (1) Analysis — detect the stack (language,
  framework, database), map the current architecture, and print a summary;
  (2) Audit — cross the code against the anti-pattern catalog, classify each
  finding by severity (CRITICAL, HIGH, MEDIUM, LOW) with exact file and line,
  generate a structured report, and pause for confirmation; (3) Refactoring —
  restructure the codebase to MVC eliminating the found issues, then validate
  that the application still boots and its endpoints respond. Also trigger when
  the user mentions "God Class", tight coupling, business logic in
  controllers, N+1 queries, hardcoded credentials, deprecated APIs, or any
  violation of separation of concerns.

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

The pipeline has **three sequential phases**:

1. **Analysis** — detect the stack, map the current architecture, print a summary.
2. **Audit** — cross the code against the anti-pattern catalog, generate the
   report, ask for confirmation.
3. **Refactoring** — restructure to MVC, then validate that it works.

The skill is **technology-agnostic**: never assume a stack — derive it from the
project using `references/project-analysis.md`.

---

## Phase 1 — Analysis

**Goal**: detect the stack (language, framework, database), map the current
architecture, and print an analysis summary.

Load `references/project-analysis.md` now — it drives this entire phase.

### 1.1 Stack detection

Using the heuristics in `project-analysis.md`, detect:

- **Language** (from manifests and dominant source extensions)
- **Framework** (from the dependency manifest and the entry point's imports)
- **Database and access layer** (ORM vs raw driver)

### 1.2 Architecture mapping

- Locate the **entry point** (`app.py`, `index.js`, `application.rb`, `main.go`,
  `index.php`).
- Build a **layer inventory**: classify what each source file currently does
  (routing, business logic, data access, presentation, configuration), noting
  files that mix several responsibilities.
- List existing folders that imply layers, where credentials/config live, and
  flag files longer than 200 lines (God Class candidates).

### 1.3 Record the test baseline

If a runner is configured, execute it and save the result to
`audit/baseline-tests.txt` before any changes — this is the reference for
Phase 3 validation.

```bash
# Example: capture test baseline
<test-runner> [options] > audit/baseline-tests.txt 2>&1
```

### 1.4 Print the analysis summary

Print the `ARCHITECTURE ANALYSIS` block defined in `project-analysis.md` to the
terminal. The mixed-responsibility files listed there are the primary targets
for Phase 2.

---

## Phase 2 — Audit

**Goal**: cross the code against the anti-pattern catalog, classify every finding
by severity with exact location, consolidate into a structured report, print and
save it, then **pause and ask for confirmation** before any modification.

Load `references/anti-patterns.md` (catalog with detection signals) and
`references/severity-scale.md` (severity classification) now.

### 2.1 Systematic reading

Traverse the project using `view` on each relevant file. Prioritise:

- Entry point and routing files
- Files longer than 200 lines (God Class candidates)
- Files with direct database access
- Configuration files with potentially exposed credentials

### 2.2 Detection against the catalog

For each file, match against the anti-patterns in `anti-patterns.md` using their
detection signals, and classify with the severity scale:

**CRITICAL** — hardcoded credentials (AP-01); SQL injection via string building
(AP-02); full God Class (AP-03).
**HIGH** — business logic in controllers/views (AP-04); missing Model layer
(AP-05); tight coupling without DI (AP-06); mutable global state (AP-07).
**MEDIUM** — N+1 queries (AP-08); missing input validation (AP-09); deprecated /
outdated API usage (AP-10).
**LOW** — magic numbers/strings (AP-11); meaningless names (AP-12); dead code /
outdated comments (AP-13).

### 2.3 Recording findings

For each finding, record it in the format below before moving to the next file:

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

### 2.4 Audit report

Load `references/report-template.md` and render the report. Print the full report
to the terminal using this exact structure:

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

### 2.5 Save the report to disk

After printing, write the same content to the path defined in
`references/report-template.md` (`../reports/audit-project-<N>.md`, where `<N>`
is the project number set in that template). Create the directory if needed:

```bash
mkdir -p ../reports
```

Wrap the terminal block in a fenced code block inside the Markdown file so the
fixed-width formatting is preserved.

### 2.6 Confirmation checkpoint

**Do not modify any file before this checkpoint is cleared.** Wait for the
user's response to `Proceed with refactoring (Phase 3)? [y/n]`:

- **`y`**: confirm with `Starting Phase 3 — MVC Refactoring.` and continue.
- **`n`**: confirm with `Audit saved. Refactoring cancelled.` and stop.
- Any other input: repeat the prompt once, then stop if still invalid.

---

## Phase 3 — Refactoring & Validation

**Goal**: restructure the codebase to the MVC pattern in the priority order
defined in the report, then validate that the application still works.

Load `references/mvc-patterns.md` (target MVC guidelines per framework) and
`references/refactoring-playbook.md` (before/after transform per anti-pattern).

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
6. **HIGH and MEDIUM**: eliminate coupling, fix N+1 queries, replace deprecated
   APIs, add missing validations.
7. **LOW last**: renaming, constant extraction, dead code removal.

For each issue, apply the matching transform from `refactoring-playbook.md`.

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

### 3.4 Validation with automated tests

If tests are configured, run the runner and compare with the baseline:

```bash
# Run and save result
<test-runner> [options] > audit/post-refactor-tests.txt 2>&1

# Compare with baseline
diff audit/baseline-tests.txt audit/post-refactor-tests.txt
```

Any test that passed in the baseline and fails after refactoring is a
regression — it must be fixed before closing.

### 3.5 Validation without automated tests

If no tests exist, perform a structural check that the application **boots and
its endpoints respond**:

- [ ] The application starts without errors (use the project's standard startup command)
- [ ] Main routes respond with the expected HTTP status
- [ ] No `import`, `require`, or `use` references files that were moved without
  path updates
- [ ] No environment variable or credential was removed without a replacement

### 3.6 Closing checklist

- [ ] All CRITICAL and HIGH findings have been resolved
- [ ] `audit/refactoring-log.md` is complete
- [ ] Post-refactoring validation (tests and/or boot + endpoints) documented

---

## References

| File                              | When to load                                          |
|-----------------------------------|-------------------------------------------------------|
| `references/project-analysis.md`  | Start of Phase 1 — stack detection & architecture map |
| `references/anti-patterns.md`     | Phase 2 — anti-pattern catalog with detection signals |
| `references/severity-scale.md`    | Phase 2 — severity scale and examples                 |
| `references/report-template.md`   | Phase 2 — audit report template                       |
| `references/mvc-patterns.md`      | Phase 3 — target MVC patterns by framework            |
| `references/refactoring-playbook.md` | Phase 3 — before/after transform per anti-pattern  |
