# Audit Report Template

Used at the start of Phase 2 to render and save the audit report.

---

## Terminal Output Format

Print this block verbatim to the terminal (replace all `{placeholders}`):

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

... (repeat for MEDIUM, then LOW)

================================
Total: {N} findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Formatting Rules

1. **Separator**: exactly 32 `=` characters.
2. **Grouping**: CRITICAL → HIGH → MEDIUM → LOW. Never mix groups.
3. **Within group**: order findings alphabetically by file path.
4. **Label alignment**: `Description`, `Impact`, and `Recommendation` values that span multiple lines must be indented to align with the first character after the label colon.
5. **Blank lines**: one blank line between consecutive findings. No blank line between label and value within a finding.
6. **Language**: write the *content* of `Description`, `Impact`, and `Recommendation` fields in **Brazilian Portuguese**. All labels (`Description:`, `Impact:`, `Recommendation:`), headers, severity tags, file paths, and any other fields must remain in English.

---

## Disk Output

After printing to the terminal, write the same content to:

```
../reports/audit-project-1.md
```

Wrap the terminal block inside a fenced Markdown code block so fixed-width formatting is preserved:

````markdown
```
================================
ARCHITECTURE AUDIT REPORT
...
================================
```
````

Create the directory if needed:

```bash
mkdir -p ../reports
```

---

## Metadata Block (optional, append after the fenced block)

```markdown
---
**Generated**: {YYYY-MM-DD HH:MM}
**Analyzer**: refactor-arch skill
**Project number**: {project-number}
```

---

## Phase 2 Checkpoint

After saving, wait for user input:

| Input | Action |
|-------|--------|
| `y`   | Print `Starting Phase 3 — MVC Refactoring.` and continue |
| `n`   | Print `Audit saved to ../reports/audit-project-1.md. Refactoring cancelled.` and stop |
| other | Repeat prompt once, then stop |
