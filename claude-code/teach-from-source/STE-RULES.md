# STE Writing Rules: Summary

A short summary, in this skill's own words, of the writing rules in Part 1 of ASD-STE100 Simplified Technical English, Issue 9. It gives rule numbers, subjects and numeric limits only. It does not reproduce the specification. For the rules themselves and their examples, use your own copy from ASD (asd-ste100.org).

`course_check.py` checks the rules marked **checked**. You review the others after it runs clean.

## Section 1: Words (rules 1.1-1.14)

- 1.1-1.4: use dictionary words only as their listed part of speech, meaning and form. **Checked** in dictionary mode (word only, not meaning or part of speech).
- 1.5-1.11: technical nouns: when they are allowed, no use as verbs, keep them short and standard, one noun per item. In this skill, a technical noun is a `GLOSSARY.md` term with a `_Source_:` locator.
- 1.12-1.13: technical verbs: when they are allowed, no use as nouns. In this skill, a technical verb is a `GLOSSARY.md` term with a `_Source_:` locator, which is broader than the specification's categories.
- 1.14: American spelling, unless a directive says otherwise.

## Section 2: Noun clusters (rules 2.1-2.2)

- 2.1: at most **3 words** in a noun cluster.
- 2.2: a longer technical noun is written in full once, then shortened or hyphenated.

## Section 3: Verbs (rules 3.1-3.7)

- 3.1-3.4: simple tenses and the forms the dictionary lists. No perfect or progressive constructions. A past participle may act as an adjective.
- 3.5: "-ing" forms only inside technical nouns.
- 3.6: active voice. Passive only in descriptive text, and only when the actor is unknown.
- 3.7: show an action with a verb, not a noun.

## Section 4: Sentences (rules 4.1-4.5)

- 4.1: short, clear sentences.
- 4.2: no dropped words and no contractions. Contractions are **checked**.
- 4.3: vertical lists for complex text.
- 4.4: link related sentences with connecting words.
- 4.5: articles or "this/these" before nouns where they apply.

## Section 5: Procedural writing (rules 5.1-5.5)

- 5.1: at most **20 words** per sentence. **Checked** inside `.steps`.
- 5.2: one instruction per sentence, unless the actions happen together.
- 5.3: instructions in the imperative.
- 5.4: a condition the reader needs first goes before the command, set off by a comma.
- 5.5: notes give information, not instructions.

## Section 6: Descriptive writing (rules 6.1-6.6)

- 6.1-6.2: give information step by step, with key words that show the structure.
- 6.3: at most **25 words** per sentence. **Checked** outside `.steps`.
- 6.4-6.5: one topic per paragraph.
- 6.6: at most **6 sentences** per paragraph. **Checked** on `<p>` and glossary definitions.

## Section 7: Safety instructions (rules 7.1-7.3)

- Name the risk level, start with a clear command or condition, then explain the risk. Rarely needed in lessons.

## Section 8: Punctuation and word count (rules 8.1-8.7)

- 8.1: no semicolons. **Checked**.
- 8.2: hyphens join words that work as one unit.
- 8.3: the uses of parentheses.
- 8.4-8.7: how to count words. A colon that opens a vertical list ends the sentence. A parenthetical counts as one word. A number with its unit, an abbreviation, an identifier, a quotation, a title or a proper name each count as one word. A hyphenated word counts as one word. `course_check.py` counts this way, and counts each span of Exempt text as one word.

## Section 9: Writing practices (rules 9.1-9.4, GR-1 to GR-8)

- 9.1: when a one-word swap does not work, rebuild the sentence.
- 9.2-9.3: use approved words correctly. No phrasal verbs.
- 9.4: one consistent style and terminology.
- General recommendations: "that", "with", pronouns, "this", false friends, Latin abbreviations, inclusive language, possessives.
