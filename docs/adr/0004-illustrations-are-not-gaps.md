---
status: accepted
---

# Illustrations are not Gaps

A lesson often applies a source's claim to the learner's own project ("in MakeMyMarriage, beans are the service that merges Events") or shows it through an analogy (a wedding planner as the container). Neither is a claim about the topic, so neither is missing knowledge. The skill therefore treats them as Illustrations: they go in their own neutral `.illustration` box with a fixed first line, and they are not logged as Gaps. The `.gap` box stays reserved for topic content that no registered source backs, so its warning keeps its meaning. An Illustration may use facts about the learner's project and everyday life, but never a new fact about the topic. Such a fact still goes in a `.gap`.

## Considered Options

- **Everything unsourced is a Gap** (the v1.1.0 trial): rejected. Mappings filled the lessons with Gap boxes, a standing "mappings" Gap appeared in `SOURCES.md`, and an analogy was dropped only to avoid one more box. The Gap signal stopped meaning "be careful here".
- **Register the learner's project documents as a Primary source**: rejected as the general answer. Project documents state facts about the project, not the reasoning that connects the topic to it, and analogies stay unsolved. A course may still register them for their own facts.
- **Allow mappings and analogies as plain prose**: rejected. The learner could no longer see what the sources back, which is the failure ADR 0001 exists to prevent.

## Consequences

- `course_check.py` fails an `.illustration` without its fixed first line and does not check that line's words.
- An Illustration is a place where an unsourced topic fact could hide. The agent's review after the checker must look for one, because a script cannot.
