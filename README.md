# My-Skills — A Personal Library of Claude Code Skills

A curated collection of reusable, portable **Skills** for [Claude Code](https://claude.com/claude-code), Anthropic's AI coding assistant. Each skill packages a specific methodology, workflow, or domain expertise into a self-contained folder that anyone can drop into their Claude Code setup and start using immediately.

This repository is my **personal skills library** — a place where I collect skills I've built (or adapted) for tasks I find myself repeating. New skills are added over time as I find patterns worth packaging.

---

## What is a Claude Code Skill?

A Skill is a self-contained folder with a `SKILL.md` file (plus optional supporting files) that teaches Claude how to handle a specific type of task. When you ask Claude something that matches a skill's description, Claude automatically loads the skill and follows its instructions.

Think of skills as **shareable expertise modules** — instead of re-explaining your preferred workflow every time, you write it once as a skill, and Claude knows what to do.

Read more about skills in the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code).

---

## Skills in this library

| Skill | What it does | Status |
|---|---|---|
| [`knowledge-gap-analysis`](./knowledge-gap-analysis/) | End-to-end methodology for turning workforce assessment data (test results, competency surveys) into a prioritized training plan. Includes a 5-phase framework, a priority scoring formula, three-tier reporting hierarchy, and standalone Python scripts. | ✅ Stable |
| [`poalim-presentation`](./poalim-presentation/) | Builds single-file HTML presentation decks in the Bank Hapoalim L&D visual language: Hebrew RTL, neon-red on dark, Heebo font, animated CSS/JS — no build step, no framework. Given a topic or brief, Claude interviews you, proposes a slide outline, implements the full deck, and generates a speaker-notes companion with thumbnails. Includes the full design system (tokens, layouts, component catalogue, animation rules) and hard-won rules about RTL alignment, headings, icons, and orphan prevention. | ✅ Stable |

*More skills will be added over time. Check back periodically.*

---

## How to use a skill from this repo

### Option 1 — Install one specific skill (recommended)

Pick the skill you want, copy just that folder:

```bash
# Clone the repo (or download as ZIP)
git clone https://github.com/booya1986/My-Skills.git

# Copy a single skill into your Claude Code skills directory
cp -r My-Skills/knowledge-gap-analysis ~/.claude/skills/
```

Restart Claude Code. The skill will activate automatically the next time you ask Claude something that matches its description.

### Option 2 — Install at project scope

If you want a skill available only inside one specific project:

```bash
cp -r My-Skills/knowledge-gap-analysis your-project/.claude/skills/
```

### Option 3 — Use the methodology without Claude Code

Every skill in this library is designed to also be useful as **standalone documentation**. Open the folder, read the `SKILL.md` (and any `references/` files), and follow the methodology manually. The included scripts (where present) are usable on their own.

---

## Repo structure

```
My-Skills/
├── README.md                         You are here
├── CONTRIBUTING.md                   Guidelines for adding new skills
├── LICENSE                           MIT
└── <skill-name>/                     One folder per skill
    ├── SKILL.md                      Required — the main playbook
    ├── README.md                     Optional — user-facing intro
    ├── references/                   Optional — deep-dive docs
    ├── scripts/                      Optional — executable helpers
    └── assets/                       Optional — templates, prompts, etc.
```

Each skill folder is **self-contained**. You can install one skill without pulling in any others.

---

## Design principles

Every skill in this library follows these rules:

1. **Portable.** No dependencies on private codebases, organizations, or systems. Anyone can install and use them anywhere.
2. **No sensitive data.** No real employee data, no proprietary content, no internal terminology. Generic examples only.
3. **Methodology over implementation.** Skills teach the *how* and *why*, not just the *what*. Even if the bundled code doesn't fit your stack, the methodology still applies.
4. **Language-agnostic where possible.** Most skills work for content in any language, even if the documentation is in English.
5. **Progressive disclosure.** The main `SKILL.md` is short; deeper material lives in `references/` and is loaded only when needed.

---

## Contributing

This is a personal library, but suggestions and improvements are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for:

- How to suggest improvements to existing skills
- How skill folders are structured
- Privacy and content rules (no organization-specific information)
- Testing checklist before merging

---

## License

[MIT License](./LICENSE) — use it, adapt it, share it. No warranty.

---

## About

Maintained as a personal collection of L&D, analytics, and workflow skills built through real-world projects. Each skill went through real use before being packaged here.

If a skill saved you time or helped your team, that's the goal. If you adapted it for your context, even better.
