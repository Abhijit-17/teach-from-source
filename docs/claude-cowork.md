# Running `teach-from-source` in Claude Cowork

This is the version you want if you'd rather not install a toolchain, or you want to pick a course up from a laptop that isn't the one your books are on. It's the same skill, with the same lessons, citations, and workspace layout, running in Cowork's cloud sandbox instead of on your machine.

**Time to first lesson:** about five minutes. There's nothing to compile.

There *is* one thing to understand before you start, and it's the difference between a smooth course and a frustrating one. It's in [Step 4](#step-4-understand-the-sandbox-and-where-it-bites). Read that bit.

---

## Step 1: Get the upload bundle

Cowork takes a skill as a `.zip` containing a **single top-level folder** with `SKILL.md` inside it. The layout matters. A zip of loose files, or one with an extra wrapping directory, won't be recognised.

### Option A: Download it (no clone, no terminal)

Grab `teach-from-source.zip` from the [**latest release**](https://github.com/Abhijit-17/teach-from-source/releases/latest). It's already in the right shape, so skip to [Step 2](#step-2-upload-the-skill-to-cowork).

> **Do not use GitHub's green "Code -> Download ZIP" button for this.** It gives you `teach-from-source-main.zip`, which wraps everything in a `teach-from-source-main/` folder and puts `SKILL.md` three levels deep, under `cowork/teach-from-source/`. Cowork will reject it. Use the release asset, or build it yourself below.

### Option B: Build it from source

```bash
git clone https://github.com/Abhijit-17/teach-from-source.git
cd teach-from-source
./scripts/build-cowork-zip.sh
# -> dist/teach-from-source.zip
```

The built zip is deliberately **not** committed to the repo. It would go stale the moment `SKILL.md` changed, and a silently outdated skill is a nasty bug to chase. The script rebuilds it from source every time and checks the two builds haven't drifted.

By hand, if you prefer:

```bash
cd cowork
zip -r ../dist/teach-from-source.zip teach-from-source -x '*.DS_Store'
```

Confirm the shape before uploading:

```bash
unzip -l dist/teach-from-source.zip
```

```
teach-from-source/
teach-from-source/SKILL.md              <- must be exactly one level deep
teach-from-source/INGESTION.md
teach-from-source/TOOLS.md
teach-from-source/MISSION-FORMAT.md
teach-from-source/SOURCE-MANIFEST-FORMAT.md
teach-from-source/GLOSSARY-FORMAT.md
teach-from-source/LEARNING-RECORD-FORMAT.md
teach-from-source/assets/lesson.css
teach-from-source/assets/quiz.js
```

> **Zip the `cowork/` build, not `claude-code/`.** The CLI build carries `disable-model-invocation: true` and `argument-hint` in its frontmatter. Cowork doesn't read either key, so they're harmless. But `disable-model-invocation` is a Claude Code concept, and shipping frontmatter to a host that doesn't implement it is exactly the kind of drift that makes a skill mysterious six months later. The script picks the right one for you.
>
> **Zip on macOS?** Use the `zip` CLI or the script, not Finder's *Compress*. Finder adds a `__MACOSX/` sidecar directory that some uploaders choke on.

---

## Step 2: Upload the skill to Cowork

In Claude Desktop or claude.ai:

1. **Settings -> Skills**
2. **Add -> Upload skill**
3. Pick `dist/teach-from-source.zip`.
4. It should list as **`teach-from-source`**, described as teaching a topic grounded in sources you point at.

If the upload is rejected, it's almost always the zip shape. Re-run the `unzip -l` check above: `SKILL.md` must be exactly one directory deep, and there must be exactly one top-level folder.

---

## Step 3: Set your global instructions

This is the step that does the most work for the least effort, so don't skip it.

The CLI build uses `disable-model-invocation: true` to make sure a stateful, multi-session teaching engine only ever starts when you ask for it. Cowork has no equivalent frontmatter key, so you get the same deliberateness from a standing instruction instead.

Paste this into **[Settings -> Cowork -> Global instructions](https://claude.ai/settings/cowork)**:

> I use the `teach-from-source` skill for structured learning workspaces under `~/Downloads/LEARNING/`. In those folders, always read `MISSION.md`, `SOURCES.md`, `NOTES.md`, and any `*-HANDOFF.md` before doing anything else. Never advance a chapter or unit without my explicit confirmation. Teach ground-up, but bridge fast into trade-offs, bottlenecks, and failure modes. Sources come in every format: PDF, EPUB, Kindle, web pages, docs sites, repos, papers, lecture videos, APIs. Pick the acquisition path from `INGESTION.md` that fits the medium; never assume the source is a book.

**Make it yours.** Four things are worth editing:

| Clause | Change it to |
|---|---|
| `~/Downloads/LEARNING/` | Wherever your workspaces actually live. |
| *"never advance without explicit confirmation"* | **Keep this one.** It's what stops a session running four chapters ahead of you while you're reading lesson one. |
| *"teach ground-up, but bridge fast into trade-offs..."* | Your depth preference. Someone ten years in and someone in their first job want genuinely different lessons from the same page. |
| **Add a sentence about your background** | Optional, and the highest-leverage thing in the whole instruction. Something like *"I've written production Go for years but have never touched distributed consensus"* tells the skill exactly where your floor is, so it stops explaining what you know and starts explaining what you don't. |

> **A note on what you put here.** This instruction is yours and stays private, but people do paste theirs into issues and blog posts when asking for help. Keep it about what you *know*, not where you work or what you're angling for.

---

## Step 4: Understand the sandbox, and where it bites

Here's the thing worth internalising.

**Cowork runs shell commands in an isolated cloud environment on Anthropic's servers, not on your Mac.** Your local files are reached through the Claude Desktop app, but the *tools that parse them* are whatever the sandbox happens to ship. And this skill leans hard on real extractors.

Formats that need a specialist binary are the ones that can fail:

| Source | Needs | Risk in the sandbox | What happens instead |
|---|---|---|---|
| **EPUB** | `unzip`, `pandoc` | **Lowest.** An EPUB is a ZIP, and `toc.ncx` is a reliable map. | Even with no `pandoc`, the unpacked XHTML is readable and tag-strippable. Never blocked. |
| **PDF (text layer)** | `pdftotext`, `pdfinfo` | **Low** | `mutool draw -F txt`; failing that, narrow-range reads. |
| **Repo** | `git` | **Low** | (nothing to fall back to) |
| **Web page / docs site** | `trafilatura` | **Medium.** Network access follows your egress settings, but the extractor may be absent. | Any available fetch tool, then boilerplate stripped by hand. The degradation gets noted. |
| **PDF (scanned)** | `pdftoppm` + `tesseract` | **High.** OCR stacks are rarely present. | Pages get read visually in small ranges. The source is marked OCR-derived, and quoted numbers, symbols, and code are treated as suspect. |
| **Video / lecture** | `yt-dlp` | **High** | See below. Do this locally. |
| **Kindle `.azw3` / `.mobi`** | `ebook-convert` (Calibre) | **Highest.** Calibre in a sandbox is very unlikely. | See below. Do this locally. |

### The rule that makes all of this go away

**For the two highest-risk formats, Kindle and video, do the acquisition step on your own machine and hand Cowork the result.**

```bash
# Kindle -> EPUB (DRM-free files only)
ebook-convert ~/books/ddia.azw3 ~/Downloads/LEARNING/ddia/ddia.epub

# Lecture -> timestamped transcript
yt-dlp --write-auto-sub --sub-format vtt --skip-download \
       -o '~/Downloads/LEARNING/mit-6824/%(title)s' 'https://youtube.com/...'
```

One command each. Everything downstream of acquisition is plain-text parsing, which travels perfectly, so this removes the sandbox from the equation entirely for exactly the cases where it's shakiest. An EPUB and a `.vtt` are both boringly portable, and the `.vtt` timestamps become your locators for free.

### Probe once, record the answer

The skill is instructed to probe the toolchain **once per workspace**, before the first ingestion, and write the result into `SOURCES.md` so later sessions don't waste a turn re-probing:

```bash
for t in pdftotext pdfinfo mutool qpdf pandoc unzip ebook-convert \
         tesseract trafilatura yt-dlp jq rg git; do
  command -v "$t" >/dev/null && echo "ok   $t" || echo "MISS $t"
done
```

If you want to know what you're working with before committing to a source, just ask Cowork to run it in a new session. Sandbox images change over time, so don't trust a result from three months ago.

---

## Step 5: Connect a workspace folder

**One folder per course.** The folder *is* the state: mission, sources, lessons, coverage, and what you've actually learned, all as plain files.

```bash
mkdir -p ~/Downloads/LEARNING/ddia
```

Move or copy the source into it, or for the risky formats the *converted* source from Step 4, then connect that folder in Cowork.

Keeping every course under one parent (`~/Downloads/LEARNING/`) is what makes the global instruction from Step 3 fire reliably. Match the path in the instruction to the path you actually use.

---

## Step 6: Start the course

Say **what you have** and **what you want out of it**. The phrasing doesn't change by medium, because the skill dispatches on that itself:

| Source | What to say |
|---|---|
| Local PDF / EPUB | "Use teach-from-source on `~/Downloads/LEARNING/ddia/ddia.pdf`. I want to be able to {goal}." |
| Web article or paper | "Use teach-from-source on {URL}. Teach me {goal}." |
| Docs site | "Use teach-from-source on {URL}. Enumerate the sitemap first and let's agree which sections matter." |
| Repo | "Use teach-from-source on {git URL}. I want to understand {subsystem} well enough to {goal}." |
| Lecture transcript | "Use teach-from-source on the `.vtt` in this folder. Teach me {goal}." |
| Several at once | Name them all. One workspace can hold a textbook, three papers, and a lecture; where they conflict, that conflict becomes teaching material. |

**The one thing always worth stating is *why*.** "I want to pass X." "I want to rebuild Y at work." "I want to defend this decision in a review." The mission drives lesson sequencing far more than the source's own chapter order does, and a vague mission gets you a vague course.

For tighter control over cadence, persona, or the challenge at the end of each
lesson, [example-prompts.md](./example-prompts.md) has a structured brief to adapt.

### What the first session does

1. **Probe** the sandbox toolchain, and record it in `SOURCES.md`.
2. **Acquire.** A stable snapshot, and a short stable ID (`ddia`, `sicp`, `raft-paper`).
3. **Map.** The whole source, cheaply, once, into `sources/<id>/OUTLINE.md`: units, locators, dependencies, and the **page offset** (printed and PDF page numbers almost never agree, and every citation afterwards depends on it).
4. **Register** it in `SOURCES.md` with provenance and fetch date.
5. **Set up `assets/`.** `lesson.css` and `quiz.js` land in the workspace. If the host didn't expose the skill as files, Claude writes them from the contracts in `SKILL.md` instead; an unstyled workspace is a worse failure than a slow one.
6. **Establish the mission.** Expect to be interviewed. Answer properly.
7. **Then** lesson `0001`.

---

## Step 7: Work through the course

Lessons are self-contained HTML in `lessons/`. Open them from the connected folder in your browser.

Then come back and talk about them.

> ### The browser is a dead end
>
> `quiz.js` logs your answers to `localStorage`. **Claude cannot read `localStorage`**,
> and connecting the folder does not change that - the file is on your machine, the
> browser storage is not in the folder at all.
>
> Report the substance in the chat: `Lesson 1 quiz: Q1 b, Q2 c, Q3 b. Hesitated on Q3.`
> "I did the quiz" is a report of activity, not understanding, and the skill is
> instructed not to accept it as evidence.

Being asked "how did the quiz go?" is the mechanism, not an oversight. Answer, and coverage moves from `taught` to `practiced`. Stay quiet, and it doesn't. Exposure isn't learning.

The same holds for anything done away from the chat: exercises on paper, a technique tried in a real meeting, a chapter read ahead. Reporting a *wrong* answer is worth more than a right one, because a corrected misconception is the highest-value thing the skill can record about you. See [the README section on this](../README.md#the-one-thing-that-will-silently-stall-your-course).

Because of the global instruction, the skill will pause for confirmation before advancing a chapter. Use those pauses:

- *"Not yet. Re-test me on the last one first."*
- *"I already know Raft; skip the consensus recap."* becomes a learning record, and stops being re-taught.
- *"Shorter lessons, more diagrams."* lands in `NOTES.md` and applies from here on.
- *"Where does the book actually say that?"* should get you a locator every single time.

### Returning to a course

Reconnect the folder and say **"Continue."**

The skill re-reads `MISSION.md`, `SOURCES.md`, the last two or three learning records, and `NOTES.md`, and deliberately nothing else. It won't re-read old lessons or re-extract cached sections. Expect a one-line recap and a retrieval question from earlier material; that question is the spacing mechanism, not small talk.

---

## Troubleshooting

**The skill doesn't trigger**
Name it: *"Use the teach-from-source skill on..."*. Then check the folder path in your global instruction matches the folder you actually connected, because that mismatch is the usual culprit.

**Upload rejected**
Zip shape. `SKILL.md` must sit exactly one directory deep, under a single top-level folder, with no `__MACOSX/` sidecar. Re-run `./scripts/build-cowork-zip.sh` and check with `unzip -l`.

**Lessons render as `â€”` and `Â·`**
Missing `<meta charset="utf-8">` on line one. Over `file://` there's no `Content-Type` header to carry the encoding, so the browser falls back to a legacy single-byte one. The file is valid UTF-8, which is why the model can't see it and you can. Tell Claude; it'll fix every affected file. The skill is explicitly written to prevent this, so it's worth reporting if it recurs.

**Lessons look unstyled**
`assets/lesson.css` didn't make it into the workspace, most likely because the host didn't expose the skill's files for copying. Ask Claude to write `assets/lesson.css` and `assets/quiz.js` from the contracts in `SKILL.md`; it's instructed to do exactly that as a fallback.

**"I can't extract this PDF"**
Either there's no text layer (a scan, so expect the OCR-derived warning and distrust quoted numbers and code), or `pdftotext` is absent from the sandbox. Run the probe. If poppler is genuinely missing, converting to EPUB locally and handing that over is the reliable path.

**Kindle file failed**
Expected, because `ebook-convert` almost certainly isn't in the sandbox. Convert to EPUB on your own machine (Step 4) and hand over the EPUB. DRM-free only; the skill won't attempt to strip DRM.

**Web fetch returns navigation chrome instead of the article**
`trafilatura` is missing and the fallback fetch didn't strip boilerplate cleanly. Say so, and the skill will strip it by hand and record the degradation in `SOURCES.md`. That's what you want, because a hand-stripped extraction is lossier and its quotes deserve more suspicion.

**It advanced without asking**
Your global instruction isn't set, or got edited. Re-paste Step 3, keeping the *"never advance without my explicit confirmation"* clause verbatim.

---

## Moving between Cowork and the CLI

Both versions produce **identical workspace layouts**: `MISSION.md`, `SOURCES.md`, `GLOSSARY.md`, `NOTES.md`, `sources/`, `lessons/`, `reference/`, `learning-records/`. There's no export step, because there's no proprietary state. The files *are* the handoff.

- **Cowork to CLI:** point `claude` at the folder and say *"Continue."*
- **CLI to Cowork:** move the folder somewhere Claude Desktop can reach and connect it.

A sensible split, if you want one: do the **big local ingestion** in the CLI, where the full toolchain lives (Kindle conversion, OCR, video transcripts, 900-page PDFs), and do the **teaching sessions** in Cowork, from whatever device you're on. Once a source is extracted into `sources/<id>/sections/`, it's plain Markdown, and the sandbox never has to touch the original again.

---

## Updating the skill

Rebuild and re-upload:

```bash
cd /path/to/teach-from-source && git pull && ./scripts/build-cowork-zip.sh
```

Then re-upload it under **Settings -> Skills -> Add -> Upload skill**, replacing the existing `teach-from-source`.

Existing workspaces are unaffected, and that's deliberate. **`assets/lesson.css` in a workspace is canonical for that workspace.** A course that has grown its own components won't get them overwritten by an update. If you want a workspace on a newer stylesheet, copy it in yourself, on purpose.
