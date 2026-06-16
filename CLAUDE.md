# Schema — Gloucestershire Planning & Nature Wiki

This file tells Claude Code how to operate as the LLM maintainer of this wiki. Read it at the start of every session before making any changes.

---

## Architecture

```
Planning toolkit wiki/          ← vault root
├── CLAUDE.md                   ← this file (schema + instructions)
├── purpose.md                  ← wiki goals, key questions, scope
├── raw/
│   ├── sources/                ← immutable source documents (PDF, MD, etc.)
│   └── assets/                 ← local images
├── wiki/
│   ├── index.md                ← content catalog (update on every ingest)
│   ├── log.md                  ← chronological operation record
│   ├── overview.md             ← global summary of the wiki's current state
│   ├── concepts/               ← policies, legislation, processes, technical terms
│   ├── entities/               ← real-world orgs, councils, places
│   ├── sources/                ← one summary page per ingested source document
│   ├── synthesis/              ← cross-source analysis, comparison tables, status tables
│   ├── queries/                ← saved valuable query answers
│   └── glossary/               ← term definitions
├── Templates/
└── .obsidian/
```

## Page Types

| Folder | When to use | Frontmatter `type` |
|--------|------------|-------------------|
| `wiki/concepts/` | Policies, legislation, processes, technical concepts | `concept` |
| `wiki/entities/` | Named organisations, councils, bodies, places | `entity` |
| `wiki/sources/` | Summary of an ingested source document | `source` |
| `wiki/synthesis/` | Cross-cutting analysis, status tables, comparisons | `synthesis` |
| `wiki/queries/` | Saved useful Q&A answers | `query` |
| `wiki/glossary/` | Term definitions (can be a single file or per-term) | `glossary` |

## Frontmatter Requirements

Every wiki page must have:
```yaml
---
tags: [tag1, tag2]
type: concept | entity | source | synthesis | query | glossary
aliases: [Alternative Name, Abbreviation]
sources: [filename-of-source.pdf]   # for pages derived from specific sources
---
```

## Wikilink Conventions

- Use `[[Page Name]]` syntax (Obsidian wikilinks)
- Every page should have at least 3–5 outgoing wikilinks
- Every page should end with a `## Related` section listing related pages
- Prefer linking to the most specific relevant page (e.g. `[[Biodiversity Net Gain]]` not `[[Biodiversity]]`)

## Operations

### Ingest
When asked to ingest a new source document:
1. Read the source document from `raw/sources/`
2. Create a summary page in `wiki/sources/` with frontmatter `type: source` and `sources: [filename]`
3. Update or create relevant `wiki/concepts/` and `wiki/entities/` pages
4. Add cross-references (`[[wikilinks]]`) between related pages
5. Update `wiki/index.md` — add new pages to the catalog
6. Update `wiki/overview.md` — revise the global summary
7. Append an entry to `wiki/log.md`:
   `## [YYYY-MM-DD] ingest | Source Title`

### Query
When asked a question about the wiki:
1. Read `wiki/index.md` to identify relevant pages
2. Read the relevant pages
3. Synthesise an answer with citations (cite pages by name)
4. If the answer is valuable, offer to save it to `wiki/queries/`

### Lint
When asked to lint the wiki:
1. Check for orphan pages (no inbound links)
2. Check for missing cross-references between clearly related pages
3. Check for outdated information (flag but don't change without confirmation)
4. Check for pages that should exist but don't
5. Report findings and proposed fixes

## Content Standards

- **Plain English** — avoid jargon; if a technical term is used, explain it or link to its glossary/concept page
- **Gloucestershire context** — add a `## Gloucestershire Context` section to any concept page where local detail applies
- **Accuracy** — do not invent policy, legislation, or statistics; if uncertain, flag with `> Note: verify this claim.`
- **No duplication** — update existing pages rather than creating overlapping new ones
- **No comments about being an LLM** — write the wiki pages as factual reference material

## Index Format

`wiki/index.md` uses this structure:
```
# Index

## Concepts
- [[Page Name]] — one-line summary

## Entities
- [[Page Name]] — one-line summary

## Sources
- [[Page Name]] — source document, date ingested

## Synthesis
- [[Page Name]] — one-line summary
```

## Log Format

`wiki/log.md` entries:
```
## [2026-06-10] ingest | GWT Neighbourhood Nature Planning Toolkit
Summary of what was ingested and what pages were created/updated.
```
