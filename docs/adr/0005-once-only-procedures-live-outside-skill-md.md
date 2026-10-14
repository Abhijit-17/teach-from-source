---
status: accepted
---

# Once-only procedures live outside SKILL.md

SKILL.md loads in full every session, on both hosts, and v1.1.0 almost doubled it (from about 4.8k to 9k tokens). The procedures that run once per course, or only when something turns up, now live in files that the agent reads when SKILL.md sends it there: `FIRST-SESSION.md` (setting up a new course), `UPGRADING.md` (the upgrade sweep and the cutover), and `STE-DICTIONARY.md` (finding the STE dictionary, and its permission gate). SKILL.md keeps the trigger for each one. It also keeps every rule that applies to every lesson or every session: how to resolve `SKILL_DIR` (the upgrade check needs it every session), where to look for the STE dictionary, the Rules-only badge, and the record of Rules-only lessons in `NOTES.md`. The moved text stayed word for word, so no rule changed.

## Considered Options

- **Tighten the wording of SKILL.md**: it would save more, but it rewords rules that were already agreed, so each change needs a new review. Left for later.
- **Put the dictionary steps in `STE-RULES.md`**: rejected, because ADR 0003 removes `STE-RULES.md` if ASD objects to it, and the permission gate must stay.

## Consequences

- A rule that applies to every lesson or every session stays in SKILL.md. Only a procedure with a clear trigger moves out, and SKILL.md names that trigger.
- SKILL.md is about 8k tokens per session instead of 9k.
