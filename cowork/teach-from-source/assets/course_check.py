#!/usr/bin/env python3
# course_check.py 1.1.0
"""Check teach-from-source Course material before a lesson is announced.

Usage, from the workspace root:
    python3 assets/course_check.py [FILE ...]

With no FILE, checks lessons/*.html, reference/*.html and GLOSSARY.md.
Old lesson copies (NNNN-name.vX.Y.Z.html) are always skipped, with a count
on stderr: they were written under earlier rules.
Prints one finding per line as `file:line: [rule] message` and exits 1 when
there are any. One line on stderr says which STE mode ran.

Checks:
  charset    every .html file declares <meta charset="utf-8"> on line 1
  STE        Part 1 limits: sentence length (20 words in .steps, 25 elsewhere),
             6 sentences per paragraph, no semicolons, no contractions.
             The word check (Approved words plus GLOSSARY.md terms) runs only
             when the STE folder holds both PERMISSION.md and
             approved-words.tsv. Otherwise this is Rules-only mode.
  fp         every section.fp has the five fp-* steps, in order, as children
  gap        every .gap starts with the fixed Outside-the-source line
  illustration
             every .illustration starts with the fixed Illustration line
  quote      every inline source quote <q> has a .cite citation in the same
             paragraph or list item
  explain    every quiz .explain (an answer, so a claim) holds a .cite or a .gap
  cite       every .cite is a link (<a href>). Only a link counts as a citation
  recall     every .recall-check has a link to a lesson and a <details> answer
  lesson-ref every "Lesson NNNN" outside Exempt text, and every link to
             NNNN-*.html, names a lesson file that exists. Refer to a future
             lesson by its topic
  components a lesson that uses a skill component (.fp, .recall,
             .recall-check, .illustration) links assets/components.css,
             and links it before lesson.css
  glossary   every GLOSSARY.md entry has a _Source_: line that is a locator
             (a [...] citation or a link) or exactly
             "Outside-the-source (Gap: <name>)", where <name> is the bold name
             of a Gap under ## Gaps in SOURCES.md (a trailing . or : is
             ignored). Only terms with a valid line count as
             Technical nouns and verbs (ADR 0002)

Exempt text (blockquote, q, cite, code, pre, .cite, .math, .name) is not checked
but counts as one word in its sentence. A script cannot judge meaning, voice
or one-topic-per-sentence: the agent reviews those after this runs clean.

The STE folder is ./ste100/, else ~/.claude/ste100/. approved-words.tsv has
one row per approved word form: word<TAB>part of speech<TAB>approved meaning.
Lines starting with # are comments. Python 3 standard library only.
"""

import argparse
import re
import sys
from bisect import bisect_right
from collections import namedtuple
from html.parser import HTMLParser
from pathlib import Path

VERSION = "1.1.0"

Finding = namedtuple("Finding", "file line rule message")

PROCEDURAL_MAX = 20   # STE 5.1
DESCRIPTIVE_MAX = 25  # STE 6.3
PARAGRAPH_MAX = 6     # STE 6.6

GAP_LINE = "Outside the source: not from your registered sources. Logged as a Gap."
ILLUSTRATION_LINE = ("Illustration: the sources applied to your project, or shown through "
                     "an analogy. Not a claim from the sources.")
BOX_LINES = {"gap": GAP_LINE, "illustration": ILLUSTRATION_LINE}  # class -> fixed first line
FP_STEPS = ("fp-problem", "fp-truths", "fp-buildup", "fp-name", "fp-test")
COMPONENT_CLASSES = {"fp", "recall", "recall-check", "illustration"}  # styled by components.css
FP_LABELS = {"Problem", "Ground truths", "Build-up", "Name", "Foundation test"}

EXEMPT_TAGS = {"blockquote", "q", "cite", "code", "pre"}
EXEMPT_CLASSES = {"cite", "math", "name"}
SKIP_TAGS = {"head", "title", "script", "style", "template"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "source", "track", "wbr"}
BLOCK_TAGS = {"p", "li", "td", "th", "dd", "dt", "figcaption", "caption",
              "h1", "h2", "h3", "h4", "h5", "h6", "div", "section", "article",
              "aside", "header", "footer", "nav", "main", "figure", "ul", "ol",
              "dl", "table", "thead", "tbody", "tr", "details", "summary",
              "blockquote", "pre", "body", "html", "button", "label", "option"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

EXEMPT_MARK = "\ue000"  # stands in for one span of Exempt text
GROUP_MARK = "\ue001"   # stands in for one parenthetical or quotation

UNITS = {"ms", "s", "us", "\u00b5s", "ns", "min", "h", "b", "kb", "mb", "gb", "tb",
         "kib", "mib", "gib", "bytes", "mm", "cm", "m", "km", "g", "kg", "%",
         "hz", "khz", "mhz", "ghz", "rpm"}
NUMBER = re.compile(r"^[\d.,/%:+-]+$")
SENTENCE_END = re.compile(r"[.!?][\"\u201d\u2019)\]]*(?=\s|$)")
CONTRACTION = re.compile(
    r"\b\w+n[\u2019']t\b|\b\w+[\u2019'](?:re|ll|ve|m|d)\b|\b(?:it|that|there|what|here|who)[\u2019']s\b",
    re.IGNORECASE)
WORD = re.compile(r"[A-Za-z][A-Za-z\u2019'-]*")
LESSON_NUMBER = re.compile(r"\blessons?\s+(\d{1,4})\b", re.IGNORECASE)
LESSON_FILE = re.compile(r"^\d{4}-[^/]+\.html$")
OLD_COPY = re.compile(r"\.v\d+\.\d+\.\d+\.html$")


def is_old_copy(path):
    return bool(OLD_COPY.search(Path(path).name))


def is_lesson_link(href):
    return bool(LESSON_FILE.match(Path(href.split("#", 1)[0].split("?", 1)[0]).name))


# --- word count (STE 8.4-8.7) ------------------------------------------------

def count_words(text):
    """Count words in one sentence the STE way.

    A parenthetical, a quotation, a span of Exempt text, a number with its
    unit, and a hyphenated word each count as one word.
    """
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\([^()]*\)", f" {GROUP_MARK} ", text)
    text = re.sub(r"\u201c[^\u201d]*\u201d|\"[^\"]*\"", f" {GROUP_MARK} ", text)
    tokens = [t for t in text.split() if re.search(r"\w|[\ue000\ue001]", t)]
    count, i = 0, 0
    while i < len(tokens):
        count += 1
        bare = tokens[i].strip(".,:!?")
        if NUMBER.match(bare) and i + 1 < len(tokens) \
                and tokens[i + 1].strip(".,:!?").lower() in UNITS:
            i += 1
        i += 1
    return count


def split_sentences(text):
    """Yield (start offset, sentence) for each sentence in a block of text."""
    start = 0
    for m in SENTENCE_END.finditer(text):
        yield start, text[start:m.end()]
        start = m.end()
    if text[start:].strip():
        yield start, text[start:]


# --- STE dictionary ----------------------------------------------------------

def find_ste_dir(workspace, home):
    """Return the STE folder: ./ste100/ in the workspace first, then ~/.claude/ste100/."""
    for d in (Path(workspace) / "ste100", Path(home) / ".claude" / "ste100"):
        if d.is_dir():
            return d
    return None


def load_dictionary(ste_dir):
    """Return (approved words or None, mode line)."""
    rules_only = "STE: writing rules only, dictionary not checked"
    if ste_dir is None:
        return None, f"{rules_only} (no STE dictionary folder found)"
    if not (ste_dir / "PERMISSION.md").is_file():
        return None, f"{rules_only} (no PERMISSION.md in {ste_dir})"
    tsv = ste_dir / "approved-words.tsv"
    if not tsv.is_file():
        return None, f"{rules_only} (no approved-words.tsv in {ste_dir})"
    words = set()
    for line in tsv.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            words.add(line.split("\t")[0].strip().lower())
    return words, f"STE: writing rules and dictionary ({tsv})"


class GlossaryEntry:
    def __init__(self, term, line):
        self.term, self.line = term, line
        self.definition = []  # (line number, text)
        self.source = None    # the _Source_: locator




def parse_glossary(path):
    """Yield one GlossaryEntry per **Term**: heading.

    source stays None when the entry has no _Source_: locator.
    """
    entry = None
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"^\*\*(.+?)\*\*:\s*$", line)
        if m or line.startswith("#"):
            if entry:
                yield entry
            entry = GlossaryEntry(m.group(1), n) if m else None
        elif entry is None:
            continue
        elif line.startswith("_Source_:"):
            entry.source = line[len("_Source_:"):].strip() or None
        elif line.strip() and not line.startswith("_"):
            entry.definition.append((n, line))
    if entry:
        yield entry


LOCATOR = re.compile(r"\[[^\]]+\]|https?://")
OUTSIDE_SOURCE = re.compile(r"^Outside-the-source \(Gap: (.+)\)$")


def gap_name(text):
    """A Gap name for matching: a trailing period or colon is not part of it."""
    return text.strip().rstrip(".:").strip()


def gap_names(workspace):
    """The bold names of the items under ## Gaps in SOURCES.md."""
    path = Path(workspace) / "SOURCES.md"
    if not path.is_file():
        return set()
    names, in_gaps = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_gaps = line.strip() == "## Gaps"
        elif in_gaps:
            m = re.match(r"^- \*\*(.+?)\*\*", line)
            if m:
                names.add(gap_name(m.group(1)))
    return names


def source_problem(entry, gaps):
    """Why an entry's _Source_: line does not count, or None when it does."""
    if not entry.source:
        return f"'{entry.term}' has no _Source_: locator line"
    m = OUTSIDE_SOURCE.match(entry.source)
    if m:
        if gap_name(m.group(1)) not in gaps:
            return (f"'{entry.term}' names Gap '{gap_name(m.group(1))}', "
                    "which is not under ## Gaps in SOURCES.md")
        return None
    if not LOCATOR.search(entry.source):
        return (f"'{entry.term}': _Source_: {entry.source!r} is not a locator. "
                "Use a [...] citation, a link, or Outside-the-source (Gap: <name>)")
    return None


def glossary_terms(workspace):
    """Words of every GLOSSARY.md term with a valid _Source_: line (ADR 0002)."""
    path = Path(workspace) / "GLOSSARY.md"
    if not path.is_file():
        return set()
    gaps = gap_names(workspace)
    terms = set()
    for e in parse_glossary(path):
        if source_problem(e, gaps) is None:
            terms.update(w.lower() for w in WORD.findall(e.term))
    return terms


# --- one block of checked text -------------------------------------------------

class Block:
    """Checked text from one block element, with a map back to source lines."""

    def __init__(self, tag, steps):
        self.tag, self.steps = tag, steps
        self.text, self.offsets, self.lines = "", [], []

    def add(self, text, line):
        self.offsets.append(len(self.text))
        self.lines.append(line)
        self.text += text

    def line_at(self, offset):
        i = max(bisect_right(self.offsets, offset) - 1, 0)
        if not self.lines:
            return 0
        return self.lines[i] + self.text[self.offsets[i]:offset].count("\n")


class Checker:
    def __init__(self, dictionary, terms):
        self.dictionary, self.terms = dictionary, terms
        self.known = (dictionary or set()) | terms

    def allowed(self, word):
        w = word.lower()
        if w in self.known:
            return True
        if any(w.endswith(s) and w[:-len(s)] in self.terms for s in ("s", "es")):
            return True
        return "-" in w and all(self.allowed(p) for p in w.split("-") if p)

    def check_block(self, path, block, findings):
        text = block.text
        for fixed in BOX_LINES.values():
            if text.strip().startswith(fixed):
                i = text.index(fixed)
                text = text[:i] + " " * len(fixed) + text[i + len(fixed):]
        if not re.search(r"\w", text):
            return
        heading = block.tag in HEADINGS

        for m in re.finditer(";", text):
            findings.append(Finding(path, block.line_at(m.start()), "STE 8.1",
                                    "semicolon: write two sentences"))
        for m in CONTRACTION.finditer(text):
            findings.append(Finding(path, block.line_at(m.start()), "STE 4.2",
                                    f"contraction '{m.group()}': write it in full"))

        sentences = [(o, s) for o, s in split_sentences(text) if count_words(s)]
        if not heading:
            limit, rule = ((PROCEDURAL_MAX, "STE 5.1") if block.steps
                           else (DESCRIPTIVE_MAX, "STE 6.3"))
            for offset, s in sentences:
                n = count_words(s)
                if n > limit:
                    lead = " ".join(s.replace(EXEMPT_MARK, "\u2026").split()[:8])
                    findings.append(Finding(path, block.line_at(offset), rule,
                                            f"sentence has {n} words (max {limit}): {lead} \u2026"))
            if block.tag == "p" and len(sentences) > PARAGRAPH_MAX:
                findings.append(Finding(path, block.line_at(0), "STE 6.6",
                                        f"paragraph has {len(sentences)} sentences "
                                        f"(max {PARAGRAPH_MAX})"))

        if self.dictionary is None or (heading and text.strip() in FP_LABELS):
            return
        for m in WORD.finditer(text):
            word = re.sub(r"[\u2019']s$|[\u2019']$", "", m.group()).strip("-")
            if not word or "'" in word or "\u2019" in word or self.allowed(word):
                continue
            findings.append(Finding(path, block.line_at(m.start()), "STE 1.1",
                                    f"'{word}' is not an Approved word or a GLOSSARY.md term"))


# --- HTML --------------------------------------------------------------------

class LessonParser(HTMLParser):
    """Splits a lesson into Blocks and checks structure and lesson references."""

    def __init__(self, path, checker, findings, lessons_dir):
        super().__init__(convert_charrefs=True)
        self.path, self.checker, self.findings = path, checker, findings
        self.lessons_dir = Path(lessons_dir)
        self.stack = []      # dicts: tag, classes, exempt, skip, steps, line
        self.blocks = []     # open Blocks, innermost last
        self.fp = []         # open fp sections: [line, step classes seen]
        self.gaps = []       # open .gap and .illustration boxes: [line, text, class]
        self.recalls = []    # open .recall-check elements: [line, link, answer]
        self.component_line = None   # first use of a COMPONENT_CLASSES class
        self.explains = []   # open .explain elements: [line, has .cite or .gap]
        self.components_linked = False
        self.lesson_css_linked = False

    def top(self, key):
        return self.stack[-1][key] if self.stack else False

    def flush(self):
        if self.blocks and self.blocks[-1].text:
            b = self.blocks[-1]
            self.checker.check_block(self.path, b, self.findings)
            self.blocks[-1] = Block(b.tag, b.steps)

    def handle_starttag(self, tag, attrs):
        classes = set((dict(attrs).get("class") or "").split())
        line = self.getpos()[0]
        if self.stack and "fp" in self.stack[-1]["classes"] \
                and self.stack[-1]["tag"] == "section":
            self.fp[-1][1].extend(c for c in classes if c in FP_STEPS)
        if tag == "a":
            self.check_link(dict(attrs).get("href") or "", line)
        sheet = Path(dict(attrs).get("href") or "").name if tag == "link" else ""
        if sheet == "lesson.css":
            self.lesson_css_linked = True
        if sheet == "components.css":
            self.components_linked = True
            if self.lesson_css_linked:
                self.findings.append(Finding(
                    self.path, line, "components",
                    "link components.css before lesson.css, so lesson.css can restyle a component"))
        if classes & COMPONENT_CLASSES and self.component_line is None:
            self.component_line = line
        cite = "cite" in classes
        if cite and not (tag == "a" and dict(attrs).get("href")):
            cite = False
            self.findings.append(Finding(self.path, line, "cite",
                                         ".cite must be a link: <a class=\"cite\" href=\"...\">"))
        for x in self.explains:
            x[1] = x[1] or cite or "gap" in classes
        if "explain" in classes:
            self.explains.append([line, False])
        if tag == "q" or cite:
            block = next((e for e in reversed(self.stack) if e["tag"] in BLOCK_TAGS), None)
            if block is not None:
                key = "q_line" if tag == "q" else "has_cite"
                block.setdefault(key, line if tag == "q" else True)
        for r in self.recalls:
            r[1] = r[1] or (tag == "a" and is_lesson_link(dict(attrs).get("href") or ""))
            r[2] = r[2] or tag == "details"
        if tag in VOID_TAGS:
            return
        exempt = self.top("exempt") or tag in EXEMPT_TAGS or bool(classes & EXEMPT_CLASSES)
        skip = self.top("skip") or tag in SKIP_TAGS
        steps = self.top("steps") or "steps" in classes
        if exempt and not self.top("exempt") and not skip and self.blocks \
                and tag not in BLOCK_TAGS:
            self.blocks[-1].add(f" {EXEMPT_MARK} ", line)
        self.stack.append(dict(tag=tag, classes=classes, exempt=exempt,
                               skip=skip, steps=steps, line=line))
        if tag in BLOCK_TAGS:
            self.flush()
            self.blocks.append(Block(tag, steps))
        if tag == "section" and "fp" in classes:
            self.fp.append([line, []])
        for box in BOX_LINES:
            if box in classes:
                self.gaps.append([line, "", box])
        if "recall-check" in classes:
            self.recalls.append([line, False, False])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not any(e["tag"] == tag for e in self.stack):
            return
        while self.stack:
            e = self.stack.pop()
            if e["tag"] in BLOCK_TAGS:
                self.flush()
                self.blocks.pop()
                if e.get("q_line") and not e.get("has_cite"):
                    self.findings.append(Finding(
                        self.path, e["q_line"], "quote",
                        "<q> source quote needs a .cite citation in the same paragraph or list item"))
            if e["tag"] == "section" and "fp" in e["classes"]:
                self.close_fp()
            if e["classes"] & BOX_LINES.keys():
                self.close_gap()
            if "explain" in e["classes"]:
                line, sourced = self.explains.pop()
                if not sourced:
                    self.findings.append(Finding(
                        self.path, line, "explain",
                        ".explain is an answer, so a claim: cite it with .cite, or put it in a .gap"))
            if "recall-check" in e["classes"]:
                self.close_recall()
            if e["tag"] == tag:
                break

    def handle_data(self, data):
        for g in self.gaps:
            g[1] += data
        if not self.top("skip") and not self.top("exempt"):
            self.check_lesson_numbers(data)
        if self.top("skip") or self.top("exempt") or not self.blocks:
            return
        self.blocks[-1].add(data, self.getpos()[0])

    def close_fp(self):
        line, seen = self.fp.pop()
        if tuple(seen) == FP_STEPS:
            return
        missing = [s for s in FP_STEPS if s not in seen]
        if missing:
            msg = "section.fp is missing " + ", ".join(missing)
        else:
            msg = "section.fp steps out of order: " + ", ".join(seen)
        self.findings.append(Finding(self.path, line, "fp",
                                     msg + f" (need {', '.join(FP_STEPS)})"))

    def close_gap(self):
        line, text, box = self.gaps.pop()
        if not " ".join(text.split()).startswith(BOX_LINES[box]):
            self.findings.append(Finding(self.path, line, box,
                                         f".{box} must start with: {BOX_LINES[box]}"))

    def check_link(self, href, line):
        target = href.split("#", 1)[0].split("?", 1)[0]
        if ":" in target or not LESSON_FILE.match(Path(target).name):
            return
        if not (Path(self.path).parent / target).exists():
            self.findings.append(Finding(self.path, line, "lesson-ref",
                                         f"link to {target}, which does not exist"))

    def check_lesson_numbers(self, data):
        start = self.getpos()[0]
        for m in LESSON_NUMBER.finditer(data):
            n = int(m.group(1))
            if not any(p for p in self.lessons_dir.glob(f"{n:04d}-*.html")
                       if not is_old_copy(p)):
                line = start + data.count("\n", 0, m.start())
                self.findings.append(Finding(
                    self.path, line, "lesson-ref",
                    f"lesson {n:04d} does not exist yet: refer to a future lesson by its topic"))

    def finish(self):
        if self.component_line and not self.components_linked:
            self.findings.append(Finding(
                self.path, self.component_line, "components",
                'uses a skill component: link ../assets/components.css before lesson.css'))

    def close_recall(self):
        line, link, answer = self.recalls.pop()
        missing = [m for m, ok in (("a link to the lesson that built it", link),
                                   ("a <details> answer", answer)) if not ok]
        if missing:
            self.findings.append(Finding(self.path, line, "recall",
                                         ".recall-check needs " + " and ".join(missing)))


def check_html(path, checker, findings, lessons_dir):
    raw = Path(path).read_text(encoding="utf-8")
    first = raw.split("\n", 1)[0]
    if not re.search(r"<meta\s+charset=[\"']?utf-8", first, re.I):
        findings.append(Finding(str(path), 1, "charset",
                                'line 1 must be <meta charset="utf-8">'))
    parser = LessonParser(str(path), checker, findings, lessons_dir)
    parser.feed(raw)
    parser.close()
    while parser.stack:
        parser.handle_endtag(parser.stack[-1]["tag"])
    parser.finish()


def check_glossary(path, checker, findings):
    """Check each GLOSSARY.md definition as one descriptive paragraph."""
    gaps = gap_names(Path(path).parent)
    for e in parse_glossary(path):
        problem = source_problem(e, gaps)
        if problem:
            findings.append(Finding(str(path), e.line, "glossary", problem))
        block = Block("p", False)
        for n, line in e.definition:
            block.add(line + "\n", n)
        checker.check_block(str(path), block, findings)


def check_paths(paths, workspace, home):
    dictionary, _ = load_dictionary(find_ste_dir(workspace, home))
    checker = Checker(dictionary, glossary_terms(workspace))
    findings = []
    for p in paths:
        if is_old_copy(p):
            continue
        if str(p).endswith(".md"):
            check_glossary(p, checker, findings)
        else:
            check_html(p, checker, findings, Path(workspace) / "lessons")
    return sorted(findings, key=lambda f: (f.file, f.line, f.rule))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check teach-from-source Course material.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--version", action="version", version=f"course_check.py {VERSION}")
    args = ap.parse_args(argv)

    workspace, home = Path.cwd(), Path.home()
    paths = [Path(f) for f in args.files]
    if not paths:
        paths = sorted(Path("lessons").glob("*.html")) + sorted(Path("reference").glob("*.html"))
        if Path("GLOSSARY.md").is_file():
            paths.append(Path("GLOSSARY.md"))

    _, mode = load_dictionary(find_ste_dir(workspace, home))
    print(mode, file=sys.stderr)
    old = sum(1 for p in paths if is_old_copy(p))
    if old:
        print(f"skipped {old} old lesson {'copy' if old == 1 else 'copies'} (NNNN-name.vX.Y.Z.html)",
              file=sys.stderr)
    findings = check_paths(paths, workspace, home)
    for f in findings:
        print(f"{f.file}:{f.line}: [{f.rule}] {f.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
