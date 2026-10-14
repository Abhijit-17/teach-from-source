"""Tests for course_check.py. Run from the repo root: python3 -m unittest

The samples in tests/samples/ are made up. The word list in
tests/samples/ste100/ is invented for these tests and is not ASD-STE100 content.
"""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "claude-code" / "teach-from-source" / "assets" / "course_check.py"
SAMPLES = Path(__file__).resolve().parent / "samples"

sys.dont_write_bytecode = True  # keep __pycache__ out of the skill folder
spec = importlib.util.spec_from_file_location("course_check", SCRIPT)
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)


class Workspace:
    """A throwaway course workspace with chosen sample lessons copied in."""

    def __init__(self, *lessons, dictionary=False, permission=False):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "course"
        self.home = Path(self.tmp.name) / "home"
        (self.root / "lessons").mkdir(parents=True)
        self.home.mkdir()
        shutil.copy(SAMPLES / "GLOSSARY.md", self.root / "GLOSSARY.md")
        for name in lessons:
            shutil.copy(SAMPLES / "lessons" / f"{name}.html", self.root / "lessons")
        if dictionary:
            ste = self.root / "ste100"
            ste.mkdir()
            shutil.copy(SAMPLES / "ste100" / "approved-words.tsv", ste)
            if permission:
                (ste / "PERMISSION.md").write_text("Test permission note.\n")

    def check(self, *names):
        paths = [self.root / "lessons" / f"{n}.html" for n in names]
        return cc.check_paths(paths, workspace=self.root, home=self.home)

    def close(self):
        self.tmp.cleanup()


def rules(findings):
    return sorted({f.rule for f in findings})


class WorkspaceTest(unittest.TestCase):
    def ws(self, *lessons, **kw):
        w = Workspace(*lessons, **kw)
        self.addCleanup(w.close)
        return w

    def check_one(self, name, **kw):
        return self.ws(name, **kw).check(name)


class CleanLessonTest(WorkspaceTest):
    def test_clean_lesson_has_no_findings_in_rules_only_mode(self):
        self.assertEqual(self.check_one("clean"), [])

    def test_clean_lesson_has_no_findings_with_dictionary(self):
        self.assertEqual(self.check_one("clean", dictionary=True, permission=True), [])


class CharsetTest(WorkspaceTest):
    def test_missing_charset_on_first_line_is_reported_at_line_1(self):
        findings = self.check_one("missing-charset")
        self.assertEqual(rules(findings), ["charset"])
        self.assertEqual(findings[0].line, 1)


class SentenceLengthTest(WorkspaceTest):
    def test_descriptive_sentence_over_25_words(self):
        findings = self.check_one("long-descriptive")
        self.assertEqual(rules(findings), ["STE 6.3"])
        self.assertEqual(findings[0].line, 5)

    def test_procedural_sentence_over_20_words(self):
        self.assertEqual(rules(self.check_one("long-procedural")), ["STE 5.1"])

    def test_same_sentence_outside_steps_is_descriptive_and_passes(self):
        self.assertEqual(self.check_one("procedural-length-as-descriptive"), [])

    def test_exempt_span_counts_as_one_word(self):
        findings = self.check_one("long-with-exempt")
        self.assertEqual(rules(findings), ["STE 6.3"])
        self.assertIn("26 words", findings[0].message)

    def test_each_quiz_button_is_its_own_block(self):
        self.assertEqual(self.check_one("quiz-buttons"), [])

    def test_paragraph_over_6_sentences(self):
        self.assertEqual(rules(self.check_one("long-paragraph")), ["STE 6.6"])


class PunctuationTest(WorkspaceTest):
    def test_semicolon_in_checked_text(self):
        self.assertEqual(rules(self.check_one("semicolon")), ["STE 8.1"])

    def test_contraction_in_checked_text(self):
        self.assertEqual(rules(self.check_one("contraction")), ["STE 4.2"])


class StructureTest(WorkspaceTest):
    def test_fp_section_missing_a_step(self):
        findings = self.check_one("fp-missing-step")
        self.assertEqual(rules(findings), ["fp"])
        self.assertIn("fp-name", findings[0].message)

    def test_fp_section_out_of_order(self):
        self.assertEqual(rules(self.check_one("fp-out-of-order")), ["fp"])

    def test_gap_without_fixed_first_line(self):
        self.assertEqual(rules(self.check_one("gap-without-fixed-line")), ["gap"])

    def test_recall_check_without_answer(self):
        findings = self.check_one("recall-check-without-answer")
        self.assertEqual(rules(findings), ["recall"])
        self.assertIn("details", findings[0].message)

    def test_recall_check_without_link(self):
        findings = self.check_one("recall-check-without-link")
        self.assertEqual(rules(findings), ["recall"])
        self.assertIn("link", findings[0].message)


class DictionaryTest(WorkspaceTest):
    def test_disallowed_word_is_reported_with_permission(self):
        findings = self.check_one("disallowed-word", dictionary=True, permission=True)
        self.assertEqual(rules(findings), ["STE 1.1"])
        self.assertIn("utilizes", findings[0].message)

    def test_untagged_name_is_reported_with_permission(self):
        findings = self.check_one("untagged-name", dictionary=True, permission=True)
        words = " ".join(f.message for f in findings)
        self.assertIn("Martin", words)
        self.assertIn("Kleppmann", words)

    def test_rules_only_without_permission_skips_word_check(self):
        self.assertEqual(self.check_one("disallowed-word", dictionary=True), [])

    def test_rules_only_still_checks_length(self):
        findings = self.check_one("long-descriptive", dictionary=True)
        self.assertEqual(rules(findings), ["STE 6.3"])

    def test_workspace_ste100_is_found_before_home(self):
        w = self.ws(dictionary=True)
        (w.home / ".claude" / "ste100").mkdir(parents=True)
        self.assertEqual(cc.find_ste_dir(w.root, w.home), w.root / "ste100")

    def test_home_ste100_is_used_when_workspace_has_none(self):
        w = self.ws()
        home_ste = w.home / ".claude" / "ste100"
        home_ste.mkdir(parents=True)
        self.assertEqual(cc.find_ste_dir(w.root, w.home), home_ste)


class GlossaryTest(WorkspaceTest):
    def test_long_glossary_definition_is_reported(self):
        w = self.ws()
        with open(w.root / "GLOSSARY.md", "a") as g:
            g.write(
                "\n**Follower**:\n"
                "A node that reads all writes from the leader and keeps a copy of the "
                "data so that it can take over when the leader stops at any time.\n"
                "_Source_: [Ch. 5 §1, p. 153]\n"
            )
        findings = cc.check_paths([w.root / "GLOSSARY.md"], workspace=w.root, home=w.home)
        self.assertEqual(rules(findings), ["STE 6.3"])
        self.assertEqual(findings[0].line, 21)

    def test_sample_glossary_is_clean_with_dictionary(self):
        w = self.ws(dictionary=True, permission=True)
        findings = cc.check_paths([w.root / "GLOSSARY.md"], workspace=w.root, home=w.home)
        self.assertEqual(findings, [])

    def append_unsourced_term(self, w):
        with open(w.root / "GLOSSARY.md", "a") as g:
            g.write("\n**Utilizes**:\nA made-up term with no locator.\n")

    def test_entry_without_source_line_is_reported(self):
        w = self.ws()
        self.append_unsourced_term(w)
        findings = cc.check_paths([w.root / "GLOSSARY.md"], workspace=w.root, home=w.home)
        self.assertEqual(rules(findings), ["glossary"])
        self.assertEqual(findings[0].line, 20)
        self.assertIn("Utilizes", findings[0].message)

    def test_term_without_source_line_is_not_a_technical_word(self):
        w = self.ws("disallowed-word", dictionary=True, permission=True)
        self.append_unsourced_term(w)
        findings = w.check("disallowed-word")
        self.assertEqual(rules(findings), ["STE 1.1"])
        self.assertIn("utilizes", findings[0].message)


class WordCountTest(unittest.TestCase):
    def test_number_with_unit_parentheses_and_hyphens_count_as_one(self):
        text = "Set the value to 20 ms (see the note) on the well-known node."
        self.assertEqual(cc.count_words(text), 10)


class CommandLineTest(WorkspaceTest):
    def run_cli(self, w, *names):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *[f"lessons/{n}.html" for n in names]],
            cwd=w.root, capture_output=True, text=True,
            env={"HOME": str(w.home), "PATH": "/usr/bin:/bin"},
        )

    def test_exit_0_and_no_output_when_clean(self):
        r = self.run_cli(self.ws("clean"), "clean")
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_exit_1_with_file_line_findings(self):
        r = self.run_cli(self.ws("semicolon"), "semicolon")
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"^lessons/semicolon\.html:5: \[STE 8\.1\] ")

    def test_mode_line_on_stderr_in_rules_only_mode(self):
        r = self.run_cli(self.ws("clean"), "clean")
        self.assertIn("STE: writing rules only, dictionary not checked", r.stderr)

    def test_version_flag(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--version"],
                           capture_output=True, text=True)
        self.assertRegex(r.stdout.strip(), r"^course_check\.py \d+\.\d+\.\d+$")


if __name__ == "__main__":
    unittest.main()
