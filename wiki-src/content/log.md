---
title: Log
unlisted: true
---

# Log

*Chronological record of wiki operations.*

## [2026-06-11] maintenance | Graph cleanup — connectivity, layout, colour

Fixed the LLM Wiki app graph (messy "Other 65" grey blob, scattered clusters, apparently-orphaned pages like GCER). Root causes: (a) the 63 kebab-renamed files had a UTF-8 BOM that broke the app's `type:` detection; (b) the app only builds graph edges from `[[wikilinks]]`, but most relationships were written as plain text.

**Changes:**
- **BOM stripped** from all 63 affected files (UTF-8 no-BOM) → restored correct `type:` colours.
- **Dead links resolved (all 22 targets → 0):** repaired malformed/variant links (PLTOF, LNRS-2026, escaped-pipe table link, path-style), piped shorthand (`[[GCER]]` → `[[Gloucestershire Centre for Environmental Records|GCER]]`), and unbracketed non-pages.
- **Related sections bracketed:** 704 plain-text page references across 131 pages converted to `[[wikilinks]]` (allow-listed to real pages) → edges jumped to ~1,200; GCER inbound links 0 → 42.
- **7 stub pages created:** [[Defra]], [[Environment Agency]], [[Historic England]], [[CIEEM]], [[Cotswold Beechwoods SAC]], [[Rodborough Common SAC]], [[Wye Valley Woodlands SAC]].
- **Central hub:** [[Home]] retitled "Gloucestershire Planning & Nature Wiki" (`type: hub`), linked to 12 core/sub-hub pages, with reciprocal `[[Home]]` back-links → sits central, ringed by core topics.
- **Protected-species cluster** tightened (reciprocal hub links on all species/survey pages).
- **Type tidy:** `type: organisation` → `entity` (9 council/org pages).
- Added 2 em-dash pages' no-dash aliases; populated index Designated Sites / Synthesis sections.

**Result:** 144 graph nodes, ~1,204 edges, 0 dead links, 0 orphans, only `log.md` lacks a type. Use the app's **Community** colour mode for topical grouping.

## [2026-06-10] ingest | GWT Neighbourhood Nature Planning Toolkit

**Source**: `raw/sources/Neighbourhood Nature planning toolkit.pdf` (22 pages, Gloucestershire Wildlife Trust)

**Pages created**:
- `wiki/sources/GWT Neighbourhood Nature Planning Toolkit.md` — source summary
- `wiki/concepts/` — 35 concept pages covering planning system, legislation, policy, biodiversity, and green infrastructure
- `wiki/entities/` — 11 entity pages (6 Gloucestershire councils, GWT, GCER, Natural England, OEP, Secretary of State)
- `wiki/synthesis/Neighbourhood Plans — Gloucestershire Status.md` — NDP status across all 6 districts
- `wiki/glossary/Glossary.md` — definitions of all key terms

**Pages updated**: n/a (initial ingest)

**Notes**: Initial build. Wiki covers all content from the GWT toolkit PDF plus expanded context on national legislation, policy, and organisation roles. Graph view configured with colour-coding by folder. Two note templates created.


## [2026-06-10] ingest | Natural England — Bats Planning Guidance

Added source summary and 6 new concept pages: [[Bats in Planning]], [[European Protected Species]], [[EPS Mitigation Licence]], [[Bat Surveys]], [[Dark Corridors]], [[Species of Principal Importance]]. Updated Protected Species and Natural England entity pages. Updated index and overview. Key themes: EPS legal framework, survey triggers, precautionary principle, mitigation hierarchy, licensing obligations for LPAs.

## [2026-06-10] ingest | Natural England — Great Crested Newts Planning Guidance

## [2026-06-10] ingest | Natural England — Otters Planning Guidance

Added source summary at `wiki/sources/Natural England - Otters Planning Guidance.md`. Created new concept page `wiki/concepts/otters-in-planning.md` covering legal status (EPS + WCA 1981 + S41), water proximity survey trigger, survey methods, mitigation hierarchy (including mammal ledges and artificial holts), site-by-site EPS licensing, and the absence of a District Level Licensing equivalent. Created new entity page `wiki/entities/nbn-atlas.md` for the National Biodiversity Network Atlas as a recommended first-check tool for species records. Updated `wiki/concepts/european-protected-species.md` to add otters as a third worked example and include a comparison table of EPS licensing routes. Updated `wiki/concepts/eps-mitigation-licence.md` to add otter-specific note on absence of DLL. Updated `wiki/concepts/habitats-and-ecosystems.md` to add riparian habitats section and Gloucestershire watercourse network context. Updated `wiki/entities/natural-england.md` to add otter standing advice and licensing table. Updated `wiki/entities/gloucestershire-centre-for-environmental-records.md` to add otter data coverage and NBN Atlas complementarity note. Updated `wiki/index.md` and `wiki/overview.md`.

## [2026-06-10] ingest | Batch — flooding/SuDS, LWS, NRF, S106/CIL, GWT NRZs, GCER, LNRS

**New raw sources added** (9 files in `raw/sources/`): National SuDS Standards; Nature Restoration Fund Implementation Plan; S106 Guidance; CIL Guidance; Local Wildlife Sites PPG; GWT Nature Recovery Zones; GCER overview; GWT Strategy to 2030 (+ PDF); Gloucestershire LNRS 2026 (+ 84-page PDF).

**New wiki source summaries** (9 in `wiki/sources/`): National Standards for Sustainable Drainage Systems; Nature Restoration Fund Implementation Plan; Planning Obligations Section 106; Community Infrastructure Levy Guidance; Local Wildlife Sites Planning Guidance; GWT Nature Recovery Zones; GCER Overview; GWT Strategy to 2030; Gloucestershire LNRS 2026.

**New concept pages** (4): Nature Restoration Fund, Planning Obligations, Flooding and Natural Flood Management, Planning and Infrastructure Act 2025.

**Updated concept pages**: [[SuDS]] (7 national standards, LLFA role, LNRS reference); Community Infrastructure Levy (exemptions/reliefs, commencement notice, IFS); Local Nature Recovery Strategy (Gloucestershire LNRS 2026, 6 key messages, internationally designated sites, priority species); Local Wildlife Sites (LPA statutory duties, PPG selection criteria, LNRS cross-reference).

**Index updated** — new legislation, policy, biodiversity, and GI/water entries; all 9 new sources listed.

**Total wiki pages: ~80.**

## [2026-06-10] ingest | Natural England — Badgers Planning Guidance
- 2026-06-10: Created query page `conservation-of-habitats-and-species-regulations-2-2026-06-10-213852.md` from review


## [2026-06-10] ingest | Natural England — Water Voles Planning Guidance

Source: Natural England standing advice on water voles in planning (gov.uk, last updated 7 April 2025).
New pages created: [[Water Voles in Planning]], [[Water Vole Surveys]], Natural England - Water Voles Planning Guidance (source summary).
Pages updated: Protected Species, Habitats and Ecosystems, [[Species of Principal Importance]], [[EPS Mitigation Licence]], Natural England, Gloucestershire Centre for Environmental Records, [[Index]], [[Overview]].
Key additions: WCA 1981 (non-EPS) legal status for water voles; Class Licence CL31 for impacts on <50m of bank; displacement mitigation; mink control as compensation; habitat-based survey triggers (soft earth banks, slow-flowing water, dense vegetation, predator escape areas); post-development monitoring requirements.

## [2026-06-10] ingest | Natural England — Wild Birds Planning Guidance
## [2026-06-10] delete | Neighbourhood Nature planning toolkit.pdf

Deleted 1 source file and 1 wiki pages.


## [2026-06-10] ingest | Natural England - Ancient Woodland, Ancient Trees and Veteran Trees Planning Guidance

## [2026-06-10] ingest | Natural England — Hazel Dormice Planning Guidance

Source: Natural England standing advice on hazel dormice in planning (gov.uk)
Pages created: wiki/sources/Natural England - Hazel Dormice Planning Guidance.md, wiki/concepts/hazel-dormice-in-planning.md, wiki/concepts/dormouse-surveys.md, wiki/concepts/green-bridges.md
Pages updated: wiki/concepts/european-protected-species.md, wiki/concepts/species-of-principal-importance.md, wiki/entities/natural-england.md, wiki/concepts/habitats-and-ecosystems.md, wiki/entities/gloucestershire-centre-for-environmental-records.md, wiki/entities/nbn-atlas.md, wiki/index.md, wiki/overview.md
Key additions: Hazel dormice as EPS + S41 + Red List Vulnerable; 3-year survey currency rule; presence assumption rule; green bridges as connectivity mitigation; dormouse survey methods (nest tubes, footprint tunnels, visual searches); hibernation season (October–April) as construction timing consideration

## [2026-06-11] fixes | Review queue — 9 no-research items resolved

**Contradiction fixed**:
- [[Barn Owls in Planning]]: Added prominent warning that barn owl nesting season is April–October, not March–August. The general March–August rule is insufficient for barn owl works and could result in an offence in September/October
- [[Wild Birds in Planning]]: Updated the season note to explicitly call out barn owls and their extended nesting window

**Pages updated**:
- Protected Species: Updated species table to include Hazel Dormice, Reptiles, Swifts with correct links; updated Detailed Coverage section to include all new species pages and Barn Conversions and Wildlife
- [[Badgers in Planning]]: Added s.10 Protection of Badgers Act licensing criteria; expanded bTB context noting Gloucestershire is within the bTB High Risk Area; clarified why translocation is not an option in Gloucestershire
- Biodiversity Net Gain: Added section on how 20% BNG in the Cotswolds National Landscape works in practice; note on which Local Plans need to formally adopt it
- [[European Protected Species]]: Added multi-species EPS coordination section covering timing conflicts between bats/otters/dormice/barn owls and licence sequencing advice
- [[Green Bridges]]: Expanded A417 Missing Link into a full case study with ecological context (dormice, bats, Cotswolds National Landscape, Cotswold Beechwoods SAC)
- [[Glossary]]: Added BS 5837 and Biodiversity Gain Plan entries

**New entity page**:
- [[MHCLG]] — Ministry of Housing, Communities and Local Government; role in planning, NPPF, SuDS, BNG; name history (DCLG → MHCLG → DLUHC → MHCLG)

**review.json**: review-19 (LNRS status) marked as resolved — LNRS 2026 was already ingested

## [2026-06-11] manual | Gap analysis round 2 — 6 new pages created

**New concept pages**:
- [[Reptiles in Planning]] — slow worm, grass snake, common lizard, adder; Schedule 5 WCA 1981; artificial refugia survey method; soft clearance and translocation; no licence required unlike EPS; Gloucestershire context
- [[Flood Risk Assessment]] — FRA and Sequential Test; flood zones 1–3b; Exception Test; climate change allowances; SuDS and NFM relationship; Severn Vale and Tewkesbury context
- [[Biodiversity Gain Plan]] — statutory pre-commencement document; baseline, on-site/off-site gain, management plan, 30-year commitment; priority order; LPA approval process; monitoring and enforcement
- [[Swifts in Planning]] — red-listed S41 species; site-faithful nesters; survey by emergence watch; swift bricks; no licence route; Gloucestershire colonies in market towns and villages
- [[Barn Conversions and Wildlife]] — synthesis for the most common rural planning scenario; bats, barn owls, swallows, swifts, reptiles; prior approval and ecology; EPS licence requirements; Gloucestershire context
- [[Calcareous and Neutral Grassland]] — CG2/CG5 calcareous and MG5/MG4 neutral grasslands; NVC survey; indicator species; butterfly and invertebrate links; Cotswolds escarpment and Severn Vale importance; key sites table; LNRS priorities

**Index and log updated**.

## [2026-06-11] manual | Gap analysis — 11 new pages created

**New concept pages (9)**:
- [[Wye Valley National Landscape]] — designated 1971; covers west Gloucestershire and the Wye gorge; explains Forest of Dean as Crown Forest (not a National Landscape); bat/dormice/white-clawed crayfish ecology; planning protections
- [[Wye Valley Biosphere Reserve]] — UNESCO Biosphere Reserve status (verify current designation); three-zone structure; non-statutory but material planning consideration; international significance of the Wye Valley
- [[30x30 Commitment]] — Kunming-Montreal Global Biodiversity Framework; ~8% of England currently qualifies; GWT target of 30,000 additional ha in Gloucestershire; connection to BNG, LNRS, agri-environment, and NRF
- [[Environmental Impact Assessment]] — Annex I/II development; screening and scoping opinions; Environmental Statement; relationship to EcIA and HRA; Gloucestershire context (Cotswolds Water Park, NSIPs)
- [[Planning Appeals]] — written representations/hearing/public inquiry; who can appeal; third-party involvement; ecology in appeals; five-year housing land supply context
- [[Village Design Statements]] — community design guidance; LPA adoption as material consideration; VDS vs NDP comparison table; nature and biodiversity embedding opportunities
- [[Important Hedgerows]] — Hedgerows Regulations 1997 criteria; ecological (7+ woody species, listed species) and historical (pre-1850 boundaries); 42-day removal notification; Gloucestershire species context (dormice, bats, birds, badgers)
- [[Agri-environment Schemes]] — SFI, Countryside Stewardship, Landscape Recovery; LNRS delivery mechanism; BNG off-site habitat link; Gloucestershire priority habitats and species
- [[Wye Valley National Landscape]] (already logged above)

**New entity pages (1)**:
- Severn Estuary — SAC, SPA, Ramsar; qualifying features; nutrient neutrality driver; HRA screening trigger; ecology (lampreys, twaite shad, migratory birds, otters)

**New synthesis pages (1)**:
- Gloucestershire Internationally Designated Sites — full table of SACs, SPAs, Ramsar sites; planning implications; HRA triggers; in-combination effects; where to find data

**Index and log updated**.

## [2026-06-11] manual | 8 skipped review queue items created

**New concept pages (8)**:
- [[Habitats Regulations Assessment]] — HRA two-stage process, Gloucestershire SAC/SPA sites, IROPI test, NRF connection
- [[Biodiversity Metric]] — statutory BNG calculation tool; habitat/hedgerow/watercourse accounts; condition, distinctiveness, strategic significance; 30-year requirement; LNRS multiplier
- [[Conservation Covenants]] — Environment Act 2021; responsible bodies; Biodiversity Gain Site Register; 30-year minimum; comparison with S106
- [[Tree Preservation Orders]] — LPA power to protect trees; consent requirements; Conservation Area trees; link to ancient trees
- [[Nutrient Neutrality]] — HRA-derived requirement; Severn Estuary relevance; ~16,500 homes/year affected nationally; NRF EDPs as solution from 2026
- [[Ecological Impact Assessment]] — PEA → targeted surveys → impact assessment → mitigation; CIEEM standards; BS 42020; Gloucestershire species context
- [[Invasive Non-Native Species]] — INNS: knotweed, Himalayan balsam, giant hogweed, signal crayfish, mink; legal framework; planning requirements; Gloucestershire LNRS context
- [[Lighting and Wildlife]] — ALAN impacts on bats, otters, dormice, invertebrates, birds; mitigation hierarchy; ILP guidance; Cotswolds dark sky; Gloucestershire context

**Index updated**. Duplicate SuDS source page removed.

## [2026-06-10] ingest | National Standards for Sustainable Drainage Systems (SuDS)
- 2026-06-11: Created query page `restructure-protected-species-as-a-hub-page-2026-06-11-095917.md` from review

## [2026-06-11] maintenance | Kebab-case rename — 63 files

All title-case wiki files with spaces in their filenames were renamed to kebab-case to fix broken links in the LLM Wiki desktop app. The app resolves `related` frontmatter slugs against actual filenames; files named with Title Case and spaces were invisible to the app. Each file's original title was added as an `aliases` entry in its frontmatter so that Obsidian `wikilinks` continue to resolve via the alias.

**Files renamed**: 63 across `wiki/concepts/`, `wiki/entities/`, `wiki/sources/`, and `wiki/synthesis/`
**Total wiki pages after rename**: 139
