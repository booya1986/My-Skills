# Changelog

## 2026-09-29 · Decision angles, debunked statistics, scoring script, publish step
- **Decision-shaped questions** ("should I take/build/buy X") now get framing questions
  first (purpose, scope, output, employer link) and a default set of nine decision
  angles: readings of the mandate, stakeholder win/lose map, the end user's view,
  alternatives to doing it at all, cost and promises, personal fit, a pre-mortem, an
  interview guide, and a measurement framework. For these questions a targeted round
  two is the default. See `references/decision-questions.md`.
- **A working Reddit route:** when a Firecrawl MCP is available, its search with
  `site:reddit.com/r/<sub>` returns thread titles, counts and highlights. The
  orchestrator runs this pass itself, because subagents often lack MCP tools and report
  Reddit as empty. Closed communities are recorded as a finding, not retried.
- **Debunked-statistics list** (`references/debunked-statistics.md`): famous numbers
  that fail fact-checking, with what to say instead. Verify reads it first; consolidate
  appends to it.
- **Scores come from a script** (`scripts/score.py`), not from an agent's arithmetic.
- **Numbers discipline:** every statistic carries who/when/sample, or is marked
  `UNTRACED`; verify tags findings VERIFIED / SINGLE-SOURCE / UNTRACED / REFUTED / STALE.
- **Right-to-left rendering rules:** top-down flows or tables, no LR diagrams or ASCII
  charts, arrows in reading direction, bidi isolation for Latin runs.
- **Native-voice writing guide** (`references/writing-voice.md`): answer first, one
  everyday picture per hard idea, short spoken paragraphs, numbers in context, no
  calques or report-speak, read-aloud test.
- **Inline source links:** every source named in the text is linked at that spot, not
  only in the sources list.
- **Richer note structure:** jargon key, limits section, do-not-cite table with
  replacements, ratios explained with worked examples.
- **Optional publish step** (`references/publish.md` + `assets/publish-kit/`): a
  designed HTML report for LTR or RTL languages with interactive components and
  infographics, on GitHub Pages, with a `DESIGN.md` contract and real-browser
  verification. Offered in one line; built only when asked.
- **Evals** (`evals/evals.json`): four scenarios covering topic, decision-shaped,
  date-sensitive and publish runs.
