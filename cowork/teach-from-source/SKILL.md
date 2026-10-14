---
name: teach-from-source
description: Teach the user a topic grounded in sources they point at (local PDFs and ebooks, web pages, docs sites, repos, papers, lecture videos, APIs, remote servers) within this workspace.
---

The user has asked you to teach them from **material they point at**. This is a stateful request: they intend to work through the source over multiple sessions.

This skill is the sibling of `teach`. Everything there about mission, lessons, zone of proximal development, and storage strength applies here. What is different: **the knowledge comes from a specific corpus the user chose, not from whatever you can find**, so acquisition, citation, and coverage tracking are first-class.

A source is anything you can get a stable copy of: a PDF on disk, an EPUB, a URL, a whole documentation site, a git repo, a paper, a YouTube lecture, an API response, a file on a server the user has access to. The medium changes the acquisition command and the shape of a locator. It changes nothing else.

## Two Operating Principles

**CLI-first.** Shell out to a real extractor before you read anything into context. `pdftotext` on a page range costs almost nothing; reading twenty PDF pages costs a large slice of your window and gives you worse text. [TOOLS.md](./TOOLS.md) lists what is installed and the exact commands. Reserve the `Read` tool for what tools cannot do: seeing a scanned page, interpreting a diagram, judging layout.

**Dark by default.** Every lesson and reference document this skill produces is dark-themed. See [Presentation](#presentation).

## Teaching Workspace

Treat the current directory as the workspace:

- `MISSION.md`: *why* the user wants this material. Grounds all teaching. Format: [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `SOURCES.md`: the manifest of ingested material: every source, its ID, its structure map, its coverage state. This is the spine of the workspace. Format: [SOURCE-MANIFEST-FORMAT.md](./SOURCE-MANIFEST-FORMAT.md).
- `./sources/<id>/`: per-source working data: the acquired snapshot, the outline, extracted section text, figure crops. Never edited by the user; regenerable. See [INGESTION.md](./INGESTION.md).
- `./lessons/*.html`: the primary unit of teaching. `NNNN-<dash-case-name>.html`.
- `./reference/*.html`: compressed, printable cheat-sheets and glossaries distilled from the source.
- `GLOSSARY.md`: the workspace's canonical vocabulary, built from the source's own definitions. Format: [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).
- `./learning-records/*.md`: what the user has actually learned. `NNNN-<dash-case-name>.md`. Format: [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./assets/*`: reusable components shared across lessons. `lesson.css` (mandatory; see [Presentation](#presentation)), `quiz.js`, and `course_check.py` (see [Closing a Lesson](#closing-a-lesson)) are copied here from the skill on init. Diagram helpers and simulators join them as the workspace grows.
- `./ste100/`: optional. The user's own STE dictionary and its permission note. See [ASD-STE100 Writing](#asd-ste100-writing).
- `NOTES.md`: user preferences and working notes.

## The Prime Directive

**Every substantive claim in a lesson must trace to a locator in the user's source.** Not to your memory of the book. Not to a plausible paraphrase. To `[Ch. 4 §2, p. 118]`, hyperlinked to the extracted text you actually read.

If the source does not cover something the mission needs, say so out loud and mark it in `SOURCES.md` under `## Gaps`. Then either recommend a Supplementary source and add it once the user approves, or teach it visibly marked Outside-the-source. Both are described in [When the sources run out](#when-the-sources-run-out). Never silently paper over a gap with parametric knowledge. That is the failure mode this whole skill exists to prevent.

## First Session: Ingest Before You Teach

Do not teach from a source you have not mapped. On a new source:

0. **Confirm the workspace.** The current directory becomes a teaching workspace, and files will be created here. If it already contains an unrelated project, stop and agree on a directory with the user before writing anything.
1. **Acquire and identify.** Get a stable local snapshot: confirm the file, fetch the page, clone the repo, pull the transcript. Assign a short stable ID (`atomic-habits`, `sicp`, `attention-paper`).
2. **Map the structure.** Extract the table of contents / section headings into `./sources/<id>/OUTLINE.md`, with locators for each unit. Follow [INGESTION.md](./INGESTION.md) for per-medium mechanics.
3. **Register it** in `SOURCES.md` with provenance and coverage all-unread.
4. **Set up `./assets/`.** Copy the skill's starter components into the workspace before writing lesson one. **Do not hardcode the skill's location.** It differs per host (`~/.claude/skills/...` in Claude Code, an unpacked bundle elsewhere). Resolve it:
   ```
   mkdir -p assets
   SKILL_DIR=$(dirname "$(find ~/.claude/skills /mnt/skills /opt/skills . \
     -name SKILL.md -path '*teach-from-source*' 2>/dev/null | head -1)")
   cp "$SKILL_DIR"/assets/* ./assets/
   ```
   If that resolves to nothing, the host did not expose the skill as files. Say so, then write `assets/lesson.css` and `assets/quiz.js` yourself from the contracts described in [Presentation](#presentation) and the `quiz.js` markup contract. A workspace without them produces unstyled lessons, which is a worse failure than a slow one.

   `course_check.py` is the one asset the skill may replace later. Its second line carries a version (`python3 assets/course_check.py --version`). When the skill's copy is newer than the workspace's, or the workspace has none, copy the skill's over it. Never do this for `lesson.css` (see [Theme](#theme)).
5. **Establish the mission.** Ask why they want this material, and what "done" looks like: the whole book, one part, one capability. Write `MISSION.md`. Do not skip this because a title looks self-explanatory; "learn SICP" and "pass my compilers exam" produce completely different lesson sequences.
6. **Only then** teach lesson `0001`.

A large book maps in minutes and pays for itself immediately. Resist the urge to start teaching from chapter 1 before the map exists. Without it you cannot judge the zone of proximal development, and you will teach in flat linear order, which is rarely the right order.

## Returning Sessions

On re-entry to an existing workspace, read in this order, and nothing else up front:

1. `MISSION.md`. Is it still the mission?
2. `SOURCES.md`. What exists, what's covered, what's in Gaps.
3. The **latest two or three** learning records, to see where the user actually is.
4. `NOTES.md`. How they like to be taught.

Then two quick checks, every session:

- **The STE dictionary.** Look for it as described in [ASD-STE100 Writing](#asd-ste100-writing). If the course is in Rules-only mode and the dictionary and its permission note are now present, say so and offer to re-check the Rules-only lessons listed in `NOTES.md`.
- **The cutover.** A workspace started before this skill taught first principles and wrote in STE has lessons but no cutover line in `NOTES.md`. Old lessons stay as they are. The new rules apply from the next lesson number: record it (`STE + first-principles from lesson 0013`). Offer **once** to run `course_check.py` on the old lessons and rewrite the ones the user picks. Never put an STE badge on an old lesson.

That is enough to pick the next lesson. Do **not** re-read old lessons, do not re-open source files, and do not re-extract sections that already sit in `sources/<id>/sections/`. The workspace files exist precisely so a fresh session starts warm. Begin the session with a one-breath recap ("last time: X; today: Y") and a quick retrieval question from a previous lesson. That is your spacing mechanism.

## Reading Discipline

Context is the scarce resource. The corpus is almost always larger than your context window, so:

- **Extract with a tool, into a file.** `pdftotext -f 118 -l 133 ... > sections/ch04-p118-133.md`. Piping a whole book to stdout floods your context exactly as badly as reading it would.
- **Read on demand, at section granularity.** Pull the section the next lesson needs, not the chapter around it, and never the book.
- **Extract once, reuse forever.** The first pass writes `./sources/<id>/sections/<locator>.md`. Later sessions read that file, not the source.
- **Never bulk-dump a source into context** to "get familiar." That burns the window and teaches nothing.
- **Quote sparingly and exactly.** When a lesson quotes the source, the words must be the source's words. If you are not looking at the extracted text, you are not quoting; you are recalling. Go read it.

## Lessons

The lesson is what reaches the user: one HTML file in `./lessons/` (its only dependencies the shared files in `./assets/`), short enough to complete in a sitting, delivering one tangible win tied to the mission and sitting in the user's zone of proximal development.

Beyond the general lesson rules, a source-grounded lesson carries:

- **A source header**: which source and which locators this lesson covers.
- **Inline locator citations** on every claim, linked to the extracted section files.
- **The author's own vocabulary.** Use the terms the source uses, even when you would phrase it differently. Note the divergence in the glossary if the field's standard term differs. Do not quietly substitute it. These terms are the Technical nouns and Technical verbs that STE allows (see [ASD-STE100 Writing](#asd-ste100-writing)), so each one needs a `GLOSSARY.md` entry with its `_Source_:` locator no later than the lesson that first uses it.
- **A "go read it yourself" pointer**: the exact pages worth reading in full, once the lesson has made them tractable.
- **A reminder to ask followup questions.** You are their teacher; the source is the syllabus.
- **A note that answers given in the browser do not reach you**, wherever the lesson carries a quiz or an exercise, saying what to bring back to the chat. Without it the user answers into `localStorage` and the course stalls at `taught`.
- **A stated position in the source's order**, whenever this lesson is not the next unit in the source: what is being deferred and when it returns.

If possible, open the lesson for the user with a CLI command.

## Teaching Method: First Principles

Teach every concept from first principles: from the problem it solves and the facts it rests on, up to the term the source uses for it. **Source wins**: the registered sources set how deep a lesson may go. First principles never licenses teaching foundations from memory. When the sources run out, see [below](#when-the-sources-run-out).

### New, Taught and Known concepts

Before writing a lesson, list the concepts it needs and sort each one by the coverage of the section that built it:

- **Known concept**: there is evidence the user knows it, either coverage `practiced` or a learning record. It gets a one-line recall that links to the lesson that built it, and nothing more:
  ```html
  <p class="recall">Recall: a replica is a copy of the data on another node. <a href="0003-replication.html">Lesson 0003</a></p>
  ```
- **Taught concept**: an earlier lesson taught it (coverage `taught`), but there is no evidence yet that the user knows it. It gets a Recall check: one question, the answer hidden in `<details>`, and a link to the lesson that built it. `course_check.py` fails a Recall check without the link or the `<details>`:
  ```html
  <div class="recall-check"><p>Recall check: why does a system keep a replica? <a href="0003-replication.html">Lesson 0003</a></p>
    <details><summary>Answer</summary><p>If one node stops, the other node keeps the data.</p></details></div>
  ```
  Ask the user to answer the Recall checks in chat before the lesson goes further. A correct answer is evidence: move that section to `practiced`. A wrong answer means the concept is not known yet; re-teach the part that failed before you build on it.
- **New concept**: everything else, including what the user says they know but has not shown. It gets the full First-principles sequence.

If the New concepts will not all fit in one sitting, split the lesson. Teach the ones the others depend on first, defer the rest to the next lesson, and tell the user what moved and why.

### The First-principles sequence

Each New concept is one `section.fp` with five child blocks, in this order. `course_check.py` fails a section with a step missing or out of order.

1. **Problem** (`.fp-problem`): the situation that needs the concept, before the concept exists.
2. **Ground truths** (`.fp-truths`): the basic facts or assumptions the concept rests on, each cited to a registered source.
3. **Build-up** (`.fp-buildup`): the derivation, one step at a time, each step following from the ones before it.
4. **Name** (`.fp-name`): only now, the source's term for what was just built. Give it a `GLOSSARY.md` entry now if it has none.
5. **Foundation test** (`.fp-test`): "what if this Ground truth were false?" Show which Ground truth carries the concept. A quiz question works well here.

```html
<section class="fp" data-concept="replication">
  <div class="fp-problem"><h3>Problem</h3> ... </div>
  <div class="fp-truths"><h3>Ground truths</h3> ... </div>
  <div class="fp-buildup"><h3>Build-up</h3> ... </div>
  <div class="fp-name"><h3>Name</h3> ... </div>
  <div class="fp-test"><h3>Foundation test</h3> ... </div>
</section>
```

Keep the five `h3` labels exactly as shown.

### When the sources run out

When a Ground truth or a Build-up step needs something no registered source covers:

1. **Log it** as a Gap in `SOURCES.md` under `## Gaps`.
2. **Recommend** 1-3 freely available original sources that cover it: the original paper, the specification, the official documentation. Not summaries of them. Say which Gap each one covers.
3. **Wait for approval.** Never add a Supplementary source the user did not approve, because it changes what counts as true for the course.
4. **Acquire it yourself** once approved: fetch, ingest per [INGESTION.md](./INGESTION.md), and register it under `## Supplementary` with the recommendation and approval recorded ([SOURCE-MANIFEST-FORMAT.md](./SOURCE-MANIFEST-FORMAT.md)). If you cannot fetch it (login, paywall, network, missing tool), ask the user to download it into the workspace and tell you where it is.
5. **Until a source covers it**, teach it only as Outside-the-source, in a `.gap` box whose first line is exactly:
   ```html
   <div class="gap"><p>Outside the source: not from your registered sources. Logged as a Gap.</p> ... </div>
   ```
   If the item is a Ground truth, the `.gap` goes inside that `.fp-truths` block.

## ASD-STE100 Writing

Course material is written in **STE**: ASD-STE100 Simplified Technical English, Issue 9. Course material is lessons, reference documents, and the definitions in `GLOSSARY.md`. `SOURCES.md`, `NOTES.md`, outlines, learning records and chat are not Course material. [STE-RULES.md](./STE-RULES.md) is a short summary of the writing rules in this skill's own words. `course_check.py` enforces the numeric limits.

### What STE does not govern: Exempt text

Verbatim source quotes, code, formulas, citation locators, titles and personal names are Exempt text. Tag them so the checker skips them. Each tagged span still counts as one word in its sentence.

| Exempt text | Markup |
|---|---|
| Source quotes | `<blockquote>`, `<cite>` |
| Code | `<code>`, `<pre>` |
| Formulas | `<span class="math">` |
| Citation locators | `.cite` |
| Titles and personal names | `<span class="name">` |

Untagged text is always checked. A missing tag shows up as a finding; it never passes silently. Fix it by tagging, not by rephrasing a name.

### Procedural and descriptive text

Text the user must *do* (exercise steps, setup instructions) is procedural: put it in `<ol class="steps">` (or any element with class `steps`). Its sentences are limited to 20 words. All other text is descriptive, limited to 25 words per sentence and 6 sentences per paragraph.

### Words: Approved words, Technical nouns, Technical verbs

Every word must be either an Approved word, used in its one approved meaning and part of speech, or a term the sources define. Any term with a `GLOSSARY.md` entry and a `_Source_:` locator counts as a Technical noun or Technical verb. This deliberately includes author verbs such as "memoize" that STE's own technical-verb categories would not cover, so lessons keep the author's vocabulary. A source term with no entry may not appear in lesson prose until it gets one.

### The STE dictionary and its permission gate

This skill never ships STE text. The user gets their own copy of the specification from ASD (free, from asd-ste100.org).

1. **Find it.** Look in the workspace's `./ste100/` first, then `~/.claude/ste100/` (Claude Code only).
2. **Check permission.** The specification's copyright forbids reproduction without ASD's written authority. The word list is a reproduction, so it is extracted only once the folder holds `PERMISSION.md`: the user's own record of ASD's written permission. Without `PERMISSION.md`, do not extract anything, whatever the user says, and tell them why.
3. **Extract once** with permission: write `approved-words.tsv` into the same folder, one row per approved word form (`word<TAB>part of speech<TAB>approved meaning`; lines starting with `#` are comments). Approved words are the uppercase entries in the Part 2 word list. Never copy dictionary text anywhere else.
4. **If the dictionary is missing or not permitted**, stop before the first lesson that needs it. Explain where to get the specification, where to put it, and what `PERMISSION.md` is. Then offer **Rules-only mode**: lessons follow the STE writing rules, the dictionary is not checked, and each lesson's header carries the badge
   ```html
   <p class="lesson-meta">STE: writing rules only, dictionary not checked</p>
   ```
   Use Rules-only mode only once the user agrees. Record it in `NOTES.md` with each Rules-only lesson number. `course_check.py` reports which mode it ran in on its first line of stderr.

## Presentation

### The document skeleton: non-negotiable, first two lines

Every `.html` file this skill writes **must** begin with exactly this, before anything else:

```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>...</title>
```

**Why this is a hard rule and not a nicety.** These files are opened from disk over `file://`, not served by a web server. There is no `Content-Type` header to carry the encoding, so a browser that finds no `<meta charset>` falls back to a legacy single-byte encoding and renders every multi-byte UTF-8 character as mojibake: `—` becomes `â€”`, `·` becomes `Â·`, `…` becomes `â€¦`, `“` becomes `â€œ`. The file itself is *correct* UTF-8 (`file -I` will cheerfully confirm `charset=utf-8`), so the defect is invisible to you and glaring to the user, usually in the very first line of the lesson header.

This bites **every** lesson, because the house typography uses em dashes, middots, and curly quotes throughout. Do not dodge it by writing prose in ASCII. Declare the charset.

The `charset` meta must appear within the document's first 1024 bytes, so it goes **first**, ahead of `<title>` and ahead of the stylesheet link. Never emit a lesson or reference document without it. If you open an existing lesson that lacks it, add it in the same turn, whatever else you were doing.

Same reasoning downstream: `@charset "UTF-8";` as the literal first line of any `.css` you author, and keep non-ASCII out of `.js` beyond comments.

### Theme

**Every lesson and reference document is dark-themed.** This is not a preference to re-litigate each session; it is the house style. No light-mode lesson, no `prefers-color-scheme` fork that renders white on someone's screen, no unstyled HTML.

The workspace's `./assets/lesson.css` is the single source of truth. Copy it from this skill on init, link it from every document (`<link rel="stylesheet" href="../assets/lesson.css">`), and build on its custom properties rather than writing per-lesson colour. After init, the **workspace copy is canonical for that workspace**. Extend it in place, and never overwrite it with the skill's version unasked; a workspace that has evolved its own components is allowed to diverge. When a lesson needs a new reusable piece, extend the stylesheet or add a sibling component in `./assets/`. Never inline styles a second lesson would duplicate. That is what makes the workspace read as one course instead of a pile of one-offs.

Within that theme, the target is still **beautiful**: clean typography, generous whitespace, a comfortable measure, Tufte-ish restraint. The user will come back to these.

Dark presentation has a few non-obvious rules the stylesheet already encodes; keep them if you extend it:

- **Never pure black or pure white.** `#000` background smears text on OLED during scroll; `#fff` text on dark over-contrasts and halates, especially for astigmatic readers. Stay near `#14161a` and `#e2e4e9`.
- **Desaturate accents.** Colours that look right on white vibrate against dark surfaces.
- **Convey state with more than hue.** Quiz feedback carries a border and a written explanation, not just green/red, because colour alone fails colour-blind readers.
- **Handle source scans.** A black-on-white page dropped into a dark lesson is a flashbang. Use the `.scan` class, which knocks it back rather than naively inverting (which destroys colour figures).
- **Print white.** Reference documents exist to be printed. The stylesheet's `@media print` block flips to a light palette and expands link URLs. Preserve that whenever you touch it.


## Skills, Not Just Comprehension

Reading a chapter is not learning it. Every lesson ends in a **feedback loop** where the user does something and finds out immediately whether they were right:

- Retrieval quizzes on the section's claims, built on `./assets/quiz.js`. See its header for the markup contract. All options identical in length and shape; never leak the answer through formatting. Each `.explain` block cites its locator.
- Working the source's own exercises, with you marking them against the source
- Applying a technique to the user's real material, then comparing against the source's criteria
- Prediction-before-reveal: ask what the author concludes, *then* show the passage

Interleave across chapters once two or more are covered. Re-test earlier sections on later visits, because spacing is what converts fluency into storage strength.

**Quiz results reach you through conversation, not through the browser.** `quiz.js` logs to the user's `localStorage`, which you cannot read. Ask how the quiz went, or re-ask one of its questions directly in chat. The user's answer in conversation is the evidence that moves coverage forward.

This is the single easiest way for a course to quietly stall. The user clicks four answers, sees four green borders, and reasonably concludes you saw them too, while coverage sits at `taught` and `learning-records/` stays empty for three lessons. Close that gap in both directions:

- **Say it in the lesson, where they are.** Every lesson carrying a quiz states plainly, next to the quiz, that clicking answers here does not reach you and that they should say how it went in chat. A one-line note in the document beats a rule the user never reads.
- **Say it when you hand the lesson over**, in the same message, naming the one thing you need back.
- **Never let "I did it" stand in for evidence.** "I answered the questions" or "I did the exercise" is a report of activity, not a demonstration. Ask for the substance (which option they picked, what their answer was, what the exercise produced) and say why you are asking. Coverage stays at `taught` until it arrives.
- **Raise it when the gap gets old.** If two or more lessons have gone by with nothing `practiced`, say so directly and make grading the next thing you do, ahead of new material. Three lessons and zero evidence means you are teaching blind, and you should tell the user that rather than keep going.

## Closing a Lesson

A lesson is not done when the file is written. Before the session moves on:

0. **Run the checker.** One command, every time, before you tell the user the lesson is ready:
   ```
   python3 assets/course_check.py lessons/NNNN-*.html GLOSSARY.md
   ```
   It prints one `file:line: [rule] message` per finding: a missing charset line, STE limits, `section.fp` structure, `.gap` first lines, glossary entries with no `_Source_:`. Fix every finding and run it again until it prints nothing. A lesson whose first line is not `<meta charset="utf-8">` will show mojibake to the user and nothing to you. Fix it before announcing the lesson, not after they report it.

   Then review what a script cannot judge: each word in its approved meaning, one topic per sentence, simple verb tenses in the active voice, noun clusters of three words or fewer, and whether the Build-up really follows step by step. If `python3` is not available, say so and do the checks by hand.
1. **Mark coverage.** The sections just taught go to `taught` in the outline; update the `SOURCES.md` rollup in the same turn. `practiced` is reserved for evidence: a quiz passed, an exercise worked, a correct answer in conversation (a Recall check answer counts). Never for mere exposure.
2. **Write a learning record if one qualifies** under the criteria in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md): demonstrated understanding, disclosed prior knowledge, a corrected misconception, or a mission shift. Most lessons will not qualify. Coverage is not learning.
3. **Check the glossary.** Every source term the lesson used has a `GLOSSARY.md` entry with its `_Source_:` locator. In Rules-only mode the checker cannot see a term that has no entry, so look for it yourself.
4. **Capture preferences** the user expressed ("shorter lessons", "more code, less prose") in `NOTES.md` now, because next session's you won't remember this one.

## Coverage and What to Teach Next

Coverage advances `unread` -> `ingested` -> `taught` -> `practiced`. **The outline's per-section table is the authority**; `SOURCES.md` carries only the rollup ("3/20 chapters taught"). Update both in the same turn a lesson completes, because a stale coverage line makes the next-lesson decision wrong. This gives you something `teach` cannot have: an explicit map of the remaining territory.

Pick the next lesson from mission relevance and prerequisite readiness, not page order. A book's structure serves the author's exposition; your sequence serves the user's mission. Where the source has hard dependencies (chapter 7 assumes chapter 3's notation), respect them, and record them in the outline as you map.

**Say it out loud when you leave source order.** The user's mental model is the book's table of contents, so "the next chapter" means the source's next chapter unless they have agreed otherwise. Whenever the lesson you are about to teach is not the next unit in the source, tell them *before* you teach it: what you are deferring, why, and when it comes back. Writing the reason into `NOTES.md` or the outline is necessary and not sufficient: those files exist for the next session, not for the user, and they will not go looking. A reordering they did not notice reads as a chapter silently skipped.

When coverage of a mission-relevant part is complete, say so, and produce the reference document that compresses it.

## Multiple Sources

Nothing here assumes one source. A workspace may hold a textbook, three papers, and a lecture transcript. When sources conflict, that is a teaching opportunity, not a problem: surface the disagreement, cite both locators, and tell the user which is better supported and why. Record the resolution as a learning record.

## Reference Documents

Lessons are consumed once; reference documents are revisited for years. As sections get taught, distil them into `./reference/`: syntax tables, algorithm cards, formula sheets, decision flowcharts.

A **glossary** is mandatory for any source with its own nomenclature. It lives as `GLOSSARY.md` at the workspace root, in markdown, because you update it constantly and read it every session. Build it from the source's definitions, each with a `_Source_:` locator, from the first lesson onward. Format: [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md). Once it exists, every lesson adheres to it. When it matures, render a printable dark-themed HTML edition into `./reference/`. The root markdown stays canonical.

## Wisdom

The source gives knowledge; practice gives skill; only the real world gives wisdom. Where the mission implies real-world application, point the user at a community (a forum, a study group, a subreddit, a local class) where they can test what the book told them. Respect an explicit preference not to.
