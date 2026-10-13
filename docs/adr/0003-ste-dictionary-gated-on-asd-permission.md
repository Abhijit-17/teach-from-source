---
status: accepted
---

# STE dictionary check is gated on ASD permission

ASD-STE100 is free to download, but the Issue 9 PDF is copy-protected (`copy:no`), and its copyright notice forbids reproduction "in whole or in part" without written authority from an officer of ASD. Its special usage rights cover ASD/AIA/AIAC members and their customers, defence ministries, airworthiness authorities, and universities or research institutes for educational purposes, not individual learners in general. The skill therefore builds the dictionary check (a private word list extracted from the learner's own copy) behind a switch that stays off until ASD grants written permission. Until then, Course material runs in Rules-only mode. This repository never ships STE text. It tells users to get their own copy from ASD. The one exception is `STE-RULES.md`: a short summary of the Part 1 writing rules in our own words, with rule numbers and numeric limits but no copied text or examples. The same permission request asks ASD whether this summary is acceptable, and it is removed if ASD objects. If ASD refuses the dictionary, STE in this skill means the Part 1 writing rules only.

## Consequences

- Do not "fix" the disabled dictionary check by turning it on. First check that permission exists, and record it here (update this ADR's status).
- If ASD objects to `STE-RULES.md`, delete it and supersede this ADR.
- The word-list format and extraction steps may be designed now. They must not be run against the real specification before permission arrives.
