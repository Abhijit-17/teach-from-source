# Toolchain

This skill is **CLI-native**. Shelling out to a real extractor is faster, cheaper in context, and more faithful than reading pages into the model. Prefer a tool; fall back to the `Read` tool only when no tool fits (scanned pages you must *see*, diagram interpretation, layout judgement).

Check availability before using anything: `command -v pdftotext`. Never assume, never ask the user to install mid-lesson. Degrade to `Read` and note it in `SOURCES.md`.

## Installed and verified

| Tool | Use it for |
|---|---|
| `pdftotext` | **The default PDF path.** `-f N -l M -layout file.pdf -` extracts a page range to stdout. Orders of magnitude cheaper than reading pages. |
| `pdfinfo` | Page count, title, whether the PDF has a text layer. Run this first on every PDF. |
| `pdftoppm` | Render a page to PNG, for figures or to feed OCR. |
| `pdfimages` | Pull embedded figures out at native resolution for lessons. |
| `mutool` | `mutool draw -F txt`, and `mutool show file.pdf outline` for a **real TOC** when one is embedded. Try this before hand-mapping. |
| `qpdf` | Split, merge, repair, decrypt. `qpdf --pages file.pdf 40-72 -- out.pdf` to carve a chapter. |
| `pandoc` | The universal converter. HTML/EPUB/DOCX/LaTeX/RST → Markdown. `pandoc -t markdown --wrap=none`. |
| `tesseract` | OCR for scanned PDFs, with `tesseract-lang` for non-English. Pair with `pdftoppm -r 300`. |
| `trafilatura` | **The default web path.** Extracts article text from a URL, stripping nav/ads/boilerplate. `trafilatura -u URL --markdown`. Also does sitemap crawls. |
| `ebook-convert` | **Kindle and legacy ebook formats.** `.azw3`/`.mobi`/`.lit`/`.fb2`/`.pdb` → EPUB, which you then unpack normally. Also the fastest whole-book text dump: `ebook-convert in.azw3 out.txt`. |
| `ebook-meta` | Title, author, language, ISBN from any ebook. Fills the `SOURCES.md` entry without guessing. |
| `markitdown` | Fallback converter for DOCX/PPTX/XLSX and odd formats. |
| `yt-dlp` | Video/audio sources. `--write-auto-sub --skip-download` gets a **transcript with timestamps**, which are locators for free. |
| `ffmpeg` | Audio extraction and segmenting when you must transcribe yourself. |
| `unzip` | EPUB is a ZIP. Also DOCX, PPTX. |
| `jq`, `rg` | JSON APIs and searching extracted text. `rg` is how you find which section says a thing. |
| `git` | Cloning a repo or docs site as a source. Shallow: `--depth 1`. |

**The table above describes a well-provisioned Claude Code host. It is not a guarantee.** This skill also runs on hosts with a different toolchain: Cowork sessions execute in an isolated cloud sandbox, and other harnesses vary. Never assume a binary exists because it is listed here.

**Probe once, at the start of the first ingestion in a workspace**, and record the result in `SOURCES.md` so later sessions don't re-probe:

```
for t in pdftotext pdfinfo mutool qpdf pandoc unzip ebook-convert \
         tesseract trafilatura yt-dlp jq rg git; do
  command -v "$t" >/dev/null && echo "ok   $t" || echo "MISS $t"
done
```

Then degrade deliberately, in this order:

1. **A different CLI tool for the same job.** No `pdftotext`? Try `mutool draw -F txt`. No `pandoc` for an EPUB? The unpacked XHTML is readable, and `rg`/`sed` can strip tags. No `trafilatura`? Fetch the page with whatever fetch tool the host gives you.
2. **The host's own fetch/convert tooling** where the CLI is absent but a native tool exists.
3. **The `Read` tool**, on a narrow range only, never a whole book.

Whatever you land on, **write which tool produced each section file into that file's header**, and note the degradation in `SOURCES.md`. A future session must be able to tell a `pandoc` extraction from a hand-stripped one, because the second is lossier and quotes from it deserve more suspicion.

Never block a lesson on an install, and never ask the user to install something mid-lesson.

## Recipes

**Map a PDF's real outline**
```
pdfinfo book.pdf
mutool show book.pdf outline 2>/dev/null || pdftotext -f 1 -l 20 -layout book.pdf -
```

**Extract one section**
```
pdftotext -f 118 -l 133 -layout book.pdf - > sources/<id>/sections/ch04-p118-133.md
```

**Scanned page → text**
```
pdftoppm -r 300 -f 118 -l 118 -png book.pdf /tmp/pg && tesseract /tmp/pg-118.png - 2>/dev/null
```

**Kindle format → workable EPUB (then map it normally)**
```
ebook-meta book.azw3                             # title/author for SOURCES.md
ebook-convert book.azw3 sources/<id>/raw/book.epub
unzip -q sources/<id>/raw/book.epub -d sources/<id>/raw/unpacked/
```
DRM-free files only. If conversion errors out on DRM, say so and ask the user for an unencumbered copy. Do not attempt to strip it.

**EPUB → per-chapter Markdown**
```
unzip -q book.epub -d sources/<id>/raw/
pandoc sources/<id>/raw/OEBPS/ch04.xhtml -t markdown --wrap=none
```

**Web article**
```
trafilatura -u "https://..." --markdown --with-metadata
```

**Docs site / multi-page**
```
trafilatura --sitemap "https://docs.example.com/" --list          # enumerate first
trafilatura -u "<one url>" --markdown                              # then fetch chosen pages
```

**Video lecture transcript**
```
yt-dlp --write-auto-sub --sub-format vtt --skip-download -o 'sources/<id>/raw/%(title)s' URL
```

**Repo as source**
```
git clone --depth 1 URL sources/<id>/raw/
```

**API / JSON source**
```
python3 -c "import urllib.request,sys; sys.stdout.write(urllib.request.urlopen(sys.argv[1]).read().decode())" URL > sources/<id>/raw/resp.json
jq . sources/<id>/raw/resp.json | head -40
```
(Print the raw bytes. Do not `print(json.load(...))`, which emits a Python dict repr that `jq` cannot parse.)

## Rules

- **Redirect to a file, don't print a book to stdout.** Extract to `sources/<id>/sections/`, then read that file. A bare `pdftotext ... -` on 200 pages floods context exactly as badly as reading it would.
- **Check for a text layer first.** `pdfinfo` plus a one-page `pdftotext` test. If it comes back empty, it is a scan, so switch to the OCR path and say so.
- **Pipe through `head`/`rg` when exploring.** Full dumps only into files.
- **Record which tool produced a section file** in its header. If extraction was lossy, the next session needs to know.
