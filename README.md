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

When your source *doesn't* cover something your mission needs, the skill says so out loud, logs it under `## Gaps` in `SOURCES.md`, and either finds you a supplementary source or teaches it clearly flagged as outside-the-source. It never quietly papers over a hole with parametric knowledge.

---

## Features

**Any source, one workflow.** PDF, EPUB, Kindle (`.azw3`/`.mobi`), web pages, whole docs sites, git repos, papers, YouTube lectures, JSON APIs, files on a remote box. The medium changes the acquisition command and the shape of a locator. It changes nothing else.

**CLI-first ingestion.** `pdftotext -f 118 -l 133` on a page range costs almost nothing. Reading twenty PDF pages into context costs a large slice of the window and gives you *worse* text. The skill shells out to real extractors (poppler, pandoc, trafilatura, yt-dlp, calibre) and reserves the model's eyes for what tools genuinely can't do: scanned pages, diagrams, layout judgement.

**Three-phase ingestion that respects your context window.** Acquire, then map, then extract, always in that order and never inverted. The whole source gets mapped once, cheaply, into an `OUTLINE.md`. Sections get extracted **on demand**, one at a time, and cached forever. No bulk-dumping a book into context "to get familiar."

**Lessons that are actually nice to read.** One self-contained HTML file per lesson, dark-themed by house rule, Tufte-ish typography, generous whitespace, a comfortable measure. Not pure black (smears on OLED), not pure white text (halates), never colour-alone for state. You'll come back to these.

**Quizzes with a real feedback loop.** Retrieval quizzes built on a tiny dependency-free `quiz.js`. Options are matched in length and shape so formatting never leaks the answer. Every explanation cites its locator. Feedback carries a border *and* prose, not just green and red.

**Coverage is not learning.** Sections advance `unread` to `ingested` to `taught` to `practiced`, and `practiced` requires *evidence*: a quiz passed, an exercise worked, a correct answer given in conversation. Exposure doesn't count.

**Stateful across sessions.** The workspace is the memory. A returning session reads `MISSION.md`, `SOURCES.md`, the last two or three learning records, and `NOTES.md`, then starts warm without re-reading a single lesson or re-extracting a single section.

**A glossary in the author's own words.** The skill uses the source's vocabulary even where it would phrase things differently, and records the divergence when the field's standard term differs. Terms get promoted to `GLOSSARY.md` only once *you* can use them correctly.

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
|       `-- assets/
|           +-- lesson.css          <- the dark theme, single source of truth
|           `-- quiz.js             <- ~40 lines, no dependencies
|
+-- cowork/
|   `-- teach-from-source/          <- zip this folder, upload to Cowork
|       `-- ...                     <- identical, minus the two CLI-only keys
|
`-- scripts/
    +-- install-cli.sh              <- symlink or copy into ~/.claude/skills/
    `-- build-cowork-zip.sh         <- produce dist/teach-from-source.zip
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

## What you actually get

A learning workspace: one directory per course, yours, plain files, no lock-in.

```
~/LEARNING/ddia/
+-- MISSION.md                      # why you're reading this, and what "done" means
+-- SOURCES.md                      # the spine: what's ingested, coverage, gaps, conflicts
+-- GLOSSARY.md                     # the source's vocabulary, promoted only once you can use it
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

---

## Requirements

- **Claude Code CLI version:** Claude Code, plus as much of the extraction toolchain as you care to install. `poppler` and `git` get you most of the way; `pandoc`, `trafilatura`, `calibre`, and `yt-dlp` unlock EPUB, web, Kindle, and video respectively. See [docs/claude-code-cli.md](./docs/claude-code-cli.md).
- **Cowork version:** a Claude account with Cowork, and Claude Desktop if your sources are local files. Nothing to install, but read the sandbox toolchain table in [docs/claude-cowork.md](./docs/claude-cowork.md) before you point it at a Kindle file or a video.

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
