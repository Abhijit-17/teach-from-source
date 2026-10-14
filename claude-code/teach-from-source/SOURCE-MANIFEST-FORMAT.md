# SOURCES.md Format

`SOURCES.md` is the spine of the workspace: what material exists, where it lives, how far through it the user is, and what it fails to cover.

## Structure

```md
# {Topic} Sources

## Primary

### `atomic-habits`: _Atomic Habits_, James Clear
- File: `~/books/atomic-habits.pdf` (PDF, 320pp)
- Outline: [sources/atomic-habits/OUTLINE.md](./sources/atomic-habits/OUTLINE.md)
- Ingested: 2026-08-02
- Coverage: 3/20 chapters taught, 2 practiced
- Use for: habit loop mechanics, environment design, identity-based change.

### `deep-work`: _Deep Work_, Cal Newport
- File: `~/books/deep-work.epub` (EPUB)
- Outline: [sources/deep-work/OUTLINE.md](./sources/deep-work/OUTLINE.md)
- Ingested: 2026-08-02 via `unzip` + `pandoc`
- Coverage: 0/12 chapters
- Use for: attention residue, scheduling, the shallow/deep split.

### `huberman-habits`: Huberman Lab, "Habits" episode
- Origin: `https://youtube.com/watch?v=...` (auto-subs, fetched 2026-08-02 via `yt-dlp`)
- Snapshot: `sources/huberman-habits/raw/habits.en.vtt`
- Outline: [sources/huberman-habits/OUTLINE.md](./sources/huberman-habits/OUTLINE.md)
- Locators: timestamps
- Coverage: 2/9 segments taught
- Use for: the neuroscience layer the books gesture at but don't explain.

## Supplementary

### `lally-2010`: "How are habits formed", Lally et al. (2010)
- Origin: `https://example.com/lally-2010.pdf` (fetched 2026-08-03 via `curl`)
- Snapshot: `sources/lally-2010/raw/lally-2010.pdf`
- Gap: the primary source cites the "66 days" figure without the study.
- Recommended: 2026-08-03, as the original study behind the figure. Approved by the user: 2026-08-03.
- Use for: the actual variance in the data.

## Gaps
- **Relapse recovery**: neither source covers it in any depth, and the mission needs it. Find a supplementary source.
- **Ch. 11 figure**: the `atomic-habits` Ch. 11 figure is a scan; text extraction is unreliable.

## Conflicts
- Clear says habit stacking is near-universal; Lally's data suggests high inter-individual variance. Resolved in [learning-records/0004-habit-timeline-variance.md](./learning-records/0004-habit-timeline-variance.md): teach the range, not the number.
```

## Rules

- **Every source gets a short stable ID.** It is the directory name under `sources/`, and it appears in every citation. Do not rename one casually, because lessons link to it.
- **Record the absolute path, format, and size.** A future session needs to find the file without asking.
- **Record provenance for anything remote**: origin URL, fetch date, tool used, and the local snapshot path. Remote content mutates; a citation without a date cannot be checked. Teach from the snapshot, not the live URL.
- **Note lossy extraction.** If a source came through OCR or a converter that mangled things, say so here. It changes how much you trust a quote.
- **Annotate with "use for."** One line on what this source is actually good for. In three months a bare title tells you nothing.
- **Keep coverage current.** Update it in the same turn you finish a lesson, not "later." A stale coverage line makes the next-lesson decision wrong.
- **Separate primary from supplementary.** Primary is what the user brought and wants to learn. Supplementary is what you added to patch a gap, and it must always say which gap.
- **Record the recommendation and the approval.** A Supplementary entry says when you recommended it and when the user approved it. Never register one the user did not approve. If the user downloaded it because you could not fetch it, say so in place of the fetch tool (`downloaded by the user, 2026-08-03`).
- **Give each Gap a bold name** at the start of its line. A glossary entry for a name no source gives refers to its Gap by that name (`_Source_: Outside-the-source (Gap: Relapse recovery)`), and `course_check.py` matches it exactly, ignoring a trailing period or colon.
- **Surface gaps loudly.** A `## Gaps` section that stays empty across a whole book means you are not checking the mission against the source. Every source has gaps.
- **Log conflicts, don't arbitrate silently.** When sources disagree, record both positions and link the learning record where it was resolved.
- **Prune dead sources.** If material turned out to be off-mission or wrong, remove it and note why in `NOTES.md`. Better two sharp sources than nine skimmed ones.
