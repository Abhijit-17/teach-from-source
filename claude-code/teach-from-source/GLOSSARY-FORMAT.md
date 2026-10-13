# GLOSSARY.md Format

`GLOSSARY.md` is the canonical language for this teaching workspace. All explainers, exercises, and learning records should adhere to its terminology. It is also the list of Technical nouns and Technical verbs that STE allows in lessons (see SKILL.md -> ASD-STE100 Writing): a source term may appear in a lesson only once it has an entry here with a `_Source_:` locator. Definitions are Course material, so they are written in STE and checked by `course_check.py`.

## Structure

```md
# {Topic} Glossary

{One or two sentence description of the topic this glossary covers.}

## Terms

**Hypertrophy**:
The growth of a muscle that mechanical tension and metabolic stress cause over many training sessions.
_Avoid_: Bulking, getting big
_Source_: [Ch. 2 §1, p. 31]

**Progressive overload**:
A gradual increase in the demand on a muscle over time, through load, volume, or intensity.
_Avoid_: Pushing harder, levelling up
_Source_: [Ch. 3, p. 54]

**RPE (Rate of Perceived Exertion)**:
A self-rating from 1 to 10 of how hard a set was. A value of 10 is failure, and 8 means that two more reps were possible.
_Avoid_: Effort score, intensity rating
_Source_: [Ch. 3 §4, p. 70]
```

## Rules

- **Add a term no later than the lesson that first uses it**, at the latest in that concept's Name step. Lessons may not use a source term that has no entry. Whether the user has *learned* the term is tracked by coverage and learning records, not here.
- **Every entry has a `_Source_:` line** with the locator of the source's own definition or first use, in the lesson citation format. An entry without one does not count as a Technical noun or verb, and `course_check.py` reports it.
- **Be opinionated.** When several words exist for the same concept, pick the best one and list the rest as aliases to avoid. This is how language compresses.
- **Keep definitions tight.** One or two sentences. Define what the term IS, not what it does or how to do it.
- **Use the glossary's own terms inside definitions.** Once a term is in the glossary, prefer it everywhere, including inside other definitions. This is what makes complex terms easier to grasp later.
- **Group under subheadings** when natural clusters emerge (e.g. `## Anatomy`, `## Programming`). A flat list is fine when terms cohere.
- **Flag ambiguities explicitly.** If a term is used loosely in the wider field, note the resolution: "In this workspace, 'set' always means a working set. Warm-ups are tracked separately."
- **Revise as understanding deepens.** A definition the user wrote in week one may be wrong by week six. Update in place; do not leave stale entries.
