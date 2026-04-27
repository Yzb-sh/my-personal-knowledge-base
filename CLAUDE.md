# Personal Knowledge Base - Claude Code Instructions

## Project Overview
This is a Zettelkasten-style personal growth-oriented knowledge base for quantitative strategy research. The vault uses Obsidian as the primary platform with LLM-assisted note creation and management.

## Vault Structure
- `00-Inbox/` -- Fleeting notes, unprocessed captures (process within 48h)
- `01-Atlas/` -- Structure notes / Maps of Content (MOCs)
- `02-Source/` -- Literature notes (books, papers, courses, articles)
- `03-Zettel/` -- Permanent atomic notes (the core knowledge)
- `04-Project/` -- Active research projects
- `05-Daily/` -- Daily notes and review logs
- `06-Archive/` -- Inactive and deprecated content
- `09-Templates/` -- Note templates (prefix: T-)
- `10-System/` -- Scripts, config, system-level files

## File Conventions
- **Filenames**: `YYYYMMDDHHmm - Descriptive Title.md` for permanent notes
- **Source notes**: `YYYY-MM-DD - Author - Title.md`
- **Daily notes**: `YYYY-MM-DD.md`
- **Encoding**: UTF-8
- **Links**: Use `[[wikilinks]]`, not markdown links
- **No special characters** in filenames (Windows compatibility)

## Frontmatter Rules
Every note must include YAML frontmatter with:
- `id`: unique identifier (timestamp for zettel, src-date for source, moc-date for structure)
- `title`: note title
- `created` / `updated`: ISO date
- `tags`: array with exactly one `#type/` tag, and for permanent notes one `#domain/` and one `#mastery/` tag

## Tag System
- `type/zettel` | `type/source` | `type/structure` | `type/fleeting` | `type/daily` | `type/code` | `type/project` -- exactly one per note
- `domain/math/*` | `domain/python/*` | `domain/sql/*` | `domain/quant/*` | `domain/methods/*` -- permanent notes only
- `mastery/0-unaware` through `mastery/5-synthesizing` -- permanent notes only
- `status/draft` | `status/review` | `status/active` | `status/archive` -- optional

## Linking Rules
- Every permanent note MUST have at least one outgoing link in `## Connections`
- Each link should have a brief annotation explaining the relationship
- Structure notes (MOCs) are curated annotated indexes of related permanent notes

## When Creating Notes
1. Ask: "What existing note does this connect to?" before saving
2. Use the appropriate template from `09-Templates/`
3. Place in the correct folder based on type
4. Ensure the frontmatter is complete with all required fields
5. For permanent notes: fill in "My Understanding" in the user's own words (no copy-paste)

## When the User Asks for Help
- **Explain a concept**: Offer to create a permanent note using T-Zettel template
- **About a source**: Offer to create a source note using the appropriate T-Source template
- **Review knowledge**: Check for orphan notes, suggest connections, run gap analysis
- **Find gaps**: Compare existing notes against the knowledge framework in MOC files
- **Quiz**: Read relevant permanent notes, generate questions, evaluate answers

## Knowledge Domains
- Mathematics: probability, statistics, linear algebra, calculus, optimization, stochastic processes
- Programming: Python fundamentals, NumPy, Pandas, visualization, quantitative libraries
- SQL: fundamentals, window functions, query optimization
- Quantitative Strategy: factor models, strategy development, backtesting, risk management, portfolio construction, execution
- Learning Methods: Zettelkasten, spaced repetition, learning science

## Priority Guidelines
- Cross-domain bridge notes (notes connecting math↔python, math↔quant, python↔quant) are especially valuable
- Application examples in permanent notes should be quantitative-research-specific
- When suggesting topics to study, reference the dependency order in the MOCs
