# teach-from-source

**An AI skill that teaches you a topic from the material *you* point at, and refuses to make anything up.**

Point it at a PDF, an EPUB, a Kindle file, a docs site, a paper, a git repo, or a lecture video. It maps the source, builds a mission, and teaches you through it one lesson at a time. Lessons arrive as dark-themed HTML with interactive quizzes, and **every substantive claim carries a locator back into your source**.

Two versions live in this repo: one for the **Claude Code CLI**, one for **Claude Cowork**.

---

## Credits, in the order they're owed

**First, Matt Pocock ([@mattpocock](https://github.com/mattpocock)).** This skill exists because his `teach` skill exists. The pedagogical spine is his design: mission-first teaching, the zone of proximal development, storage strength over fluency, and learning records as ADRs for what a person actually knows. `teach-from-source` is explicitly its sibling rather than its replacement. If you haven't seen his skills, go there first. This one assumes you understand why they work.

**Second, Claude ([@claude](https://github.com/claude), by [@anthropics](https://github.com/anthropics)).** The skill was built with Claude, across a lot of sessions. Not "Claude wrote a draft and I cleaned it up". Claude did the architecture work: the three-phase ingestion model, the context-discipline rules that keep a 900-page book from eating a context window, the degradation ladder for missing binaries, and the reason every lesson opens with `<meta charset="utf-8">` (ask me about character encodings some time). Naming that honestly matters more to me than looking clever.

**Finally, me: Abhijit Bhadoria ([@Abhijit-17](https://github.com/Abhijit-17)).** I kept buying good technical books and then not reading them properly. I wanted something that would teach me *Designing Data-Intensive Applications* from **my copy of DDIA**, cite the page, quiz me on it, and tell me honestly when the book didn't cover something. That's what this is. If it's useful to you too, wonderful. That's why it's here.

---

## The problem this solves

Ask any LLM to teach you a book and it will teach you *its memory of reviews of that book*. Fluently. Confidently. With page numbers it invented.

That's the failure mode this whole skill exists to prevent. So it inverts the default:

> **The Prime Directive.** Every substantive claim in a lesson must trace to a locator in your source. Not to a plausible paraphrase. To `[Ch. 4 Sec. 2, p. 118]`, hyperlinked to the extracted text the model actually read.

When your source *doesn't* cover something your mission needs, the skill says so out loud, logs it under `## Gaps` in `SOURCES.md`, and either recommends a supplementary source for you to approve or teaches it clearly flagged as outside-the-source. It never quietly papers over a hole with parametric knowledge.

---

## What's new in v1.1.0

- **First principles, built in.** Every new concept is taught in five steps: the problem, the ground truths it rests on (each cited), a step-by-step build-up, the name last, and a "what if this ground truth were false?" test. Concepts you have already shown you know get a one-line recall instead. Concepts an earlier lesson taught, but that you haven't shown you know yet, get a **recall check**: one question with a hidden answer. Answer it in chat and that counts as evidence.
- **The source still wins.** Your sources set how deep a lesson goes. When first principles needs a foundation they don't cover, the skill logs a gap, recommends 1-3 freely available original sources, and fetches them only after you approve. Until then, that material appears in a visible "Outside the source" box. A common name no source gives (say, "coordinator") can still go in the glossary, marked Outside-the-source and tied to its gap.
- **Illustrations are not gaps.** Mapping a concept onto your own project, or explaining it through an analogy, goes in a neutral "Illustration" box. It isn't logged as a gap, so the red gap box keeps meaning "this isn't from your sources". A new fact about the topic still goes in a gap box.
- **Answers are cited, questions are free.** Quiz questions and interview prompts make no claim. Every answer does: each quiz explanation, model answer and critique cites its source or is marked Outside-the-source. Exact source words inside a sentence go in `<q>` with a citation next to them.
- **Lessons in Simplified Technical English.** Lessons, reference documents and glossary definitions follow ASD-STE100 (Issue 9): short sentences, one meaning per word, the author's own terms kept through the glossary. See [STE setup](#ste-setup).
- **A lesson checker.** `assets/course_check.py` (Python 3, standard library only) runs before every lesson is handed over. It prints `file:line` findings for the charset line, the STE limits, the first-principles structure, recall checks, uncited quotes and quiz explanations, citations that aren't links, glossary locators, and lesson numbers that don't exist yet.
- **Splitting a lesson renumbers nothing.** Only lessons that exist have numbers. A plan lists topics in order, and lessons refer to a future lesson by its topic.
- **Older courses keep working.** Existing lessons stay as they are, and the new rules start at your next lesson. The skill's own lesson components ship in `assets/components.css`, which the skill may update, so your `lesson.css` is never overwritten. On each upgrade the skill checks your course notes and glossary for anything that now conflicts, and proposes changes for you to approve. When you rewrite an old lesson, the old version is kept beside it as `NNNN-name.vX.Y.Z.html`, and the checker skips it.

---

## Features

**Any source, one workflow.** PDF, EPUB, Kindle (`.azw3`/`.mobi`), web pages, whole docs sites, git repos, papers, YouTube lectures, JSON APIs, files on a remote box. The medium changes the acquisition command and the shape of a locator. It changes nothing else.

**CLI-first ingestion.** `pdftotext -f 118 -l 133` on a page range costs almost nothing. Reading twenty PDF pages into context costs a large slice of the window and gives you *worse* text. The skill shells out to real extractors (poppler, pandoc, trafilatura, yt-dlp, calibre) and reserves the model's eyes for what tools genuinely can't do: scanned pages, diagrams, layout judgement.

**Three-phase ingestion that respects your context window.** Acquire, then map, then extract, always in that order and never inverted. The whole source gets mapped once, cheaply, into an `OUTLINE.md`. Sections get extracted **on demand**, one at a time, and cached forever. No bulk-dumping a book into context "to get familiar."

**Lessons that are actually nice to read.** One self-contained HTML file per lesson, dark-themed by house rule, Tufte-ish typography, generous whitespace, a comfortable measure. Not pure black (smears on OLED), not pure white text (halates), never colour-alone for state. You'll come back to these.

**Quizzes with a real feedback loop.** Retrieval quizzes built on a tiny dependency-free `quiz.js`. Options are matched in length and shape so formatting never leaks the answer. Every explanation cites its locator. Feedback carries a border *and* prose, not just green and red.

**Coverage is not learning.** Sections advance `unread` to `ingested` to `taught` to `practiced`, and `practiced` requires *evidence*: a quiz passed, an exercise worked, a correct answer given in conversation. Exposure doesn't count.

**Stateful across sessions.** The workspace is the memory. A returning session reads `MISSION.md`, `SOURCES.md`, the last two or three learning records, and `NOTES.md`, then starts warm without re-reading a single lesson or re-extracting a single section.

**A glossary in the author's own words.** The skill uses the source's vocabulary even where it would phrase things differently, and records the divergence when the field's standard term differs. Every term gets a `GLOSSARY.md` entry, with a locator, no later than the lesson that first uses it. That entry is also what lets the author's terms into STE-checked lessons.

**Multiple sources, and conflicts as material.** A workspace can hold a textbook, three papers, and a lecture. When they disagree, that's a lesson. Both locators get cited, the better-supported position gets called, and the resolution becomes a learning record.

**Graceful degradation, never a blocked lesson.** The toolchain gets probed once per workspace and the result is recorded. Missing `pdftotext`? Try `mutool`. No `pandoc` for an EPUB? The unpacked XHTML is readable. Whatever produced a section file gets written into that file's header, because a hand-stripped extraction is lossier than a `pandoc` one and its quotes deserve more suspicion. It never asks you to install something mid-lesson.

---

## Which version do I want?

| | **Claude Code CLI** | **Claude Cowork** |
|---|---|---|
| Runs on | Your Mac / Linux box | Anthropic's cloud sandbox |
| Sources live | On your disk, in place | Reached via Claude Desktop |
| Toolchain | Whatever you install; the full poppler/pandoc/calibre/yt-dlp stack | Whatever the sandbox ships; **probe, don't assume** |
| Invocation | Explicit, via `/teach-from-source` | Natural language, steered by global instructions |
| Best for | Big local PDFs, EPUBs, Kindle libraries, repos, OCR work | Web/docs-site sources, working from any device, no local setup |
| Guide | **[docs/claude-code-cli.md](./docs/claude-code-cli.md)** | **[docs/claude-cowork.md](./docs/claude-cowork.md)** |

**You can run both.** They produce the same workspace layout, so a course started in the CLI can be continued in Cowork and back again. The workspace files *are* the handoff.

### How the two versions differ

They're the same skill. Literally: the payloads are byte-for-byte identical apart from **two lines of YAML frontmatter** in `SKILL.md`.

```diff
  ---
  name: teach-from-source
  description: Teach the user a topic grounded in sources they point at ...
+ disable-model-invocation: true
+ argument-hint: "A source (file path, URL, repo, video) and what you want to learn from it"
  ---
```

Those two lines are Claude Code CLI features:

- `disable-model-invocation: true` stops Claude from firing a long, stateful, file-writing teaching session at you because you happened to say the word "teach". You invoke it deliberately with `/teach-from-source`.
- `argument-hint` is what the CLI shows you in the slash-command menu.

Cowork doesn't read either key, so the Cowork build drops them and gets the same deliberateness from a global instruction instead. Everything downstream (ingestion, lessons, quizzes, coverage, glossary, presentation) is shared, unchanged.

---

## Repository structure

```
teach-from-source/
+-- README.md                       <- you are here
+-- LICENSE
|
+-- docs/
|   +-- claude-code-cli.md          <- install & run the local CLI version
|   +-- claude-cowork.md            <- set up & run the Cowork version
|   `-- example-prompts.md          <- one-liner and structured-brief examples
|
+-- claude-code/
|   `-- teach-from-source/          <- copy this into ~/.claude/skills/
|       +-- SKILL.md                <- + disable-model-invocation, + argument-hint
|       +-- INGESTION.md            <- acquire, map, extract, per medium
|       +-- TOOLS.md                <- the CLI toolchain, recipes, degradation ladder
|       +-- MISSION-FORMAT.md       <- MISSION.md contract
|       +-- SOURCE-MANIFEST-FORMAT.md <- SOURCES.md contract
|       +-- GLOSSARY-FORMAT.md      <- GLOSSARY.md contract
|       +-- LEARNING-RECORD-FORMAT.md <- learning-records/*.md contract
|       +-- STE-RULES.md            <- STE Part 1 rules, summarised in our own words
|       `-- assets/
|           +-- lesson.css          <- the dark theme, single source of truth
|           +-- components.css      <- styles for the skill's lesson components
|           +-- quiz.js             <- ~40 lines, no dependencies
|           `-- course_check.py     <- the lesson checker, standard library only
|
+-- cowork/
|   `-- teach-from-source/          <- zip this folder, upload to Cowork
|       `-- ...                     <- identical, minus the two CLI-only keys
|
+-- scripts/
|   +-- install-cli.sh              <- symlink or copy into ~/.claude/skills/
|   `-- build-cowork-zip.sh         <- produce dist/teach-from-source.zip
|
`-- tests/                          <- python3 -m unittest (not shipped in the skill)
```

`SKILL.md` is the entry point in both builds and loads the rest progressively. The format files and `TOOLS.md` are only pulled in when they're actually needed, which keeps the resident cost of having the skill installed near zero.

---

## Quickstart

### Claude Code CLI (60 seconds)

```bash
git clone https://github.com/Abhijit-17/teach-from-source.git
cd teach-from-source
./scripts/install-cli.sh            # copies into ~/.claude/skills/teach-from-source

mkdir -p ~/LEARNING/ddia && cd ~/LEARNING/ddia
claude
```

Then, in the session:

```
/teach-from-source ~/books/ddia.pdf
I want to design a replication strategy I can defend in an architecture review.
```

That one line is genuinely enough. When you want tighter control (a fixed chapter cadence, a specific teaching persona, a challenge at the end of every lesson), see **[docs/example-prompts.md](./docs/example-prompts.md)** for a structured brief you can adapt.

Full walkthrough, toolchain install, and troubleshooting: **[docs/claude-code-cli.md](./docs/claude-code-cli.md)**.

### Claude Cowork (5 minutes)

Download `teach-from-source.zip` from the [**latest release**](https://github.com/Abhijit-17/teach-from-source/releases/latest), or build it yourself:

```bash
git clone https://github.com/Abhijit-17/teach-from-source.git
cd teach-from-source
./scripts/build-cowork-zip.sh       # -> dist/teach-from-source.zip
```

Upload it via **Settings -> Skills -> Add -> Upload skill**, paste the global instruction from the guide, connect a folder, and say what you've got. Full walkthrough and the sandbox-toolchain gotchas: **[docs/claude-cowork.md](./docs/claude-cowork.md)**.

---

## The one thing that will silently stall your course

**Answering a quiz in the browser is a dead end. Claude never sees it.**

This applies identically in the Claude Code CLI and in Cowork, and it is the single
most common way a course quietly stops working.

`quiz.js` writes your answers to the browser's `localStorage`. Claude cannot read
`localStorage`, in either host. So you click four options, four borders turn green,
you reasonably conclude it landed, and meanwhile coverage is still sitting at
`taught`, `learning-records/` is still empty, and the next lesson is being chosen
from no evidence at all. It is perfectly possible to work through three lessons and
have the skill know nothing about how you did.

**Report your progress in the chat, with the substance.** Not "I did the quiz" or
"I finished the exercise" - those describe activity, not understanding, and the
skill is instructed not to accept them:

```
Lesson 2 quiz: Q1 I picked b, Q2 c, Q3 a. Hesitated on Q3.
The exercise gave me two cases where I'd called it luck and one where I hadn't.
```

That is what moves a section from `taught` to `practiced`, what produces a learning
record, and what the next lesson is chosen against. Reporting a *wrong* answer is
worth more than reporting a right one, because a corrected misconception is the
highest-value thing the skill can record about you.

The same applies to anything else you did away from the chat: exercises worked on
paper, a technique tried in a real meeting, a chapter you read ahead. If it did not
happen in the conversation, it did not happen.

> Lessons from v1.0.1 onward carry this warning next to the quiz itself, and the
> skill will raise it if two lessons pass with nothing practiced. Neither is a
> substitute for telling it how you did.

---

## What you actually get

A learning workspace: one directory per course, yours, plain files, no lock-in.

```
~/LEARNING/ddia/
+-- MISSION.md                      # why you're reading this, and what "done" means
+-- SOURCES.md                      # the spine: what's ingested, coverage, gaps, conflicts
+-- GLOSSARY.md                     # the source's vocabulary, each term with its locator
+-- NOTES.md                        # how you like to be taught
+-- sources/
|   `-- ddia/
|       +-- OUTLINE.md              # the map: units, locators, dependencies, page offset
|       +-- sections/
|       |   `-- ch05-p151-190.md    # extracted once, header carries locator + tool + date
|       +-- figures/
|       `-- raw/                    # snapshots: unpacked EPUB, fetched HTML, transcripts
+-- lessons/
|   +-- 0001-replication-is-a-latency-problem.html
|   `-- 0002-leaders-followers-and-the-lies-they-tell.html
+-- reference/
|   `-- consistency-models-card.html    # printable; @media print flips it to light
`-- learning-records/
    `-- 0001-quorum-intuition-was-wrong.md
```

Every file is human-readable and human-editable. Delete a lesson you didn't like. Rewrite `MISSION.md` when your goal moves. Extend `assets/lesson.css` and every future lesson inherits it. The workspace is the state, and it's yours.

---

## Design principles

The rules in `SKILL.md` that are worth arguing about, and why they're there:

1. **Never invent a locator.** If you can't point at where the source says something, you didn't read it there. The source wins over expectation, every time.
2. **Extract with a tool, into a file.** Piping a whole book to stdout floods context exactly as badly as reading it would. Extract once, at section granularity, reuse forever.
3. **Teach in mission order, not page order.** A book's structure serves the author's exposition. Your sequence serves *your* goal, subject to the source's real prerequisites, which get recorded in the outline as it's mapped.
4. **Dark by default, and it's not up for re-litigation each session.** Near `#14161a` on `#e2e4e9`, desaturated accents, state conveyed by more than hue, scans knocked back rather than naively inverted, and a `@media print` block that flips reference cards to light because reference cards get printed.
5. **`<meta charset="utf-8">` on line one of every HTML file.** These open over `file://`, where there's no `Content-Type` header to carry the encoding. Skip it and the lesson's typography renders as `â€”`: invisible to the model, glaring to you, usually in the first line of the header.
6. **Coverage is not learning.** `practiced` needs evidence. And quiz results reach the model through *conversation*, not the browser. `quiz.js` writes to your `localStorage`, which the model can't read, so being asked "how did the quiz go?" is a feature.
7. **Never block a lesson on an install.** Degrade deliberately, record the degradation, keep teaching.
8. **First principles, bounded by the source.** Every new concept is derived from cited ground truths, but your sources decide how deep. The skill never fetches a new source without your approval, because that would change what counts as true for your course.
9. **Write for a reader under load.** STE keeps sentences short and words unambiguous, which is what you want when the concept itself is hard. The author's terms stay, through the glossary, so a lesson still maps onto the page.

---

## Requirements

- **Claude Code CLI version:** Claude Code, plus as much of the extraction toolchain as you care to install. `poppler` and `git` get you most of the way; `pandoc`, `trafilatura`, `calibre`, and `yt-dlp` unlock EPUB, web, Kindle, and video respectively. See [docs/claude-code-cli.md](./docs/claude-code-cli.md).
- **Cowork version:** a Claude account with Cowork, and Claude Desktop if your sources are local files. Nothing to install, but read the sandbox toolchain table in [docs/claude-cowork.md](./docs/claude-cowork.md) before you point it at a Kindle file or a video.
- **Both:** `python3` for the lesson checker (see [docs/claude-code-cli.md](./docs/claude-code-cli.md) for the CLI). If it is missing, the skill says so and checks lessons by hand.

---

## STE setup

Lessons follow the writing rules of ASD-STE100 Simplified Technical English from the first lesson, with no setup. Checking every word against the STE **dictionary** needs two things from you:

1. **Your own copy of the specification.** This repo does not ship it. Get it free from ASD: [https://www.asd-ste100.org/](https://www.asd-ste100.org/).
2. **ASD's written permission.** The specification's copyright notice forbids reproducing it without written authority from ASD, and the dictionary check needs a word list extracted from your copy. Ask ASD for permission. When they grant it, save their reply as `PERMISSION.md` next to the specification.

Where to put them:

| Version | Folder |
|---|---|
| Claude Code CLI | `~/.claude/ste100/` (shared by every course), or a course's own `./ste100/` |
| Cowork | each course's own `./ste100/`. Cowork cannot see `~/.claude/`, so each course needs its own copy. |

Until both are in place, the skill offers **Rules-only mode**: lessons follow the STE writing rules, the dictionary is not checked, and each lesson says so in its header (`STE: writing rules only, dictionary not checked`). The skill looks again every session. Once it finds the dictionary and `PERMISSION.md`, it extracts the word list once, into that same folder, and offers to re-check your Rules-only lessons.

[`STE-RULES.md`](./claude-code/teach-from-source/STE-RULES.md) summarises the writing rules in our own words: rule numbers, subjects and limits, no text from the specification.

---

## Contributing

Issues and PRs welcome, particularly:

- **New source media.** An acquisition path for a format `INGESTION.md` doesn't cover yet.
- **Degradation paths.** A fallback that works when a preferred binary is missing.
- **Presentation components.** Reusable pieces for `assets/`: diagram helpers, simulators, better reference-card layouts.
- **Field reports.** Which sources it taught well, and which it taught badly. The failure cases are more useful than the successes.

If you change `SKILL.md`, change it in **both** builds and keep the diff to those two frontmatter keys. `scripts/build-cowork-zip.sh` will tell you if it has drifted.

---

## License

MIT. See [LICENSE](./LICENSE).

The skill files are yours to fork, vendor, and rewrite. The pedagogical model came from [@mattpocock](https://github.com/mattpocock)'s work. Please keep the credit, and go read his skills.

---

## Acknowledgements

| | | |
|---|---|---|
| **Inspiration** | [@mattpocock](https://github.com/mattpocock) | The `teach` skill this one is a sibling of. Mission-first teaching, the zone of proximal development, storage strength over fluency, and learning records as ADRs are all his design. |
| **Built with** | [@claude](https://github.com/claude) and [@anthropics](https://github.com/anthropics) | Architecture, not autocomplete: three-phase ingestion, the context-discipline rules, the degradation ladder for missing binaries, and the presentation contract. |
| **Author** | [@Abhijit-17](https://github.com/Abhijit-17) | Built it after buying too many good technical books and not reading them properly. |

Matt, if this crosses your feed: thank you. The `teach` skill changed how I read, and this is what happened when I pointed it at my own bookshelf. Nothing here is meant to replace it.
