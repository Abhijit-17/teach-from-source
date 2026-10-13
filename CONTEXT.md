# teach-from-source

A skill that teaches a learner a topic grounded in material the learner points at, with every claim traced to that material.

## Language

### Material

**Primary source**:
Material the learner brought and wants to learn from, registered in `SOURCES.md` under `## Primary`.
_Avoid_: book, input, document

**Supplementary source**:
Freely available original material the skill recommends to cover a Gap, which is acquired into the workspace and cited like a Primary source. It always names the Gap it covers.
_Avoid_: resource, extra reading, reference material

**Gap**:
Something the Mission needs that no registered source covers.
_Avoid_: missing topic, hole

**Outside-the-source**:
Lesson content that no registered source backs, shown visibly in the lesson and logged as a Gap.
_Avoid_: background, general knowledge, parametric knowledge

### Grounding

**Source wins**:
The rule that teaching depth is bounded by registered sources: anything deeper must come from a Supplementary source or be marked Outside-the-source.
_Avoid_: source-first, grounding rule

### Teaching method

**First-principles sequence**:
The five-step order in which a concept is taught: Problem, Ground truths, Build-up, Name it last, Foundation test.
_Avoid_: first principles approach, derivation, bottom-up teaching

**New concept**:
A concept in a lesson that the learner has not yet shown they know. Every New concept gets the full First-principles sequence.
_Avoid_: unfamiliar concept, fresh topic

**Known concept**:
A concept with evidence the learner knows it (coverage `practiced` or a learning record). It gets a one-line recall linking to the lesson that built it.
_Avoid_: covered concept, taught concept, prerequisite

**Ground truth**:
A basic fact or assumption a concept rests on, cited to a registered source, from which the concept is derived.
_Avoid_: axiom, premise, fundamental, basics

**Build-up**:
The step-by-step derivation of a concept from its Ground truths, where each step follows from the previous one.
_Avoid_: walkthrough, explanation

**Foundation test**:
A "what if this Ground truth were false?" probe that shows which Ground truth carries the concept.
_Avoid_: counterfactual, sanity check

### Lesson language

**STE**:
ASD-STE100 Simplified Technical English (Issue 9), applied to Course material: Part 1 writing rules always, and the Part 2 dictionary once its use is permitted.
_Avoid_: ASD-TSE100, plain English, simple English, controlled English

**Course material**:
What the learner reads as the course and what STE governs: lessons, reference documents, and `GLOSSARY.md` definitions. Workspace notes and chat are not Course material.
_Avoid_: content, output, docs

**STE dictionary**:
The learner's own official copy of the ASD-STE100 specification, kept outside this repo, against which lesson words are checked.
_Avoid_: word list, STE file, spec

**STE permission note**:
A learner's own record, kept next to their STE dictionary, of ASD's written permission to use the dictionary for checking. Without it the dictionary check stays off.
_Avoid_: licence file, permission flag

**Rules-only mode**:
A learner-approved fallback, used while no STE dictionary is found or its use is not permitted, in which lessons apply the STE writing rules but not the dictionary and carry a visible badge saying so.
_Avoid_: lite STE, partial STE, degraded mode

**Exempt text**:
Text in a lesson that STE does not govern: verbatim source quotes, code, formulas, citation locators, titles, and personal names. Everything else the skill writes in a lesson is governed by STE.
_Avoid_: excluded content, non-STE text

**Approved word**:
A word listed in the STE dictionary, usable only in its one approved meaning and part of speech.
_Avoid_: allowed word, simple word

**Technical noun**:
A noun defined by a registered source and recorded in `GLOSSARY.md` with its locator, usable in lessons although it is not an Approved word.
_Avoid_: technical name (pre-Issue 9 term), jargon, keyword

**Technical verb**:
A verb defined or used as a term by a registered source and recorded in `GLOSSARY.md` with its locator, usable in lessons although it is not an Approved word. This is broader than STE Rule 1.12 technical-verb categories.
_Avoid_: domain verb, jargon
