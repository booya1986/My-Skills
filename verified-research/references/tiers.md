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

Plain `WebFetch` is bot-blocked by Reddit and X. Use the route that actually works per
venue, and **always name a venue you couldn't reach**: the point of the tier-balance
rule is that an unstated gap reads as "covered".

**Reddit, with a Firecrawl MCP available: its search is the route.** Load the
Firecrawl search tool (e.g. `firecrawl_search`; via ToolSearch if tools are deferred)
and query `site:reddit.com/r/<sub> <terms>` with `sources: ["web"]`. It returns real
thread titles, subreddit, upvote and comment counts and a highlight sentence. That is
snippet level, and it is usually enough to corroborate practitioner patterns the formal
tier cannot. Known dead ends at the time of writing: Firecrawl *scrape* refuses
reddit.com, `WebFetch` and `.json` endpoints return 403, and `site:reddit.com` through
plain `WebSearch` often returns nothing. Subagents are frequently not given MCP tools,
so **the orchestrator runs this pass itself** after the lenses return and writes
`ART/gathered-community-supplement.md`. Full threads need a server-side scraping actor
(e.g., an Apify Reddit actor), when you have one.

**Hacker News: reliable everywhere (no auth), thin for enterprise topics.** Algolia API:
- Stories: `https://hn.algolia.com/api/v1/search?query=<q>&tags=story`
- Comments: `...&tags=comment` · recency: `...&numericFilters=created_at_i>...`
- `WebFetch` (or `curl`) this JSON directly: full titles, points, URLs, dates.
- Comment pages (`news.ycombinator.com/item?id=...`) rate-limit after a few fetches per
  session; budget them.
- HN is genuinely empty on many organizational disciplines (HR, L&D, procurement…); two
  or three variants returning nothing is a finding, not an access failure. What it does
  carry is the receiving end: engineers and employees describing the tools they are
  made to use.

**X / Twitter:** `WebSearch "site:x.com <query>"` is snippet level and often ignores the
site filter; a scraping API (e.g., Firecrawl scrape of a direct post URL) works. Low
yield; do not spend more than two calls.

**Closed communities are a finding.** Most enterprise-function and niche local-market
discourse lives in LinkedIn groups, private chat communities and paid conferences. When
every open venue is empty in every relevant language, write `community: none found`
once, state in the note that the knowledge sits with people, and add an interview guide
(see references/decision-questions.md) instead of retrying.

**No-shell / no-MCP subagents:** the reliable path is HN via the Algolia API over
WebFetch, with `site:reddit.com` / `site:x.com` WebSearch snippets as fallback. If 2–3
query variants return 0 relevant hits, record `"community: none found for <topic>"` and
STOP; don't burn turns retrying.

**Rule:** the community tier is *satisfied* if HN OR Reddit OR X yields real signal, but
every venue you tried and couldn't reach must be named explicitly in the discover output.
