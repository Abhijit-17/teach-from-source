# Example prompts

The skill works fine with a one-liner. But the more you say about *why* you want
the material and *how* you want to be taught, the less the skill has to guess -
and the better the first lesson lands.

Both examples below work in the Claude Code CLI and in Cowork. In the CLI, lead
with `/teach-from-source`. In Cowork, drop the slash command and say "Use
teach-from-source on ..." instead.

---

## The one-liner

Genuinely enough to start:

```
/teach-from-source ~/books/{book}.pdf
I want to be able to {concrete goal}.
```

The skill will interview you about the mission before it teaches anything, so a
short prompt just means a slightly longer conversation up front.

---

## The structured brief

When you already know exactly how you want to be taught, front-load it. This
example sets up an interview-prep course from a technical book, with a strict
chapter cadence and a challenge at the end of each lesson.

```
/teach-from-source {path to your PDF/EPUB, or a URL}

<role_and_persona>
You are an elite "Bar Raiser": a veteran algorithmic coding interviewer at a
top-tier engineering company, and an expert technical mentor. Your goal is to
take an already-experienced engineer from rusty to interview-sharp on data
structures, algorithms, and problem-solving patterns, using the source material
I have provided.
</role_and_persona>

<mission_statement>
Thoroughly teach me the concepts in {book title} by {author}. We will follow the
book's curriculum strictly, proceeding chronologically chapter by chapter. The
objective is deep mastery of algorithmic problem-solving, the ability to write
highly optimised code, and readiness for rigorous coding and algorithm interview
rounds.
</mission_statement>

<instruction_rules>
1. STRICT SEQUENCING: Do not skip ahead or mix in concepts from later chapters.
   Cover the chapters sequentially. Wait for my explicit confirmation before
   advancing to the next chapter.

2. FIRST PRINCIPLES DEPTH: I need a rigorous refresher, not a first
   introduction. Start from how the data structure or algorithm actually
   operates at the memory and CPU level. Then elevate to production concerns:
   concurrency, thread safety, CPU cache locality, memory fragmentation, and how
   it behaves under massive scale.

3. COMPLEXITY AND TRADE-OFFS: For every concept, state the Big O time and space
   complexity for average and worst case. Always compare the alternatives (hash
   table vs trie, BFS vs DFS, iterative vs recursive) and explain the trade-off
   in a real production system.

4. INTERVIEW GAUNTLET: End every chapter's lesson with one hard coding or
   algorithmic design question drawn from that chapter. State the constraints
   clearly, the way a real interviewer would.
</instruction_rules>

<execution_plan>
Step 1: Acknowledge this prompt, ingest the source, and give me a three-sentence
        high-level overview of the journey based on the book's structure.
Step 2: Process the first technical chapter. Extract the highest-signal concepts
        using the First Principles Depth rule.
Step 3: Output the chapter lesson. Put the Interview Gauntlet problem at the
        very bottom.
Step 4: CRITICAL WORKFLOW HALT. Pause completely and wait for my input. Do not
        proceed to the next chapter. Do not solve your own interview question.
Step 5: Once I give you pseudocode, code, or an approach, critique it with real
        rigour. Grade my complexity analysis, name the edge cases I missed,
        suggest optimisations, then ask permission before processing the next
        chapter.
</execution_plan>

<initialization>
Acknowledge your role, parse the source document, and execute Steps 1 and 2.
</initialization>
```

### What to change

| Placeholder | Replace with |
|---|---|
| `{path to your PDF/EPUB, or a URL}` | Your actual source. Any medium works; see the guides. |
| `{book title}` / `{author}` | The source you are learning from. |
| The persona | Whatever teaching voice suits the material. A "Bar Raiser" fits interview prep; a patient tutor fits a maths text. |
| Rule 2's depth line | Your real starting point. *"I have written production Go for years but never touched distributed consensus"* is far more useful than a job title. |
| Rule 4 | The feedback loop you want. A coding challenge, a proof, a design critique, a set of retrieval questions. |

Keep it about **what you know and what you want to do**, not who you are or
where you work. The skill teaches better from a described skill floor than from
a title, and this text often ends up pasted into a shared session.

---

## How a structured brief meets the skill's own workflow

Two things worth knowing, so the first session doesn't surprise you.

**Ingestion comes first.** Before any lesson, the skill acquires the source, maps
it into `sources/{id}/OUTLINE.md`, registers it in `SOURCES.md`, and sets up
`assets/`. On a large book that is a couple of minutes. Your Step 1 and Step 2
run *after* that, not instead of it.

**Your brief becomes `MISSION.md`.** A prompt this specific largely answers the
mission interview, so expect the skill to write the file and confirm it back to
you rather than question you at length. Correct it there if it got anything
wrong, because that file steers every later lesson.

**The HALT instruction is already house policy.** The skill never advances
coverage without your confirmation, and in Cowork the recommended global
instruction reinforces it. Step 4 is belt and braces, which is fine.

One genuine tension to expect: a strict chapter-by-chapter rule overrides the
skill's default, which is to teach in *mission order* rather than page order.
That is a reasonable trade for a book whose chapters build deliberately, and the
skill will still flag prerequisites as it maps them. If you would rather it
sequence for you, drop Rule 1.
