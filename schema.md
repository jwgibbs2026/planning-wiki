# Schema — Gloucestershire Planning & Nature Wiki

## Purpose

A knowledge base connecting planning law, policy, biodiversity, and local nature in Gloucestershire. Designed for individuals, community groups, parish councillors, ecologists, and developers who want to understand and engage with the planning system.

## Wiki Structure

```
wiki/
├── index.md          — content catalog (update on every ingest)
├── log.md            — chronological operation record
├── overview.md       — global summary of the wiki's current state
├── concepts/         — policies, legislation, processes, technical terms
├── entities/         — named organisations, councils, bodies, places
├── sources/          — one summary page per ingested source document
├── synthesis/        — cross-cutting analysis, status tables, comparisons
├── queries/          — saved valuable query answers
└── glossary/         — term definitions
```

## Page Types

| Folder | type value | When to use |
|--------|-----------|-------------|
| `wiki/concepts/` | `concept` | Policies, legislation, processes, technical concepts |
| `wiki/entities/` | `entity` | Named organisations, councils, bodies, places |
| `wiki/sources/` | `source` | Summary of an ingested source document |
| `wiki/synthesis/` | `synthesis` | Cross-cutting analysis, comparison tables |
| `wiki/queries/` | `query` | Saved useful Q&A answers |
| `wiki/glossary/` | `glossary` | Term definitions |

## Frontmatter Requirements

Every wiki page must have:
```yaml
---
tags: [tag1, tag2]
type: concept | entity | source | synthesis | query | glossary
aliases: [Alternative Name, Abbreviation]
sources: [filename.pdf]
---
```

## Wikilink Conventions

- Use `[[Page Name]]` syntax throughout
- Every page should have at least 3–5 outgoing wikilinks
- Every page should end with a `## Related` section
- Link to the most specific relevant page

## Ingest Workflow

When a new source is added to `raw/sources/`:
1. Create a summary page in `wiki/sources/` with `type: source`
2. Update or create relevant `wiki/concepts/` and `wiki/entities/` pages
3. Add cross-references between related pages
4. Update `wiki/index.md`
5. Update `wiki/overview.md`
6. Append to `wiki/log.md`: `## [YYYY-MM-DD] ingest | Source Title`

## Query Workflow

1. Read `wiki/index.md` to find relevant pages
2. Read relevant pages in full
3. Answer with citations by page name
4. Offer to save valuable answers to `wiki/queries/`

## Lint Workflow

Check for: orphan pages, missing cross-references, outdated claims, concepts mentioned but lacking their own page, data gaps worth filling with a web search.

## Content Standards

- Plain English — no unexplained jargon
- Add `## Gloucestershire Context` section where local detail applies
- Do not invent policy, legislation, or statistics
- Update existing pages rather than creating duplicates

## Domain

Planning and ecology topics: NPPF, BNG, LNRS, protected sites, protected species, green infrastructure, SuDS, Local Plans, Neighbourhood Plans, Gloucestershire-specific organisations and councils.
