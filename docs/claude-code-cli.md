# Running `teach-from-source` in the Claude Code CLI

This is the version you want if your sources live on your own disk: a shelf of PDFs, an EPUB library, Kindle files, cloned repos. It runs locally, which means it gets the *full* extraction toolchain, and that toolchain is most of what makes the skill good.

**Time to first lesson:** about ten minutes, most of it Homebrew.

---

## Step 1: Check you have Claude Code

```bash
claude --version
```

No output? Install it first from [claude.com/claude-code](https://claude.com/claude-code), then come back.

---

## Step 2: Clone and install the skill

```bash
git clone https://github.com/Abhijit-17/teach-from-source.git
cd teach-from-source
./scripts/install-cli.sh
```

The script copies `claude-code/teach-from-source/` into `~/.claude/skills/teach-from-source/`. If you'd rather do it by hand, or you want a symlink so `git pull` updates the skill in place:

```bash
# Copy (stable; the skill won't change under you)
cp -R claude-code/teach-from-source ~/.claude/skills/

# ...or symlink (live; tracks the repo)
ln -s "$PWD/claude-code/teach-from-source" ~/.claude/skills/teach-from-source
```

Verify:

```bash
ls ~/.claude/skills/teach-from-source
# assets  GLOSSARY-FORMAT.md  INGESTION.md  LEARNING-RECORD-FORMAT.md
# MISSION-FORMAT.md  SKILL.md  SOURCE-MANIFEST-FORMAT.md  TOOLS.md
```

> **Personal vs. project scope.** `~/.claude/skills/` makes the skill available in every session on this machine, which is what you want here, since learning workspaces aren't tied to one repo. Dropping it in a project's `.claude/skills/` instead scopes it to that project only.

Restart `claude`, and `/teach-from-source` should appear in the slash-command menu.

---

## Step 3: Install the extraction toolchain

Here's the part worth doing properly.

The skill is CLI-native by design. `pdftotext -f 118 -l 133 -layout` pulls a 15-page range in milliseconds for essentially no context cost, and gives *better* text than the model reading those pages itself. Every binary you install is a source format that works well instead of a source format that limps.

None of it is mandatory, since the skill probes what's present and degrades deliberately. But the difference between "poppler installed" and "poppler missing" is the difference between a fast, faithful course and a slow, lossy one.

### The essentials

```bash
brew install poppler git ripgrep jq
```

| Package | Gives you | Why it matters |
|---|---|---|
| `poppler` | `pdftotext`, `pdfinfo`, `pdftoppm`, `pdfimages` | **The default PDF path.** `pdfinfo` runs first on every PDF to check for a text layer; `pdftotext` does the extracting; `pdfimages` pulls the book's figures at native resolution. |
| `git` | `git` | Repos as sources. `--depth 1`. |
| `ripgrep` | `rg` | How the model finds *which* extracted section says a thing, without reopening the book. |
| `jq` | `jq` | JSON API sources. |

### Strongly recommended

```bash
brew install mupdf-tools qpdf pandoc
```

| Package | Gives you | Why it matters |
|---|---|---|
| `mupdf-tools` | `mutool` | `mutool show book.pdf outline` returns a book's **real embedded TOC**. This is the single biggest quality win in the mapping phase; a real TOC beats parsing a printed one every time. Also a fallback text extractor. |
| `qpdf` | `qpdf` | Split, merge, repair, decrypt. `qpdf --pages book.pdf 40-72 -- ch4.pdf` carves out a chapter. |
| `pandoc` | `pandoc` | The universal converter. EPUB/HTML/DOCX/LaTeX/RST to clean Markdown. This is the EPUB path. |

> **Heads-up on conflicts:** `poppler` conflicts with `xpdf` and several other PDF toolkits in Homebrew, because they ship binaries with the same names. If `brew install poppler` complains, uninstall the conflicting formula rather than forcing the link. Take `poppler`; the skill's recipes are written against it.

### Per-format extras (install what matches your library)

```bash
# Web pages, articles, and docs sites: the default web path
pipx install trafilatura

# Kindle (.azw3/.mobi) and legacy ebook formats
brew install --cask calibre        # gives you ebook-convert + ebook-meta

# Lecture videos and playlists
brew install yt-dlp ffmpeg

# Scanned PDFs (OCR)
brew install tesseract tesseract-lang

# DOCX/PPTX/XLSX and other odd formats
pipx install markitdown
```

**On `calibre`:** the cask installs the app, but `ebook-convert` and `ebook-meta` are CLI binaries inside it. If they aren't on your `PATH` afterwards:

```bash
sudo ln -sf /Applications/calibre.app/Contents/MacOS/ebook-convert /usr/local/bin/
sudo ln -sf /Applications/calibre.app/Contents/MacOS/ebook-meta    /usr/local/bin/
```

**On `pipx`:** if you don't have it, `brew install pipx && pipx ensurepath`, then open a new shell. `pipx` keeps each Python CLI in its own venv, which avoids the "I upgraded one tool and broke three others" problem that plagues `pip install --user`.

**On `tesseract`:** only needed for *scanned* PDFs, meaning books with no text layer. Most modern PDFs have one. Skip it until you hit a scan; the skill will tell you when you have.

### Verify what landed

Run the skill's own probe. It's the same loop the skill runs on first ingestion:

```bash
for t in pdftotext pdfinfo mutool qpdf pandoc unzip ebook-convert \
         tesseract trafilatura yt-dlp jq rg git; do
  command -v "$t" >/dev/null && echo "ok   $t" || echo "MISS $t"
done
```

`MISS` lines are fine. They're a menu, not a failure. `MISS ebook-convert` just means "don't hand it a `.azw3` yet."

---

## Step 4: Create a workspace

**One directory per course.** The workspace *is* the state: mission, sources, lessons, coverage, and what you've actually learned all live as plain files inside it.

```bash
mkdir -p ~/LEARNING/ddia
cd ~/LEARNING/ddia
claude
```

> **Start `claude` from inside the workspace.** The skill treats the current directory as the workspace and will create files there. It's built to stop and ask if it finds an unrelated project instead, but don't rely on that. `cd` first.

Making it a git repo is worth thirty seconds. Lessons are HTML you'll iterate on, and being able to diff a rewritten lesson or recover one you deleted is genuinely useful:

```bash
git init && git commit --allow-empty -m "start: DDIA workspace"
```

---

## Step 5: Start the course

Invoke it explicitly. `disable-model-invocation: true` in the CLI build means Claude will never fire this at you on its own. A stateful, file-writing, multi-session teaching engine shouldn't launch because you said the word "teach" in passing.

Say two things: **the source** and **why you want it**.

```
/teach-from-source ~/books/ddia.pdf
I want to design a replication strategy I can defend in an architecture review.
```

The "why" matters more than it looks. "Learn SICP" and "pass my compilers exam" produce completely different lesson sequences from the same book. Vague missions get you a vague course, and the skill is instructed to interview you rather than accept one.

### Phrasings by medium

| Source | What to say |
|---|---|
| Local PDF / EPUB | `/teach-from-source ~/books/x.pdf I want to {goal}` |
| Kindle `.azw3` / `.mobi` | Same. Locally, `ebook-convert` handles it, and this is the one format the CLI does *much* better than Cowork. |
| Web article or paper | `/teach-from-source https://... teach me {goal}` |
| Docs site | `/teach-from-source https://docs.example.com enumerate the sitemap first and let's agree which sections matter` |
| Git repo | `/teach-from-source https://github.com/... I want to understand {subsystem} well enough to {goal}` |
| Lecture video / playlist | `/teach-from-source https://youtube.com/... pull the transcript and teach me {goal}` |
| Several at once | Name them all. One workspace can hold a textbook, three papers, and a lecture. Where they disagree, that disagreement becomes a lesson. |

Want tighter control over cadence, persona, or the challenge at the end of each
lesson? [example-prompts.md](./example-prompts.md) has a structured brief to adapt.

### What happens next

The first session ingests before it teaches:

1. **Acquire.** A stable local snapshot, and a short stable ID (`ddia`, `sicp`, `attention-paper`).
2. **Map.** The whole source at low resolution into `sources/<id>/OUTLINE.md`: units, locators, dependencies, and the **page offset** (printed page numbers and PDF page numbers almost never agree, and every later citation depends on getting this right).
3. **Register** it in `SOURCES.md` with provenance, coverage all-unread.
4. **Set up `assets/`.** `lesson.css` and `quiz.js` get copied into the workspace.
5. **Establish the mission.** You'll get interviewed here. Answer properly.
6. **Then** lesson `0001`.

Mapping a 600-page book takes a couple of minutes and pays for itself immediately: without the map, the skill can't judge what you're ready for and falls back to flat chapter order, which is rarely the right order.

---

## Step 6: Work through the course

Open a lesson:

```bash
open lessons/0001-*.html          # macOS
xdg-open lessons/0001-*.html      # Linux
```

Then, and this is the part people skip, **come back and talk about it.**

`quiz.js` writes results to your browser's `localStorage`, which Claude cannot read. Quiz results reach the skill through *conversation*. Being asked "how did the quiz go?" isn't the model failing to notice; it's the only channel that exists. Answer it, or re-answer a question directly in chat, and coverage moves from `taught` to `practiced`. Otherwise it doesn't, by design. Exposure isn't learning.

Useful things to say mid-course:

- *"Shorter lessons, more code."* lands in `NOTES.md` and applies from now on.
- *"I already know consistent hashing."* becomes a learning record, and stops being re-taught.
- *"Where does the book actually say that?"* should get you a locator every time. If it doesn't, that's a bug worth filing.
- *"Skip ahead to Chapter 9."* is fine, and it'll flag any prerequisites you're skipping over.

### Returning to a course

```bash
cd ~/LEARNING/ddia && claude
```

Then just: **"Continue."**

The skill re-reads `MISSION.md`, `SOURCES.md`, the last two or three learning records, and `NOTES.md`, and nothing else. It won't re-read old lessons or re-extract sections that already sit in `sources/<id>/sections/`. That's the whole point of the workspace files: a fresh session starts warm. Expect a one-line recap and a retrieval question from a previous lesson before the new material. That question *is* the spacing mechanism.

---

## Troubleshooting

**`/teach-from-source` doesn't appear in the menu**
Check `ls ~/.claude/skills/teach-from-source/SKILL.md` resolves, and that `SKILL.md` starts with a `---` frontmatter block whose `name:` is `teach-from-source`. Restart `claude`; the skill list is read at startup. If you symlinked, confirm the link isn't dangling (`ls -l ~/.claude/skills/`).

**Claude auto-invokes it when I didn't ask**
You're running the Cowork build. Check for `disable-model-invocation: true` in `~/.claude/skills/teach-from-source/SKILL.md`; if it's missing, you copied from `cowork/` instead of `claude-code/`.

**Lessons show `â€”` where an em dash belongs, and `Â·` where a middle dot belongs**
The lesson is missing its `<meta charset="utf-8">` first line. Opened over `file://` there's no `Content-Type` header to carry the encoding, so the browser falls back to a legacy single-byte encoding. The file is *valid* UTF-8 (`file -I` will happily confirm it), which is why the model can't see the problem and you can. Check and fix:

```bash
head -1 lessons/*.html | grep -c 'charset'
```

Tell Claude, and it'll repair every affected file. This is a known trap the skill is explicitly written to avoid; report it if it recurs.

**Lessons look unstyled**
`assets/lesson.css` didn't get copied on init. Ask Claude to run the asset-resolution step again, or copy it yourself:

```bash
mkdir -p assets && cp ~/.claude/skills/teach-from-source/assets/* ./assets/
```

**PDF extraction returns nothing**
It's a scan with no text layer. Confirm with `pdfinfo book.pdf` and a one-page `pdftotext` test. Install `tesseract`, or let the skill fall back to reading pages visually in narrow ranges. Either way it'll mark the source OCR-derived in `SOURCES.md`, and you should treat quoted numbers, symbols, and code from it with real suspicion, because that's exactly what OCR mangles.

**Kindle file won't convert**
Two possibilities. If `command -v ebook-convert` comes back empty, install Calibre (above). If conversion errors on DRM, the skill will stop and ask you for a DRM-free copy. It won't attempt to strip DRM, and neither should you here.

**A course is eating my context window**
That's not supposed to happen. The whole ingestion design exists to prevent it. Symptoms of a specific failure: bulk extraction into stdout instead of into files, or re-reading `sources/<id>/raw/` instead of `sources/<id>/sections/`. Say *"you're re-reading the raw source; use the cached sections."* If it happens repeatedly, file an issue with what it was doing, because that's a real skill bug.

**I want to move a course to Cowork**
Just move the workspace directory somewhere Claude Desktop can reach and continue there. The layout is identical across both versions; the files are the handoff. See [claude-cowork.md](./claude-cowork.md).

---

## Updating

Symlinked:

```bash
cd /path/to/teach-from-source && git pull
```

Copied:

```bash
cd /path/to/teach-from-source && git pull && ./scripts/install-cli.sh
```

Existing workspaces are unaffected, and that's deliberate: **`assets/lesson.css` in a workspace is canonical for that workspace.** Once a course has evolved its own components, an update won't overwrite them. If you want a workspace to pick up an improved stylesheet, copy it in yourself, on purpose.

---

## Uninstalling

```bash
rm -rf ~/.claude/skills/teach-from-source
```

Your workspaces under `~/LEARNING/` are untouched. They're plain Markdown and HTML, and they keep working forever. That's the point.
