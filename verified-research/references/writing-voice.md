# Writing the note like a native speaker

Accurate and unreadable is a common failure. A note written like a translated analyst
report (noun chains, jargon with no picture behind it, sentences nobody would say out
loud) gets sent back with "most of this is not understandable, write it the way people
talk". This file exists so consolidate produces the readable version the first time.

The rule applies in **every language**: write like a native speaker of the note's
language explaining the topic to a smart colleague, never like a translation of the
sources. If the user keeps a tone-of-voice or style guide of their own, read it before
writing and let it override anything here.

A research note is always in an **educational mode**: definition first, one picture,
tables, practical use, summary. Not a personal story, not a sales page.

## The test that catches everything

Before saving, read each paragraph as if saying it to a colleague over coffee. If you
would not say the sentence out loud, rewrite it. If a term needs a definition to be said
out loud, define it in the same sentence or replace it.

## The tell of a calque

Research sources are mostly in English, so notes in other languages drift into English
sentence structure with local words dropped in. The tell: a verb that exists in the
language but that nobody uses for that action, or a noun phrase that is a literal gloss
of an English term. English notes have their own version: consultant-speak that nobody
says out loud ("leverage synergies", "operationalize the framework"). When you notice
one, do not patch the phrase; re-say the whole sentence from scratch as if explaining it
on the phone.

## The voice in five rules

1. **Start from the answer.** Each section opens with the conclusion in one plain
   sentence ("Short version: this team is not the one that maintains the system."). Then
   the explanation.
2. **One everyday picture per hard idea.** "Think of two people counting the same room
   and getting different numbers, and both being right." One metaphor from daily life,
   not over-explained.
3. **Short paragraphs, spoken rhythm.** Two to four sentences. Plain connectors people
   actually say ("in short", "but wait", "so why does this matter?").
4. **"We" and "you", not "the organization" and "the function".** The reader is a person
   deciding something, not an institution.
5. **Numbers inside a sentence that says what they mean.** Not "1:2,500" alone but "one
   analyst for every 2,500 employees, so about four people in a 10,000-person company".

## Patterns to rewrite on sight

| Reads as report-speak / translation | Say instead |
|---|---|
| Bare abstract nouns ("data integrity", "data governance") | What it means in practice ("numbers that are right", "who is responsible for which field"), with the term in brackets once |
| "The release cadence of SaaS is a fixed tax" | "The vendor updates the system twice a year whether you want it or not, and someone has to check everything still works after each update" |
| "The evidence supports…", "is substantiated" | "There is research showing…", "this shows up in the studies" |
| "Stakeholders", "the function", "entities" | The actual people: payroll, IT, finance, managers, employees |
| Acronyms the reader won't know (UAT, SLA, RACI, intake) | Say what it is: user testing before go-live, a promise of how long handling takes, a table of who owns what, who receives requests. Keep the acronym in brackets the first time only if the reader will meet it at work |
| "A quarter of them are delayed" (a number wearing a tie) | "One in four misses its deadline" |
| "Exceeded expectations in some aspect" | "Came out better than expected, at least in one area" |
| "Single source of truth" in running prose | "One place with the right number", "a number everyone agrees on" |
| A sentence longer than two lines | Two sentences |
| A heading that is a noun phrase | Fine for headings, but the first sentence under it must be spoken language |

## Jargon that may stay

Established acronyms the reader uses daily (AI, KPI), product names, and names of laws
or standards. Everything else gets a plain explanation the first time.

## Tables

Cell text follows the same rule. "Double data entry" is fine; "integration of data
interfaces between core systems" is not. Column headers are questions or plain nouns:
"What it is", "When it's right", "What it takes".

## Punctuation and register

Avoid academic register, empty management jargon, and signposting sentences that
describe the page instead of saying something ("In this section we will explore…"). No
emoji in the body of a research note. Many readers find em dashes and colon-heavy prose
machine-sounding; prefer periods and commas in running text unless the user's style
guide says otherwise.

## Sources inside the text are links, not names

Every place the text names a source ("according to [Survey X 2026](url)", "the most
cited thread on r/<sub>") carries the link right there. The reader should never have to
scroll to the sources list to open what a sentence rests on. Link the first mention in
each paragraph; the sources list at the end stays as the full inventory with dates and
confidence.

## Right-to-left languages

When the note's language is written right-to-left, keep the rendering rules from
SKILL.md: top-down flows or tables only, no ASCII bars or trees, and arrows that mean
"next" point left (or down when stacked). Keep Latin-script terms short inside RTL
sentences; long mixed-direction runs reorder unpredictably.

## Checklist before the note is saved

- Every source mentioned in the text is a clickable link at that spot.
- Every H2 opens with one plain sentence a colleague would say.
- Every hard concept has one everyday picture.
- No paragraph over four sentences.
- Every number has a "so what" next to it.
- Every jargon term is explained once in plain words.
- Read-aloud test passed on the TL;DR, the key insights, and the bottom line at minimum.
