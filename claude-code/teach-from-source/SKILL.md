---
name: teach-from-source
description: Teach the user a topic grounded in sources they point at (local PDFs and ebooks, web pages, docs sites, repos, papers, lecture videos, APIs, remote servers) within this workspace.
disable-model-invocation: true
argument-hint: "A source (file path, URL, repo, video) and what you want to learn from it"
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
- `./assets/*`: reusable components shared across lessons. `lesson.css` (mandatory; see [Presentation](#presentation)) and `quiz.js` are copied here from the skill on init. Diagram helpers and simulators join them as the workspace grows.
- `NOTES.md`: user preferences and working notes.

## The Prime Directive

**Every substantive claim in a lesson must trace to a locator in the user's source.** Not to your memory of the book. Not to a plausible paraphrase. To `[Ch. 4 §2, p. 118]`, hyperlinked to the extracted text you actually read.

If the source does not cover something the mission needs, say so out loud and mark it in `SOURCES.md` under `## Gaps`. Then either find a supplementary source (and add it to the manifest) or teach it explicitly flagged as outside-the-source. Never silently paper over a gap with parametric knowledge. That is the failure mode this whole skill exists to prevent.

## First Session: Ingest Before You Teach

Do not teach from a source you have not mapped. On a new source:

0. **Confirm the workspace.** The current directory becomes a teaching workspace, and files will be created here. If it already contains an unrelated project, stop and agree on a directory with the user before writing anything.
1. **Acquire and identify.** Get a stable local snapshot: confirm the file, fetch the page, clone the repo, pull the transcript. Assign a short stable ID (`atomic-habits`, `sicp`, `attention-paper`).
2. **Map the structure.** Extract the table of contents / section headings into `./sources/<id>/OUTLINE.md`, with locators for each unit. Follow [INGESTION.md](./INGESTION.md) for per-medium mechanics.
3. **Register it** in `SOURCES.md` with provenance and coverage all-unread.
4. **Set up `./assets/`.** Copy the skill's starter components into the workspace before writing lesson one. **Do not hardcode the skill's location.** It differs per host (`~/.claude/skills/…` in Claude Code, an unpacked bundle elsewhere). Resolve it:
   ```
   mkdir -p assets
   SKILL_DIR=$(dirname "$(find ~/.claude/skills /mnt/skills /opt/skills . \
     -name SKILL.md -path '*teach-from-source*' 2>/dev/null | head -1)")
   cp "$SKILL_DIR"/assets/* ./assets/
   ```
   If that resolves to nothing, the host did not expose the skill as files. Say so, then write `assets/lesson.css` and `assets/quiz.js` yourself from the contracts described in [Presentation](#presentation) and the `quiz.js` markup contract. A workspace without them produces unstyled lessons, which is a worse failure than a slow one.
5. **Establish the mission.** Ask why they want this material, and what "done" looks like: the whole book, one part, one capability. Write `MISSION.md`. Do not skip this because a title looks self-explanatory; "learn SICP" and "pass my compilers exam" produce completely different lesson sequences.
6. **Only then** teach lesson `0001`.

A large book maps in minutes and pays for itself immediately. Resist the urge to start teaching from chapter 1 before the map exists. Without it you cannot judge the zone of proximal development, and you will teach in flat linear order, which is rarely the right order.

## Returning Sessions

On re-entry to an existing workspace, read in this order, and nothing else up front:

1. `MISSION.md`. Is it still the mission?
2. `SOURCES.md`. What exists, what's covered, what's in Gaps.
3. The **latest two or three** learning records, to see where the user actually is.
4. `NOTES.md`. How they like to be taught.

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
- **The author's own vocabulary.** Use the terms the source uses, even when you would phrase it differently. Note the divergence in the glossary if the field's standard term differs. Do not quietly substitute it.
- **A "go read it yourself" pointer**: the exact pages worth reading in full, once the lesson has made them tractable.
- **A reminder to ask followup questions.** You are their teacher; the source is the syllabus.

If possible, open the lesson for the user with a CLI command.

## Presentation

### The document skeleton: non-negotiable, first two lines

Every `.html` file this skill writes **must** begin with exactly this, before anything else:

```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>…</title>
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

## Closing a Lesson

A lesson is not done when the file is written. Before the session moves on:

0. **Verify the file renders.** One command, every time, before you tell the user it is ready:
   ```
   head -1 lessons/NNNN-*.html | grep -q 'charset' && echo OK || echo "MISSING CHARSET"
   ```
   A lesson whose first line is not `<meta charset="utf-8">` will show mojibake to the user and nothing to you. Fix it before announcing the lesson, not after they report it.
1. **Mark coverage.** The sections just taught go to `taught` in the outline; update the `SOURCES.md` rollup in the same turn. `practiced` is reserved for evidence: a quiz passed, an exercise worked, a correct answer in conversation. Never for mere exposure.
2. **Write a learning record if one qualifies** under the criteria in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md): demonstrated understanding, disclosed prior knowledge, a corrected misconception, or a mission shift. Most lessons will not qualify. Coverage is not learning.
3. **Promote glossary terms** the user has shown they can use correctly.
4. **Capture preferences** the user expressed ("shorter lessons", "more code, less prose") in `NOTES.md` now, because next session's you won't remember this one.

## Coverage and What to Teach Next

Coverage advances `unread` → `ingested` → `taught` → `practiced`. **The outline's per-section table is the authority**; `SOURCES.md` carries only the rollup ("3/20 chapters taught"). Update both in the same turn a lesson completes, because a stale coverage line makes the next-lesson decision wrong. This gives you something `teach` cannot have: an explicit map of the remaining territory.

Pick the next lesson from mission relevance and prerequisite readiness, not page order. A book's structure serves the author's exposition; your sequence serves the user's mission. Where the source has hard dependencies (chapter 7 assumes chapter 3's notation), respect them, and record them in the outline as you map.

When coverage of a mission-relevant part is complete, say so, and produce the reference document that compresses it.

## Multiple Sources

Nothing here assumes one source. A workspace may hold a textbook, three papers, and a lecture transcript. When sources conflict, that is a teaching opportunity, not a problem: surface the disagreement, cite both locators, and tell the user which is better supported and why. Record the resolution as a learning record.

## Reference Documents

Lessons are consumed once; reference documents are revisited for years. As sections get taught, distil them into `./reference/`: syntax tables, algorithm cards, formula sheets, decision flowcharts.

A **glossary** is mandatory for any source with its own nomenclature. It lives as `GLOSSARY.md` at the workspace root, in markdown, because you update it constantly and read it every session. Build it from the source's definitions, with locators, from the first lesson onward. Format: [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md). Once it exists, every lesson adheres to it. When it matures, render a printable dark-themed HTML edition into `./reference/`. The root markdown stays canonical.

## Wisdom

The source gives knowledge; practice gives skill; only the real world gives wisdom. Where the mission implies real-world application, point the user at a community (a forum, a study group, a subreddit, a local class) where they can test what the book told them. Respect an explicit preference not to.
