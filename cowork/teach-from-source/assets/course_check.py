#!/usr/bin/env python3
# course_check.py 1.1.0
"""Check teach-from-source Course material before a lesson is announced.

Usage, from the workspace root:
    python3 assets/course_check.py [FILE ...]

With no FILE, checks lessons/*.html, reference/*.html and GLOSSARY.md.
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

Exempt text (blockquote, cite, code, pre, .cite, .math, .name) is not checked
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
FP_STEPS = ("fp-problem", "fp-truths", "fp-buildup", "fp-name", "fp-test")
FP_LABELS = {"Problem", "Ground truths", "Build-up", "Name", "Foundation test"}

EXEMPT_TAGS = {"blockquote", "cite", "code", "pre"}
EXEMPT_CLASSES = {"cite", "math", "name"}
SKIP_TAGS = {"head", "title", "script", "style", "template"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "source", "track", "wbr"}
BLOCK_TAGS = {"p", "li", "td", "th", "dd", "dt", "figcaption", "caption",
              "h1", "h2", "h3", "h4", "h5", "h6", "div", "section", "article",
              "aside", "header", "footer", "nav", "main", "figure", "ul", "ol",
              "dl", "table", "thead", "tbody", "tr", "details", "summary",
              "blockquote", "pre", "body", "html"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

EXEMPT_MARK = ""  # stands in for one span of Exempt text
GROUP_MARK = ""   # stands in for one parenthetical or quotation

UNITS = {"ms", "s", "us", "µs", "ns", "min", "h", "b", "kb", "mb", "gb", "tb",
         "kib", "mib", "gib", "bytes", "mm", "cm", "m", "km", "g", "kg", "%",
         "hz", "khz", "mhz", "ghz", "rpm"}
NUMBER = re.compile(r"^[\d.,/%:+-]+$")
SENTENCE_END = re.compile(r"[.!?][\"”’)\]]*(?=\s|$)")
CONTRACTION = re.compile(
    r"\b\w+n[’']t\b|\b\w+[’'](?:re|ll|ve|m|d)\b|\b(?:it|that|there|what|here|who)[’']s\b",
    re.IGNORECASE)
WORD = re.compile(r"[A-Za-z][A-Za-z’'-]*")


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
    text = re.sub(r"“[^”]*”|\"[^\"]*\"", f" {GROUP_MARK} ", text)
    tokens = [t for t in text.split() if re.search(r"\w|[]", t)]
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


def glossary_terms(workspace):
    """Words of every **Term**: heading in GLOSSARY.md (Technical nouns and verbs)."""
    path = Path(workspace) / "GLOSSARY.md"
    if not path.is_file():
        return set()
    terms = set()
    for m in re.finditer(r"^\*\*(.+?)\*\*:\s*$", path.read_text(encoding="utf-8"), re.M):
        terms.update(w.lower() for w in WORD.findall(m.group(1)))
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
        if text.strip().startswith(GAP_LINE):
            i = text.index(GAP_LINE)
            text = text[:i] + " " * len(GAP_LINE) + text[i + len(GAP_LINE):]
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
                    lead = " ".join(s.replace(EXEMPT_MARK, "…").split()[:8])
                    findings.append(Finding(path, block.line_at(offset), rule,
                                            f"sentence has {n} words (max {limit}): {lead} …"))
            if block.tag == "p" and len(sentences) > PARAGRAPH_MAX:
                findings.append(Finding(path, block.line_at(0), "STE 6.6",
                                        f"paragraph has {len(sentences)} sentences "
                                        f"(max {PARAGRAPH_MAX})"))

        if self.dictionary is None or (heading and text.strip() in FP_LABELS):
            return
        for m in WORD.finditer(text):
            word = re.sub(r"[’']s$|[’']$", "", m.group()).strip("-")
            if not word or "'" in word or "’" in word or self.allowed(word):
                continue
            findings.append(Finding(path, block.line_at(m.start()), "STE 1.1",
                                    f"'{word}' is not an Approved word or a GLOSSARY.md term"))


# --- HTML --------------------------------------------------------------------

class LessonParser(HTMLParser):
    """Splits a lesson into Blocks and checks fp and gap structure."""

    def __init__(self, path, checker, findings):
        super().__init__(convert_charrefs=True)
        self.path, self.checker, self.findings = path, checker, findings
        self.stack = []      # dicts: tag, classes, exempt, skip, steps, line
        self.blocks = []     # open Blocks, innermost last
        self.fp = []         # open fp sections: [line, step classes seen]
        self.gaps = []       # open .gap elements: [line, text]

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
        if "gap" in classes:
            self.gaps.append([line, ""])

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
            if e["tag"] == "section" and "fp" in e["classes"]:
                self.close_fp()
            if "gap" in e["classes"]:
                self.close_gap()
            if e["tag"] == tag:
                break

    def handle_data(self, data):
        for g in self.gaps:
            g[1] += data
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
        line, text = self.gaps.pop()
        if not " ".join(text.split()).startswith(GAP_LINE):
            self.findings.append(Finding(self.path, line, "gap",
                                         f".gap must start with: {GAP_LINE}"))


def check_html(path, checker, findings):
    raw = Path(path).read_text(encoding="utf-8")
    first = raw.split("\n", 1)[0]
    if not re.search(r"<meta\s+charset=[\"']?utf-8", first, re.I):
        findings.append(Finding(str(path), 1, "charset",
                                'line 1 must be <meta charset="utf-8">'))
    parser = LessonParser(str(path), checker, findings)
    parser.feed(raw)
    parser.close()
    while parser.stack:
        parser.handle_endtag(parser.stack[-1]["tag"])


def check_glossary(path, checker, findings):
    """Check each definition in GLOSSARY.md as one descriptive paragraph."""
    block, in_def = None, False
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if re.match(r"^\*\*(.+?)\*\*:\s*$", line):
            block, in_def = Block("p", False), True
        elif in_def and line.strip() and not line.startswith("_Avoid_"):
            block.add(line + "\n", n)
            continue
        elif in_def:
            checker.check_block(str(path), block, findings)
            in_def = False
    if in_def:
        checker.check_block(str(path), block, findings)


def check_paths(paths, workspace, home):
    dictionary, _ = load_dictionary(find_ste_dir(workspace, home))
    checker = Checker(dictionary, glossary_terms(workspace))
    findings = []
    for p in paths:
        if str(p).endswith(".md"):
            check_glossary(p, checker, findings)
        else:
            check_html(p, checker, findings)
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
    findings = check_paths(paths, workspace, home)
    for f in findings:
        print(f"{f.file}:{f.line}: [{f.rule}] {f.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
