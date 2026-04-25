# Contributing to My-Skills

Guidelines for adding, improving, or adapting skills in this library.

This is a personal skills library, but the rules below apply to anything that lives here — including future skills I add myself.

---

## What belongs in this library

A skill belongs here if it:

- Encodes a **reusable methodology**, not a one-off task
- Works for **any organization** (no proprietary terms or systems)
- Is **self-contained** (no external dependencies on private repos)
- Has been **tested in at least one real project** (not just theoretical)

A skill does **not** belong here if it:

- Contains real employee data, customer data, or any PII
- References specific companies, brands, or proprietary systems
- Only works inside one specific codebase
- Duplicates an existing skill without adding value

---

## Folder structure for a new skill

Every skill is a folder at the root of this repo. Use `kebab-case` for the folder name.

```
my-new-skill/
├── SKILL.md                # required
├── README.md               # recommended — user-facing intro
├── references/             # optional — deep-dive docs
│   ├── topic-a.md
│   └── topic-b.md
├── scripts/                # optional — executable helpers
│   └── do_thing.py
└── assets/                 # optional — templates, prompts, sample data
    └── template.md
```

### `SKILL.md` requirements

Must start with YAML frontmatter:

```yaml
---
name: my-new-skill
description: One paragraph that explains both what the skill does AND when Claude should invoke it. Include trigger phrases the user might say. Be specific.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
---
```

The `description` field is the single most important part — it determines whether Claude actually loads the skill at the right moment. Bad descriptions = the skill never triggers.

After the frontmatter, the body should:

- Be under 500 lines (use `references/` for deeper material)
- Explain *when* to use the skill (concrete triggers)
- Explain *why* the methodology works (not just what to do)
- Point to bundled resources clearly

### `README.md` (recommended)

A user-facing introduction that explains:

- What the skill does in 1–2 sentences
- Who it's for
- How to install it (3 options: global Claude Code, project-scoped, standalone)
- A 5-minute quick-start
- Where to read more

---

## Privacy and content rules

These are non-negotiable. Every skill must pass these checks before being added.

### Forbidden content

- Real employee names, IDs, or any PII
- Real customer data or transaction records
- Real test results, scores, or response data
- Names of specific organizations, brands, products, or systems used in any private project
- Internal file paths from private repos (e.g., `/Users/<name>/...`)
- Internal URLs (e.g., specific intranet domains)
- Project-specific numerical fingerprints (employee counts, branch counts, etc., that could identify the source organization)

### Allowed content

- Example data with obviously fictional values (`E001`, `Q01`, `Sales`, `Operations`)
- Generic example numbers used to illustrate formulas or thresholds
- Generic role names and team labels (`Team-A`, `Region North`, `Manager`)
- Industry-neutral examples that span multiple sectors

### Pre-merge security check

Before adding or updating a skill, run a privacy scan with `grep -rn` against patterns covering the categories below. All scans must return zero results. If any returns a hit, fix it before committing.

| # | Category | What to scan for |
|---|---|---|
| 1 | Non-English scripts that point to a specific region | Any character ranges from local alphabets used in your private projects |
| 2 | Specific organization names | Brand names, product names, internal system names from any private project |
| 3 | Personal names | First/last names of real people you've worked with |
| 4 | Geographic identifiers | Country, city, region names tied to specific deployments |
| 5 | Internal paths | Local user directories, internal repo paths, internal hostnames |
| 6 | Numerical fingerprints | Population sizes, transaction counts that could identify the source |
| 7 | Email addresses or contact info | Any `@domain` strings |
| 8 | Domain-specific jargon | Industry terminology that signals where the skill came from |

Build your own grep patterns based on what your private project contains. The point is mechanical verification — eyeballing isn't enough.

---

## Versioning

Skills evolve. Track meaningful changes in the skill's own folder using either:

- A `CHANGELOG.md` inside the skill folder (preferred for major changes)
- Clear commit messages on the repo (sufficient for minor tweaks)

If you make a breaking change to a skill (e.g., changing the schema a script expects), bump a version note in the skill's `SKILL.md` so existing users know.

---

## Testing checklist

Before adding a skill to the library:

- [ ] All required files present (`SKILL.md`, optionally `README.md`, `references/`, `scripts/`, `assets/`)
- [ ] `SKILL.md` frontmatter is valid YAML
- [ ] `description` field tells Claude clearly when to use the skill
- [ ] `SKILL.md` body is under 500 lines
- [ ] All scripts run without error on a sample input
- [ ] All five privacy scans return zero results
- [ ] Examples in the docs use generic, fictional data only
- [ ] The skill works without any other skill in this library being installed (self-contained)

---

## Suggesting improvements

Open an issue or pull request with:

- The skill you're commenting on
- What you'd change and why
- (For PRs) the actual changes, plus confirmation that the privacy scans pass

---

## License

Contributions are accepted under the same MIT license as the rest of the repo. By contributing, you agree your contribution may be used and adapted by anyone.
