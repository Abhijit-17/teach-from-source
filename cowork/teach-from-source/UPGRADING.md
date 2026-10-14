# Upgrading a Course

[SKILL.md](./SKILL.md#returning-sessions) sends you here from its every-session checks.

## An upgrade

The skill's `course_check.py` or `components.css` is newer than the workspace's copy, or the workspace has none. Copy both files in, then sweep the workspace's own working rules for conflicts with this skill: the conventions in `NOTES.md`, the Gaps in `SOURCES.md`, the lesson plan, and `GLOSSARY.md`. List each conflict with the wording you propose, change only what the user approves, and record the sweep in `NOTES.md` (`Upgrade sweep to skill 1.1.0, 14 Oct 2026: …`). Leave the goals and constraints in `MISSION.md` alone, because they are the user's, and leave old lessons as they are. Known conflicts when a course moves to 1.1.0:

- The old marker `<span class="cite">outside the docs</span>` becomes the `.gap` box. `course_check.py` reports a `.cite` that is not a link.
- A numbered lesson plan becomes topics in order.
- A Gap for mappings onto the user's project, or for analogies, is removed: they are Illustrations.
- A Gap for interview questions is removed: questions are free, and answers are cited.
- Typed quote marks around source words become `<q>` in every lesson written or rewritten from now on.
- Old `GLOSSARY.md` entries. `course_check.py` checks the whole glossary on every run, so an entry with no `_Source_:` line, or a definition over the STE limits, blocks every new lesson. Run `python3 assets/course_check.py GLOSSARY.md` and propose a fix for each finding: move a locator written inside a definition to its own `_Source_:` line, find the locator for an entry that has none or give an Outside-the-source line to a name that no source gives, and reword each definition the checker reports. A rule that adds a term only once the user knows it is dropped: an entry now comes no later than the lesson that first uses the term.

## The cutover

A workspace started before this skill taught first principles and wrote in STE has lessons but no cutover line in `NOTES.md`. Old lessons stay as they are. The new rules apply from the next lesson number: record it (`STE + first-principles from lesson 0013`). Offer **once** to run `course_check.py` on the old lessons and rewrite the ones the user picks, keeping each old version as an old copy (`NNNN-name.vX.Y.Z.html`). Never put an STE badge on an old lesson.
