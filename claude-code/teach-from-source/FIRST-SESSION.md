# First Session: Ingest Before You Teach

Do not teach from a source you have not mapped. On a new source:

0. **Confirm the workspace.** The current directory becomes a teaching workspace, and files will be created here. If it already contains an unrelated project, stop and agree on a directory with the user before writing anything.
1. **Acquire and identify.** Get a stable local snapshot: confirm the file, fetch the page, clone the repo, pull the transcript. Assign a short stable ID (`atomic-habits`, `sicp`, `attention-paper`).
2. **Map the structure.** Extract the table of contents / section headings into `./sources/<id>/OUTLINE.md`, with locators for each unit. Follow [INGESTION.md](./INGESTION.md) for per-medium mechanics.
3. **Register it** in `SOURCES.md` with provenance and coverage all-unread.
4. **Set up `./assets/`** before writing lesson one, as [SKILL.md](./SKILL.md#set-up-assets) describes.
5. **Establish the mission.** Ask why they want this material, and what "done" looks like: the whole book, one part, one capability. Write `MISSION.md`. Do not skip this because a title looks self-explanatory; "learn SICP" and "pass my compilers exam" produce completely different lesson sequences.
6. **Only then** teach lesson `0001`.

A large book maps in minutes and pays for itself immediately. Resist the urge to start teaching from chapter 1 before the map exists. Without it you cannot judge the zone of proximal development, and you will teach in flat linear order, which is rarely the right order.
