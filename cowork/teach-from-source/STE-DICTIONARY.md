# The STE Dictionary and Its Permission Gate

[SKILL.md](./SKILL.md#the-ste-dictionary-and-its-permission-gate) sends you here before the first lesson of a course, and whenever a dictionary turns up.

This skill never ships STE text. The user gets their own copy of the specification from ASD (free, from asd-ste100.org).

1. **Find it.** Look in the workspace's `./ste100/` first, then `~/.claude/ste100/` (Claude Code only).
2. **Check permission.** The specification's copyright forbids reproduction without ASD's written authority. The word list is a reproduction, so it is extracted only once the folder holds `PERMISSION.md`: the user's own record of ASD's written permission. Without `PERMISSION.md`, do not extract anything, whatever the user says, and tell them why.
3. **Extract once** with permission: write `approved-words.tsv` into the same folder, one row per approved word form (`word<TAB>part of speech<TAB>approved meaning`; lines starting with `#` are comments). Approved words are the uppercase entries in the Part 2 word list. Never copy dictionary text anywhere else.
4. **If the dictionary is missing or not permitted**, stop before the first lesson that needs it. Explain where to get the specification, where to put it, and what `PERMISSION.md` is. Then offer **Rules-only mode**: lessons follow the STE writing rules, the dictionary is not checked, and each lesson's header carries the badge
   ```html
   <p class="lesson-meta">STE: writing rules only, dictionary not checked</p>
   ```
   Use Rules-only mode only once the user agrees. Record it in `NOTES.md` with each Rules-only lesson number. `course_check.py` reports which mode it ran in on its first line of stderr.
