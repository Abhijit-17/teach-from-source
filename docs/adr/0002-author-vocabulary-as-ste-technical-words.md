---
status: accepted
---

# Author vocabulary counts as STE technical words

Lessons follow ASD-STE100 in full, but the skill also promises to teach in the source author's own vocabulary. To keep both, any term a registered source defines that has a `GLOSSARY.md` entry with its locator counts as a Technical noun (nouns) or Technical verb (verbs). Every other word must be an Approved word in its approved meaning. A source term with no glossary entry may not appear in lesson prose until it gets one. This deliberately goes beyond STE's own narrow technical-verb categories: author verbs such as "memoize" or "rehash" are allowed when the glossary records them.

## Considered Options

- **Nouns only**: author nouns stay, author verbs are rewritten with Approved words. Closer to the letter of STE, but rejected because lessons would stop matching the source's language exactly where learners must map lesson to page.
- **STE wins**: replace author terms with Approved words and give the original term only in brackets once. Rejected: it breaks the skill's author-vocabulary rule and makes "go read it yourself" pointers harder to follow.

## Consequences

- An entry counts only when it has a valid `_Source_:` line. `course_check.py` reports entries without one and does not treat their terms as Technical nouns or verbs.
- A common name that no registered source gives may also be an entry, with `_Source_: Outside-the-source (Gap: <name>)` naming a Gap logged in `SOURCES.md`. The concept is still taught inside a `.gap` box, and the entry gets a real locator once a Supplementary source is approved. Without this, such a name could appear only inside its `.gap` box, and it would fail the dictionary check everywhere else. `course_check.py` checks that the named Gap exists, and it rejects any other `_Source_:` text that is not a `[...]` citation or a link.
- A term gets its `GLOSSARY.md` entry no later than the lesson that first uses it, at the latest in the concept's Name step. The earlier rule "add a term only when the user understands it" is dropped: a New concept could otherwise never be named in the lesson that teaches it. Evidence that the user has learned a term lives in coverage (`practiced`) and learning records.
