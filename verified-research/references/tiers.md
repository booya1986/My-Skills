# Tiers, venue map, and the tier-balance rule

This file is the **single source of truth** for source tiers and the balance rule.

## The four tiers

| Tier | Weight (score) | Examples |
|------|----------------|----------|
| `authoritative` | 40 | Vendor primary docs, standards bodies, regulators, official changelogs, annual reports, top analyst firms (Gartner, McKinsey, Deloitte, BCG), HBR, WEF |
| `academic` | 40 | Peer-reviewed / arXiv / NBER papers, university research labs |
| `practitioner` | 20 | Named expert blogs, reputable eng/trade press, conference talks |
| `community` | 10 | Reddit, X/Twitter threads, Hacker News, GitHub discussions |

Formal = `authoritative` + `academic`. Community = `community` (practitioner sits in
between and does not satisfy the community requirement on its own).

## The venue map

Canonical file: `VENUE_MAP` (see SKILL.md Setup; default `<NOTES_DIR>/_meta/research-venues.json`).

Shape:
```json
{
  "version": "1.x",
  "updated": "YYYY-MM-DD",
  "recency_default_days": 540,
  "domains": {
    "<domain_key>": { "authoritative": ["host…"], "community": ["host…"] }
  }
}
```

**Read + append protocol (discover step):**
1. Pick the domain(s) the topic falls under; read their `authoritative` + `community` hosts as a starting where-to-look list.
2. Dynamically find additional top venues per the specific topic.
3. When a venue proves consistently good, **append** its host to the right tier array for that domain and bump `updated`. Never remove venues; the map only grows.
4. **Concurrency note:** when several discover subagents run in parallel, do NOT let each
   write the venue map (last-writer-wins corruption). Have them list "venue-map candidates"
   in their output files; the orchestrator/consolidator folds candidates in once.

## The tier-balance rule (HARD)

- **Discover:** for each topic, the round MUST surface **≥1 formal** (authoritative/academic)
  AND **≥1 community** (Reddit/X/HN) source, when such sources exist.
- **If a tier is genuinely empty** for a topic, state that explicitly in the discover
  output — `"community: none found for <topic>"`. **No silent omission** — an unstated
  gap reads as "covered" when it wasn't.
- **Verify:** confirm the balance held across the research. If a whole tier is missing,
  flag it so the critic can open a targeted round to fill it (within the round cap).

Rationale: formal sources give authority and numbers; community sources catch what's
breaking, what practitioners actually hit, and the non-obvious failure modes — you need
both to be trustworthy AND current.

## Community fetch playbook (Reddit / X / HN)

Plain `WebFetch` is bot-blocked by Reddit and X. Use the path that actually works per
venue, and **always name a venue you couldn't reach** (no silent omission):

**Hacker News — rock solid, works everywhere (no auth).** Algolia API:
- Stories: `https://hn.algolia.com/api/v1/search?query=<q>&tags=story`
- Comments: `...&tags=comment` · recency: `...&numericFilters=created_at_i>...`
- `WebFetch` (or `curl`) this JSON directly — full titles, points, URLs, dates.
- Comment pages (`news.ycombinator.com/item?id=...`) rate-limit after a few fetches per
  session — budget them.

**X / Twitter** — usually needs a scraping API (Firecrawl scrape works on profile/post
URLs). Without one: `WebSearch "site:x.com <query>"` (snippet-level).

**Reddit** — blocks direct fetches (403) including `.json`. Full threads need a
server-side scraping actor (e.g., an Apify Reddit actor). Without one:
`WebSearch "site:reddit.com/r/<sub> <query>"` (snippet-level).

**No-shell environments:** subagents dispatched without Bash can't run local scraping
helpers — the reliable community path is HN via the Algolia API over WebFetch, with
site: WebSearch snippets as fallback. If 2–3 HN query variants return 0 relevant hits,
record `"community: none found for <topic>"` and STOP — don't burn turns retrying; for
org/enterprise topics the discourse usually lives in closed spaces (LinkedIn, industry
events) and that thinness is itself a finding worth stating in the final note.

**Rule:** the community tier is *satisfied* if HN OR Reddit OR X yields real signal — but
every venue you tried and couldn't reach must be named explicitly in the discover output.
