# Open-Source Project Setup Guide for the UK Housing Sector

A guide for setting up and running open-source software projects built **by** the UK housing sector, **for** the UK housing sector. Combines professional engineering rigour with embedded skills development, so that housing professionals can meaningfully contribute to and own the tools they use.

Derived from production practices used in the Chronos project coordination platform.

---

## Table of Contents

1. [Philosophy: Why This Guide Exists](#1-philosophy-why-this-guide-exists)
2. [Foundation: Project Identity](#2-foundation-project-identity)
3. [Governance & Roles](#3-governance--roles)
4. [Contributor Journey & Skills Development](#4-contributor-journey--skills-development)
5. [Documentation Architecture](#5-documentation-architecture)
6. [CLAUDE.md: The Agent Constitution](#6-claudemd-the-agent-constitution)
7. [Architecture Decision Records (ADRs)](#7-architecture-decision-records-adrs)
8. [Security, Data Protection & Testing](#8-security-data-protection--testing)
9. [Enforcement Layer: Hooks & Guardrails](#9-enforcement-layer-hooks--guardrails)
10. [AI-Assisted Development & Multi-Agent Coordination](#10-ai-assisted-development--multi-agent-coordination)
11. [Git Workflow & Branch Strategy](#11-git-workflow--branch-strategy)
12. [CI/CD Pipeline](#12-cicd-pipeline)
13. [Developer Experience Scripts](#13-developer-experience-scripts)
14. [Task Tracking & Community Coordination](#14-task-tracking--community-coordination)
15. [Deployment & Operations](#15-deployment--operations)
16. [Collaboration Protocol](#16-collaboration-protocol)
17. [Setup Checklist](#17-setup-checklist)
18. [Principles](#18-principles)

---

## 1. Philosophy: Why This Guide Exists

The UK housing sector has a dependency problem. Critical operations — allocations, repairs, compliance, resident engagement — run on proprietary systems that housing organisations don't control, can't adapt, and pay increasing licence fees to maintain. When a vendor decides to sunset a product or raise prices, the sector has no alternative.

**Open-source, sector-built software changes this.** But only if it's done with enough rigour to be trusted in production, and enough accessibility that housing professionals — not just professional developers — can contribute to and maintain it.

This guide solves both problems simultaneously:

- **Rigour** comes from engineering practices (automated testing, architectural decisions, security patterns, enforcement hooks) that prevent the codebase from degrading as contributors come and go.
- **Accessibility** comes from progressive contributor pathways, clear documentation, AI-assisted development, and a culture that values domain expertise alongside coding skill.

### Core Beliefs

1. **Domain expertise is a first-class contribution.** A housing officer who writes a user story from lived experience, reviews a feature for regulatory accuracy, or documents how allocations actually work in practice is contributing as meaningfully as someone writing code.

2. **Skills development is a product, not a side effect.** Every project interaction should leave the contributor more capable than before. Code reviews teach. Good first issues build confidence. Pair programming transfers knowledge. The housing sector's long-term digital resilience depends on growing its own technical capacity.

3. **Quality protects contributors.** Automated tests, linting, type checking, and enforcement hooks aren't bureaucracy — they're safety nets that let less experienced contributors submit work without fear of breaking things. The guardrails do the worrying so humans don't have to.

4. **Openness requires intentional governance.** Open-source doesn't mean ungoverned. Clear roles, decision-making processes, and codes of conduct make projects welcoming, not chaotic.

---

## 2. Foundation: Project Identity

Before writing code, establish the documents that define what you're building and why.

### MASTERPLAN.md

The single source of truth for vision, architecture, and execution strategy. This is a **living document** but **protected from casual edits** — changes go through governance.

```markdown
# The Masterplan: [Project Name]

## Part 1: Vision & Core Principles (The "Why")
- What housing problem does this solve?
- Who are the users? (residents, housing officers, repairs teams, board members...)
- Core principles (3-5 max) that guide every decision
- How does this relate to existing sector standards and regulation?

## Part 2: System Architecture (The "What")
- Layer diagram with clear separation of concerns
- What each layer owns and does NOT own
- Data flows, especially for personal/sensitive data
- Integration points with existing housing systems (HMS, repairs, CRM)

## Part 3: Technology Stack (The "How")
- Stack choices with rationale (accessibility to sector contributors is a valid reason)
- Infrastructure overview
- Data hosting and sovereignty considerations (UK data, GDPR)
- Development vs. production topology

## Part 4: Sector Context
- Relevant regulation (Regulator of Social Housing, Decent Homes, Building Safety Act)
- Data standards (e.g., UPRN, UniClass, sector data dictionaries)
- Interoperability goals with existing sector systems
- Accessibility requirements (WCAG 2.2 AA minimum for public-facing)
```

**Rule:** Every feature should trace back to MASTERPLAN.md. If it doesn't align, either the work is wrong or the masterplan needs a governed update.

### PROJECT-STATUS.md

A snapshot of where things stand. Written for the community, not just the core team.

```markdown
# Project Status
Last updated: YYYY-MM-DD

## Current Phase: [Phase Name]
## What's Working Now
- [Features that are live and usable]

## What We're Building Next
- [Current priorities, linked to issues]

## How to Get Involved
- [Specific areas where help is needed right now]

## Active Work Streams
| Stream | Lead | Status | Good First Issues |
|--------|------|--------|-------------------|
```

### Licensing

Choose a licence that protects the sector's investment:

| Licence | When to Use |
|---------|-------------|
| **AGPL-3.0** | SaaS/web apps — prevents vendors from taking the code proprietary without contributing back |
| **GPL-3.0** | Desktop/mobile apps — strong copyleft |
| **Apache-2.0** | Libraries, shared components — permissive, patent protection |
| **MIT** | Small utilities — maximum adoption |

**Recommendation for housing sector tools:** AGPL-3.0 for applications (prevents "embrace, extend, extinguish"), Apache-2.0 for shared libraries and data standards.

Include a `LICENSE` file at the repository root and a licence header recommendation in `CONTRIBUTING.md`.

---

## 3. Governance & Roles

Open-source projects need clear governance so decisions are transparent and contributors know who to talk to.

### Governance Model

For sector-built projects, a **benevolent stewardship** model works well:

```
Steering Group (Strategic Direction)
  ├── Sets roadmap priorities aligned with sector needs
  ├── Approves architectural decisions (ADRs)
  ├── Resolves disputes
  └── Membership: representatives from contributing organisations

Maintainers (Technical Authority)
  ├── Merge authority on `main`
  ├── Review and approve PRs
  ├── Mentor contributors
  └── Enforce quality standards

Contributors (Everyone Else)
  ├── Submit issues, PRs, documentation, domain expertise
  ├── Participate in discussions
  └── Progress through contributor ladder (see Section 4)
```

### Decision-Making

| Decision Type | Who Decides | How |
|---------------|-------------|-----|
| Bug fix / small improvement | Any maintainer | Approve PR |
| New feature | Maintainers consensus | Discussion in issue, then PR |
| Architectural change | Steering group + maintainers | ADR process (see Section 7) |
| Dependency addition | Maintainers | ADR if significant, PR review if minor |
| Roadmap priority | Steering group | Quarterly planning meeting |
| Code of conduct enforcement | Steering group | Private deliberation |

### GOVERNANCE.md

Create this file at the repository root:

```markdown
# Governance

## Steering Group
[Names, organisations, how to contact]

## Maintainers
[Names, areas of responsibility]

## How Decisions Are Made
[Reference the table above]

## How to Become a Maintainer
[Contributor ladder — see Section 4]

## Code of Conduct
[Link to CODE_OF_CONDUCT.md]

## Meeting Cadence
- Steering group: quarterly
- Maintainers: fortnightly
- Community call: monthly (open to all)
```

### CODE_OF_CONDUCT.md

Adopt the [Contributor Covenant](https://www.contributor-covenant.org/) (v2.1) as a baseline. Add housing-sector-specific norms:

- Respect that contributors have varying technical backgrounds
- Value domain expertise (housing knowledge) equally with technical expertise
- Be patient with contributors who are learning
- Keep discussions focused on the problem being solved, not the person solving it
- Acknowledge that housing is emotive — residents' lives are affected by this software

---

## 4. Contributor Journey & Skills Development

This is the heart of "built by the sector." Design the project so that contributing **is** skills development.

### Contributor Ladder

Define clear levels so people know where they are and what's next:

```
Level 0: Observer
  → Watch the repo, attend community calls, read docs
  → No setup required
  → Outcome: Understands what the project does and how decisions are made

Level 1: Reporter
  → File issues, suggest improvements, review docs for accuracy
  → Skills: GitHub basics, clear writing
  → Outcome: Can articulate problems and requirements from domain experience

Level 2: Documenter
  → Write/improve docs, user guides, domain glossaries
  → Add housing context to technical decisions
  → Skills: Markdown, domain expertise
  → Outcome: The project's documentation reflects real-world housing practice

Level 3: First-Time Coder
  → Pick up `good-first-issue` tasks (intentionally scoped, well-documented)
  → Pair with a maintainer on first PR
  → Skills: Basic git, one programming language, running tests
  → Outcome: Has shipped code that's running in production

Level 4: Regular Contributor
  → Takes on `help-wanted` issues independently
  → Reviews others' PRs for domain accuracy
  → Skills: Testing, debugging, reading existing code
  → Outcome: Trusted to work on features with light supervision

Level 5: Maintainer
  → Merge authority, mentors others, shapes technical direction
  → Skills: Architecture, code review, project management
  → Outcome: Can steward the project independently
```

### Good First Issues

Every project should maintain a supply of `good-first-issue` labelled tasks. These must be:

- **Scoped**: One file, one function, or one test — not "refactor the auth module"
- **Documented**: The issue description includes which file to edit, what the expected behaviour is, and links to relevant patterns
- **Tested**: Either the test already exists (contributor writes the implementation) or a test template is provided
- **Reviewed promptly**: Nothing kills motivation faster than a PR that sits unreviewed for weeks

**Maintainer commitment:** Review good-first-issue PRs within 48 hours. Leave constructive, educational feedback — even if the PR is perfect, explain *why* it's good.

### Issue Templates

Create `.github/ISSUE_TEMPLATE/` with templates that lower the barrier:

**Bug Report** (`bug_report.md`):
```markdown
---
name: Bug Report
about: Something isn't working as expected
labels: bug, needs-triage
---

## What happened?
[Describe what you saw]

## What should have happened?
[Describe what you expected]

## Steps to reproduce
1.
2.
3.

## Screenshots (if applicable)

## Your environment
- Browser/device:
- User role (resident, housing officer, etc.):
```

**Feature Request** (`feature_request.md`):
```markdown
---
name: Feature Request
about: Suggest an improvement
labels: enhancement, needs-triage
---

## What problem does this solve?
[Describe the housing/operational problem]

## Who benefits?
[Residents? Housing officers? Repairs teams? Board members?]

## How does it work today (without this feature)?
[Current workaround, if any]

## What would the ideal solution look like?
[Describe from the user's perspective, not technically]

## Regulatory or compliance context (if any)
[Is this related to a standard, regulation, or audit requirement?]
```

**Good First Issue** (`good_first_issue.md`):
```markdown
---
name: Good First Issue
about: A scoped task suitable for new contributors
labels: good-first-issue, help-wanted
---

## What needs to happen
[Clear description of the change]

## Where in the code
- File: `path/to/file.ts`
- Function/section: `functionName` (around line NN)

## How to test it
- Run: `npm test -- <pattern>`
- Expected: [what should pass]

## Useful context
- Related docs: [link]
- Similar pattern: [link to existing code that does something similar]
- Domain context: [any housing-specific knowledge needed]

## Mentorship
Tag @[maintainer] if you'd like to pair on this.
```

### Pair Programming Protocol

Pair programming is the fastest way to transfer both technical and domain knowledge. Formalise it:

```markdown
## Pair Programming Guidelines

### When to Pair
- First PR from a new contributor (mandatory — maintainer pairs with contributor)
- Complex features touching multiple layers
- When domain expertise and technical expertise need to merge
- Debugging production issues (two pairs of eyes, different knowledge)

### How It Works
1. **Schedule**: Agree a 60-90 minute slot. Short enough to stay focused.
2. **Setup**: Both parties can see the code (screen share, VS Code Live Share, or similar)
3. **Roles**: Driver (types) and Navigator (guides). Swap every 20-30 minutes.
4. **For skill-building pairs**: The less experienced person drives MORE. Typing builds muscle memory.
5. **Capture**: After the session, the less experienced person writes the commit message and PR description. Writing crystallises understanding.

### Pairing Across the Skill Gap
| Contributor Level | Maintainer Role |
|-------------------|----------------|
| Level 1 (Reporter) | Walk through codebase, explain architecture decisions |
| Level 3 (First-Time Coder) | Guide through git workflow, first PR, test writing |
| Level 4 (Regular) | Discuss design trade-offs, review approach before implementation |
```

### Learning Checkpoints

Build reflection into the contribution process:

**PR Template addition for new contributors:**
```markdown
## Learning Reflection (optional, for your own growth)
- What did I learn from this change?
- What was confusing and could be better documented?
- What would I do differently next time?
```

Maintainers should respond to these reflections. They're a signal of engagement and a feedback loop for improving the project's onboarding.

### Domain Glossary

Create `docs/GLOSSARY.md` — a living dictionary of housing terms used in the codebase. This is a **two-way bridge**:

- Housing professionals learn how their domain is modelled in code
- Developers learn the domain language so they name things correctly

```markdown
# Domain Glossary

| Term | Definition | Where Used in Code | Notes |
|------|------------|-------------------|-------|
| Allocations | The process of matching applicants to available properties | `services/allocations/` | Subject to statutory guidance and local policy |
| Void | An empty property between tenancies | `models/property.ts` — `status: 'void'` | Not "vacant" — sector-specific term |
| Decant | Temporary relocation of a resident during major works | `models/resident.ts` | Legally complex; usually involves a licence, not a tenancy |
| UPRN | Unique Property Reference Number — national standard for identifying properties | `models/property.ts` — `uprn` field | 12-digit number from AddressBase |
| Tenure | The legal basis on which a resident occupies a property | `types/tenure.ts` | Values: secure, assured, introductory, licence, shared-ownership, leasehold |
| RSH | Regulator of Social Housing | Referenced in compliance checks | Sets consumer and economic standards |
| Decent Homes Standard | Government standard for minimum housing quality | Referenced in repairs/compliance | Currently being updated (2024-2026) |
```

**Convention:** When adding a domain concept to the codebase, add it to the glossary in the same PR. If a code reviewer doesn't understand a term, that's a glossary gap, not a reviewer failure.

---

## 5. Documentation Architecture

Documentation is infrastructure. In an open-source project with diverse contributors, it's also the primary onboarding mechanism.

### Directory Structure

```
project-root/
├── README.md                    # First impression — what, why, how to get started
├── CLAUDE.md                    # AI agent constitution (root)
├── MASTERPLAN.md                # Vision & architecture (protected)
├── CONTRIBUTING.md              # How to contribute (all levels)
├── CODE_OF_CONDUCT.md           # Community standards
├── GOVERNANCE.md                # Decision-making & roles
├── PROJECT-STATUS.md            # Current state & priorities
├── CHANGELOG.md                 # What changed, when, why
├── LICENSE                      # Open-source licence
│
├── docs/
│   ├── SECURITY.md              # Security & data protection patterns (protected)
│   ├── TESTING.md               # Testing standards (protected)
│   ├── GLOSSARY.md              # Domain terminology ↔ code mapping
│   ├── ACCESSIBILITY.md         # WCAG compliance patterns
│   ├── DATA-STANDARDS.md        # Sector data standards (UPRN, etc.)
│   ├── architecture/
│   │   ├── adr/                 # Architecture Decision Records
│   │   └── diagrams/            # System diagrams (C4 model recommended)
│   ├── guides/
│   │   ├── getting-started.md   # Zero-to-running for new contributors
│   │   ├── first-contribution.md # Step-by-step guide to first PR
│   │   ├── housing-context.md   # "Why housing software is different"
│   │   └── ai-assisted-dev.md   # How to use Claude Code with this project
│   ├── design/                  # UX flows, wireframes
│   ├── specs/                   # Technical specifications
│   └── reviews/                 # Code/architecture review reports
│
├── .claude/
│   ├── settings.json            # Hook configuration
│   ├── hooks/                   # Enforcement scripts
│   ├── agents/                  # AI agent definitions
│   ├── skills/                  # AI skill definitions
│   ├── plans/                   # Session execution plans
│   └── handoffs/                # Session handoff documents
│
├── scripts/                     # Developer workflow scripts
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md
    ├── ISSUE_TEMPLATE/          # Bug, feature, good-first-issue templates
    └── workflows/               # CI/CD pipelines
```

### CONTRIBUTING.md

This is the most important file for community health. Structure it by contributor level:

```markdown
# Contributing to [Project Name]

## Everyone Can Contribute
You don't need to write code to make a valuable contribution.

### Ways to Help (No Coding Required)
- **Report bugs**: Something not working? [File an issue](link)
- **Suggest features**: What would make your job easier? [Tell us](link)
- **Review for accuracy**: Does the software match how housing actually works?
- **Improve docs**: Spotted a typo? Know a better way to explain something?
- **Share domain knowledge**: Help us get the glossary right

### Your First Code Contribution
1. Find a [`good-first-issue`](link to filtered issues)
2. Comment on the issue to claim it
3. Follow the [Getting Started Guide](docs/guides/getting-started.md)
4. Open a PR — a maintainer will pair with you on your first one

### Regular Contributors
[Git workflow, testing requirements, PR process — see Sections 11-12]

### Becoming a Maintainer
[Contributor ladder — see Section 4 of the setup guide]
```

### README.md

The README is your shop window. For housing sector projects:

```markdown
# [Project Name]

[One-line description of what this does and for whom]

## Why This Exists
[The housing problem it solves — 2-3 sentences]

## Who It's For
[Specific roles: housing officers, residents, repairs managers, etc.]

## Current Status
[Alpha/Beta/Production] — [link to PROJECT-STATUS.md]

## Quick Start
[3-5 commands to get it running locally]

## Contributing
We welcome contributions from housing professionals at all technical levels.
See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## Governance
This project is stewarded by [organisations]. See [GOVERNANCE.md](GOVERNANCE.md).

## Licence
[AGPL-3.0 / Apache-2.0 / etc.] — see [LICENSE](LICENSE)
```

### Layer-Specific CLAUDE.md Files

Each major code directory gets its own `CLAUDE.md` explaining:
- What this layer owns
- Layer boundaries (what goes here vs. elsewhere) with examples
- Anti-patterns specific to this layer
- Key patterns and conventions

```
backend/CLAUDE.md       # Service boundaries, repository pattern, API conventions
frontend/CLAUDE.md      # Component patterns, state management, accessibility
shared/CLAUDE.md        # Type conventions, what doesn't belong here
```

---

## 6. CLAUDE.md: The Agent Constitution

The root CLAUDE.md is the most important file for AI-assisted development. It shapes every AI agent's behaviour when working on the project. For open-source housing projects, it also serves as a **machine-readable coding standard** that prevents contributors' AI tools from introducing inconsistencies.

### Essential Sections

#### 6.1 Project Overview
Brief description, repo structure, tech stack summary, and — critically — **domain context**:

```markdown
## Domain Context (UK Social Housing)

This software serves registered providers of social housing (housing associations
and local authority housing departments) and their residents. When building features,
understand:

- **Residents are not "users"**: They are people whose homes depend on this software
  working correctly. Treat data with corresponding care.
- **Regulation matters**: Features touching allocations, complaints, safety, or
  financial reporting may have regulatory implications. Check docs/housing-context.md.
- **Accessibility is non-negotiable**: Many residents have disabilities, limited
  digital literacy, or English as a second language. WCAG 2.2 AA minimum.
- **Data sovereignty**: All personal data must remain in UK data centres. No
  third-party services that transfer data outside the UK without explicit DPIA.
```

#### 6.2 Project-Specific Rules (Guardrails)

Non-negotiable patterns. Write them as:
- What to do (with code examples)
- What NOT to do (with code examples)
- Why it matters

```markdown
### Accessibility — CRITICAL
**All interactive elements must be keyboard-accessible and screen-reader-friendly:**

// ❌ WRONG — div with click handler, invisible to assistive technology
<div onClick={handleClick}>Submit</div>

// ✅ RIGHT — semantic button, accessible by default
<button onClick={handleClick}>Submit application</button>

### Personal Data — CRITICAL
**Never log personal data. Use identifiers only:**

// ❌ WRONG
logger.info(`Processing application for ${resident.name} at ${resident.address}`);

// ✅ RIGHT
logger.info(`Processing application ${applicationId} for resident ${residentId}`);
```

#### 6.3 Layer Boundaries Table

Quick-reference for "where does this code go?"

```markdown
| Adding...           | Put in...              | Not in...         |
|---------------------|------------------------|-------------------|
| Business logic      | `/src/services/`       | Controllers       |
| Database query      | `/src/repositories/`   | Services directly |
| API endpoint        | `/src/routes/`         | Service files     |
| Domain validation   | `/src/domain/`         | Controllers       |
| Regulatory rule     | `/src/compliance/`     | Scattered inline  |
```

#### 6.4 Edge Case Awareness

Accumulate hard-won lessons. Each entry should have:
- **What goes wrong** (symptom)
- **Why** (root cause)
- **The fix** (pattern to follow)
- **Reference** (PR or issue that discovered it)

This section grows organically and is one of the highest-value parts of CLAUDE.md.

#### 6.5 Housing-Specific Edge Cases

Dedicate a subsection to domain-specific gotchas:

```markdown
### Housing Domain Edge Cases

- **Tenure types affect everything**: Don't assume a resident has a tenancy. Leaseholders,
  shared owners, and licensees have different rights, obligations, and data requirements.
  Always check `tenure` before applying business rules.

- **Void properties aren't empty**: A void may have ongoing works, legal holds, or
  pending allocations. Status transitions follow a specific workflow.

- **UPRN is not always available**: Some properties (especially new-builds, conversions,
  or temporary accommodation) may not yet have a UPRN. The system must handle this
  gracefully — UPRN is preferred but not required.

- **Names change, addresses change, gender changes**: Design all identity-related
  features to accommodate change. Previous values may need retention for audit
  but should not be displayed to other users.
```

#### 6.6 Development Workflow, Autonomous Task Protocol, Sub-Agent Integration

These sections follow the same structure as the base Chronos guide (see Sections 10-11 for details). Adapt the specifics to your stack and team.

### Writing Style for CLAUDE.md

- **Imperative, not suggestive**: "Always use X" not "Consider using X"
- **Show, don't just tell**: Code examples for every pattern
- **Anti-patterns alongside patterns**: Show the wrong way so agents recognise it
- **Tables for quick reference**: Agents scan faster than they read prose
- **Link to deeper docs**: CLAUDE.md is the index; SECURITY.md, TESTING.md, ADRs hold the detail
- **Domain context is not optional**: Every AI agent working on housing software needs to understand it's not just another CRUD app

---

## 7. Architecture Decision Records (ADRs)

ADRs capture the **why** behind architectural choices. In open-source projects, they're doubly important: they help new contributors understand existing decisions instead of relitigating them.

### ADR Template

```markdown
# ADR-NNN: [Decision Title]

**Status**: Proposed | Accepted | Superseded by ADR-XXX
**Date**: YYYY-MM-DD
**Decision Makers**: [Who was involved — names and organisations]
**Affected Components**: [What parts of the system]

## Context
[What situation or problem prompted this decision?]
[Include any housing-sector-specific context — regulation, data standards, etc.]

## Decision
[What was decided, stated clearly]

## Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|

## Consequences
### Positive
- [Benefits]

### Negative
- [Trade-offs accepted]

### Sector Impact
- [How does this affect interoperability, data standards, or other organisations?]

## Implementation Notes
[Specific patterns or constraints this decision introduces]
```

### ADR Conventions

- **Number sequentially**: `001-`, `002-`, etc.
- **Never delete**: Supersede with a new ADR that references the old one
- **Keep them small**: One decision per ADR
- **Protected files**: ADRs must not be edited by AI agents — changes go through governance
- **Community input**: Significant ADRs should be open for comment (GitHub discussion or issue) for at least 5 working days before acceptance
- **Reference from CLAUDE.md**: List key ADRs so they're discoverable

---

## 8. Security, Data Protection & Testing

Housing software handles personal data about vulnerable people. Security and data protection aren't features — they're prerequisites.

### SECURITY.md

Structure around the attack surfaces relevant to housing software:

```markdown
# Security & Data Protection Patterns
> Read this when: Writing auth, database queries, user input handling, LLM prompts,
> or anything touching personal data.

## Core Principles
1. Never trust user input. Validate everything. Fail securely.
2. Personal data is toxic — collect the minimum, retain only what's necessary,
   encrypt at rest.
3. Audit everything that touches personal data.
4. Assume the attacker is a disgruntled insider with valid credentials.

## 1. Input Validation
[Zod schemas, sanitisation patterns, with code examples]

## 2. Authentication & Authorisation
[JWT handling, role-based access, multi-tenancy isolation]
[Housing-specific: residents must ONLY see their own data; officers see
their organisation's data; never cross-organisation data leakage]

## 3. Personal Data Handling (GDPR / UK GDPR)
### Data Classification
| Category | Examples | Handling |
|----------|----------|---------|
| Public | Organisation name, office address | Standard |
| Internal | Officer names, work email | Access-controlled |
| Personal | Resident name, address, DOB | Encrypted at rest, audit-logged |
| Special Category | Health data, disability, ethnicity | Encrypted, explicit consent, minimal retention |

### Logging Rules
- NEVER log: names, addresses, DOB, NI numbers, health data, financial details
- ALWAYS log: entity IDs, action performed, actor ID, timestamp
- Audit log retention: per your organisation's data retention policy (minimum 6 years
  for housing management records per limitation periods)

### Data Subject Rights
The system must support:
- Right of access (SAR — Subject Access Request)
- Right to rectification
- Right to erasure (with exceptions for legal obligations)
- Right to data portability

## 4. SQL Injection Prevention
[Parameterised queries, repository pattern]

## 5. LLM Prompt Injection Protection
[If applicable — delimiter patterns, output validation, never pass personal data to
third-party LLM APIs without explicit DPIA]

## 6. Multi-Tenancy Isolation
[Every query must be scoped to the organisation. No global queries without explicit
authorisation. Test for cross-tenant data leakage.]
```

### ACCESSIBILITY.md

```markdown
# Accessibility Patterns
> Standard: WCAG 2.2 AA (minimum). AAA where achievable.

## Why This Matters for Housing
- ~20% of social housing residents have a disability
- Many residents have limited digital literacy
- English may not be the first language
- Access to housing services is a fundamental need, not a nice-to-have

## Requirements
- All interactive elements keyboard-accessible
- All images have meaningful alt text (not "image" or "icon")
- Colour contrast ratio minimum 4.5:1 (text), 3:1 (large text/UI)
- Form fields have visible labels (not just placeholders)
- Error messages are specific and actionable
- Screen reader testing with NVDA or VoiceOver on every feature PR

## Testing
- Automated: axe-core in CI pipeline
- Manual: keyboard-only navigation test on every new page/component
- Real: periodic testing with assistive technology users
```

### TESTING.md

```markdown
# Testing Strategy
> Read this when: Writing tests, reviewing coverage

## Philosophy
1. Write tests first (TDD) when requirements are clear
2. Red-Green-Refactor cycle
3. Tests as documentation — a new contributor should understand the feature by reading the tests
4. No work is complete until tests pass

## Test Types
| Type | Purpose | Location | When |
|------|---------|----------|------|
| Unit | Individual functions in isolation | `__tests__/` alongside code | Every PR |
| Integration | API endpoints, database interactions | `/tests/integration/` | Every PR |
| Accessibility | WCAG compliance | `/tests/a11y/` | Every PR with UI changes |
| E2E | Complete user flows | `/tests/e2e/` | Pre-release |

## Coverage Goals
- Target: 80% (statements, lines, branches, functions)
- Critical paths (auth, allocations, payments): 95%+
- Accessibility: 100% of pages pass axe-core automated checks

## Test Structure (Arrange-Act-Assert)
[Examples in your language/framework]

## Running Tests
[Commands for each layer]
```

---

## 9. Enforcement Layer: Hooks & Guardrails

Documentation is aspirational; enforcement is real. The gap between "we should" and "the system blocks you if you don't" is where quality lives.

This is especially important in open-source projects where contributors have varying experience levels. **Guardrails protect new contributors from making mistakes that experienced developers avoid by habit.**

### Claude Code Hooks

Configure in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/restrict-commands.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### Protected Files Hook

`.claude/hooks/protect-files.sh` — blocks AI edits on files that need human review:

```bash
#!/bin/bash
# Blocks edits to protected files. Changes → handoff plan instead.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
[[ -z "$FILE_PATH" ]] && exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
REL_PATH="${FILE_PATH#$PROJECT_DIR/}"

BLOCKED=false
REASON=""

case "$REL_PATH" in
  # Governance & direction
  CLAUDE.md|*/CLAUDE.md)          BLOCKED=true; REASON="Agent instruction file" ;;
  MASTERPLAN.md)                  BLOCKED=true; REASON="Project direction" ;;
  GOVERNANCE.md)                  BLOCKED=true; REASON="Governance document" ;;
  CODE_OF_CONDUCT.md)             BLOCKED=true; REASON="Code of conduct" ;;
  LICENSE)                        BLOCKED=true; REASON="Licence file" ;;

  # Standards
  docs/architecture/adr/*)        BLOCKED=true; REASON="Architecture decision record" ;;
  docs/SECURITY.md)               BLOCKED=true; REASON="Security patterns" ;;
  docs/TESTING.md)                BLOCKED=true; REASON="Testing standards" ;;
  docs/ACCESSIBILITY.md)          BLOCKED=true; REASON="Accessibility standards" ;;
  docs/DATA-STANDARDS.md)         BLOCKED=true; REASON="Data standards" ;;

  # Infrastructure & config
  .gitignore)                     BLOCKED=true; REASON="Git configuration" ;;
  .github/*)                      BLOCKED=true; REASON="CI/CD configuration" ;;
  .env|.env.*|*.env|*.env.*)      BLOCKED=true; REASON="Environment/secrets" ;;
  Dockerfile*|*/Dockerfile*)      BLOCKED=true; REASON="Infrastructure" ;;
  docker-compose*|*/docker-compose*) BLOCKED=true; REASON="Infrastructure" ;;
  **/migrations/*)                BLOCKED=true; REASON="Database migration" ;;
esac

if [[ "$BLOCKED" == "true" ]]; then
  echo "Protected file — document needed changes in a handoff plan instead. ($REASON: $REL_PATH)" >&2
  exit 2
fi
exit 0
```

### Restricted Commands Hook

`.claude/hooks/restrict-commands.sh` — blocks destructive bash commands:

```bash
#!/bin/bash
# Blocks dangerous commands. Restricted ops → handoff plan.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
[[ -z "$COMMAND" ]] && exit 0

STRIPPED=$(echo "$COMMAND" | sed '/<<.*EOF/,/^EOF/d')

# Force push
echo "$STRIPPED" | grep -qE 'git\s+push\s+.*--force|git\s+push\s+.*-f\b' && \
  { echo "Use normal git push only." >&2; exit 2; }

# Hard reset
echo "$STRIPPED" | grep -qE 'git\s+reset\s+--hard' && \
  { echo "Use git stash push -u instead." >&2; exit 2; }

# git clean without dry-run
echo "$STRIPPED" | grep -qE 'git\s+clean\s+.*-[a-zA-Z]*f' && \
  ! echo "$STRIPPED" | grep -qE 'git\s+clean\s+.*-[a-zA-Z]*n' && \
  { echo "Run git clean -n first." >&2; exit 2; }

# Skip hooks
echo "$STRIPPED" | grep -qE 'git\s+.*--no-verify' && \
  { echo "Fix the hook failure instead of skipping." >&2; exit 2; }

# Database migrations
echo "$STRIPPED" | grep -qE 'migrate:up|migrate:down' && \
  { echo "Document migration in handoff plan." >&2; exit 2; }

# Production deployment
echo "$STRIPPED" | grep -qE 'railway\s+up|fly\s+deploy|heroku\s+.*push' && \
  { echo "Document deployment in handoff plan." >&2; exit 2; }

exit 0
```

**Make both executable:** `chmod +x .claude/hooks/*.sh`

### Why Hooks Matter for Open-Source

| Layer | What It Does | Without It |
|-------|-------------|------------|
| CLAUDE.md rules | Tells agents the standards | Agent drifts in long sessions |
| Hooks | Physically blocks violations | Violation is impossible regardless of contributor experience |
| CI checks | Catches what hooks miss (linting, tests, types) | Broken code merges |
| PR review | Human judgement on domain accuracy | Technically correct but operationally wrong code ships |

---

## 10. AI-Assisted Development & Multi-Agent Coordination

AI tools (Claude Code, GitHub Copilot, etc.) accelerate development but need guardrails — especially in projects where contributors have different skill levels and the domain (housing) has real consequences for mistakes.

### AI as a Learning Accelerator

AI-assisted development is particularly powerful for sector skill-building:

- **New contributors** can use Claude Code to understand existing code, get explanations, and have their first PR guided
- **Domain experts** can describe what they need in housing terms and get technical implementation suggestions
- **Maintainers** can use autonomous agent sessions for routine tasks, freeing time for mentoring

### Claude Code Setup for Contributors

Include in `docs/guides/ai-assisted-dev.md`:

```markdown
# AI-Assisted Development Guide

## Getting Started with Claude Code
1. Install: [link to installation]
2. The project's CLAUDE.md automatically teaches Claude our patterns
3. Start a session in the project directory — Claude reads the codebase context

## What Claude Can Help With
- "Explain what this function does" — understand existing code
- "Show me similar patterns in the codebase" — learn by example
- "Write a test for this function" — TDD guidance
- "Review my changes" — pre-PR feedback

## What Claude Cannot Do (Hooks Enforce This)
- Edit protected files (governance docs, ADRs, security standards)
- Run destructive git commands (force push, hard reset)
- Execute database migrations or production deployments
- These all require human review — Claude will create a handoff plan instead

## Tips for New Contributors
- Ask Claude to explain WHY, not just WHAT — "Why does this use a repository
  pattern instead of direct SQL?"
- If Claude suggests something that doesn't match the housing domain, trust
  your domain knowledge and push back
- Use Claude to write tests first, then implement — it enforces TDD naturally
```

### Multi-Agent Coordination

If multiple people (or agents) work on the project simultaneously, prevent conflicts:

```
Session Start:
  1. Check for active work: look at open PRs and in-progress issues
  2. Claim your issue before starting work
  3. Note which files you'll touch in the issue comments

Before Touching Shared Files (types, configs, migrations):
  1. Check for other open PRs touching the same files
  2. If overlap: coordinate in the issue comments or yield
  3. Work quickly on shared files — merge within hours, not days

Session End:
  1. Push your branch
  2. Update issue status
  3. If handing off: document state in issue comments
```

### Autonomous Agent Sessions

For maintainers running AI agents autonomously (e.g., routine refactoring, test backfill):

1. **Plan first**: Agent writes a plan file before any code changes
2. **Worktree isolation**: Agent works in a git worktree, never on main
3. **TDD mandatory**: Tests before implementation
4. **Draft PR**: Agent creates a draft PR for human review
5. **Protected files respected**: Hooks block governance docs, migrations, deployments
6. **Handoff plan**: Agent documents anything that needs human action

See Section 9 for the enforcement hooks that make this safe.

---

## 11. Git Workflow & Branch Strategy

### Branch Naming

```
feature/  — New functionality
fix/      — Bug fixes
refactor/ — Code restructuring (no behaviour change)
docs/     — Documentation only
test/     — Test additions/fixes
chore/    — Tooling, dependencies, config
a11y/     — Accessibility improvements
```

### Commit Convention

Conventional commits for automated changelogs and clear history:

```
feat(allocations): add bidding preference weighting
fix(repairs): handle void properties without UPRN
docs(glossary): add tenure type definitions
refactor(auth): extract role-based access checks
test(compliance): add Decent Homes assessment edge cases
chore(deps): update express to 4.19
a11y(forms): add visible labels to application form
```

### Rules

- Never commit directly to `main` — always via PR
- Small PRs preferred (< 400 lines changed)
- Rebase onto main before opening PR
- Reference issue number in PR description
- First-time contributors: a maintainer will merge for you

### PR Template

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Issue Reference
Closes #

## Summary
<!-- 1-3 bullet points: what changed and why -->
-

## Test Plan
- [ ] Tests pass (`npm test`)
- [ ] Linting passes (`npm run lint`)
- [ ] Accessibility checks pass (`npm run test:a11y`) — if UI changes
- [ ] Manual testing done

## Checklist
- [ ] Issue updated to "in review"
- [ ] Docs updated (if applicable)
- [ ] Glossary updated (if new domain terms introduced)
- [ ] Migration included (if schema changed)

## Contributor Level
<!-- Helps reviewers calibrate feedback. No judgement — we all start somewhere. -->
- [ ] This is my first PR to this project
- [ ] I'm a regular contributor
- [ ] I'm a maintainer

## Learning Reflection (optional)
<!-- What did you learn? What was confusing? -->
```

---

## 12. CI/CD Pipeline

### Minimum Viable CI

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test

  accessibility:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'ui')
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:a11y
```

### Issue Reference Check

```yaml
# .github/workflows/pr-check.yml
name: PR Check
on:
  pull_request:
    types: [opened, edited]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check for issue reference
        run: |
          BODY="${{ github.event.pull_request.body }}"
          if ! echo "$BODY" | grep -qE '(Closes|Fixes|Resolves) #[0-9]+'; then
            echo "PR must reference an issue (e.g., 'Closes #123')"
            exit 1
          fi
```

### Dependency Security Scanning

```yaml
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
```

---

## 13. Developer Experience Scripts

Good DX scripts reduce friction. For open-source projects, they also **standardise** the setup experience across different contributors' machines.

### First-Time Setup

```bash
#!/bin/bash
# scripts/setup.sh — Run once when first cloning the repo
set -e
echo "=== Project Setup ==="

# Check prerequisites
command -v node &>/dev/null || { echo "Install Node.js 18+ first"; exit 1; }
command -v docker &>/dev/null || { echo "Install Docker first"; exit 1; }

# Install dependencies
npm install

# Set up environment
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit with your local values"
fi

# Start infrastructure
docker compose up -d

# Wait for services
echo "Waiting for database..."
sleep 3

# Run migrations
npm run migrate:up

echo "=== Setup Complete ==="
echo "Run 'npm run dev' to start developing"
```

### Session Scripts

```bash
# scripts/start-dev.sh
#!/bin/bash
echo "=== Pre-flight Checks ==="
echo "Branch: $(git branch --show-current)"
git status --short
docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null
echo "=== Ready ==="

# scripts/health-check.sh
#!/bin/bash
echo "=== Health Check ==="
echo "Branch: $(git branch --show-current)"
docker compose ps 2>/dev/null
# Adapt ports to your stack
for port in 3000 5173; do
  lsof -iTCP:$port -sTCP:LISTEN &>/dev/null && echo "✓ :$port" || echo "✗ :$port"
done
echo "=== Done ==="
```

---

## 14. Task Tracking & Community Coordination

### GitHub Issues as the Source of Truth

For open-source housing projects, GitHub Issues is the most accessible tracker:

- Contributors already have GitHub accounts
- No additional tooling to learn
- Issues are public — transparency for the sector

### Labels System

```
Type:      bug, enhancement, documentation, accessibility, security
Priority:  P0-critical, P1-high, P2-medium, P3-low
Skill:     good-first-issue, help-wanted, mentor-available
Domain:    allocations, repairs, compliance, resident-facing, officer-facing
Status:    needs-triage, ready, in-progress, in-review, blocked
```

### MCP Integration (for maintainers using Claude Code)

```json
// .mcp.json
{
  "mcpServers": {
    "vibe-kanban": {
      "command": "npx",
      "args": ["-y", "vibe-kanban", "--mcp"]
    }
  }
}
```

### Task Completion Flow

```
1. Issue exists and is labelled → contributor claims it
2. Work on feature branch → reference issue in commits
3. Before PR → update issue with "PR incoming"
4. PR opened → references issue with "Closes #NNN"
5. PR reviewed and merged → issue auto-closes
6. If new scope discovered → create new issue before proceeding
```

---

## 15. Deployment & Operations

### Data Hosting (UK Housing Requirement)

Personal data must remain in UK data centres. When choosing hosting:

| Provider | UK Region | Notes |
|----------|-----------|-------|
| AWS | eu-west-2 (London) | Most services available |
| Azure | UK South / UK West | Good for orgs already on Microsoft |
| GCP | europe-west2 (London) | Fewer services than AWS |
| Railway | EU (check specific region) | Simple but verify data location |
| Fly.io | lhr (London) | Good for small deployments |

**In your infrastructure config, pin the region explicitly.** Don't rely on defaults.

### Database Migration Protocol

Migrations are high-risk. In open-source projects with multiple deploying organisations:

```
1. Create migration file — can be automated, included in PR
2. Review migration SQL — maintainer reviews for data safety
3. Test against staging — the PR author or reviewer runs it
4. Document rollback — every UP migration needs a DOWN
5. Release notes — CHANGELOG entry explaining the migration
6. Each deploying organisation runs at their own pace
```

### Deployment Gotchas Log

Maintain in CLAUDE.md — captures lessons so they're not repeated:

```markdown
| Gotcha | What Happens | Fix |
|--------|-------------|-----|
| [Specific to your deployment] | [Symptom] | [Resolution] |
```

---

## 16. Collaboration Protocol

This section defines how external contributors, partner organisations, and AI agents collaborate with the project maintainer(s).

### For Housing Organisations Wanting to Contribute

```
1. INTRODUCE YOURSELVES
   - Open a GitHub Discussion or email the maintainers
   - Tell us: your organisation, what you use/need, what you can contribute
   - We'll invite you to the next community call

2. START SMALL
   - File issues from your operational experience
   - Review existing features for domain accuracy
   - Pick up a good-first-issue to learn the codebase
   - No commitment required — contribute what you can

3. GO DEEPER
   - Assign a champion within your organisation (part-time is fine)
   - The champion attends community calls and represents your org's needs
   - Contributors from your org follow the contributor ladder (Section 4)
   - We pair with your team on their first PRs

4. SHAPE DIRECTION
   - After sustained contribution, join the steering group
   - Propose features via the ADR process
   - Help prioritise the roadmap based on sector needs
```

### For Individual Contributors

```
1. READ: README.md → CONTRIBUTING.md → docs/guides/getting-started.md
2. SETUP: Run scripts/setup.sh
3. EXPLORE: Browse good-first-issues, attend a community call
4. CLAIM: Comment on an issue to claim it
5. BUILD: Work on a branch, write tests, open a PR
6. LEARN: Read review feedback, ask questions, iterate
7. GROW: Move up the contributor ladder as you gain confidence
```

### For AI Agents (Claude Code, Copilot, etc.)

```
1. CLAUDE.md is your constitution — read it first, follow it always
2. Hooks enforce protected files and restricted commands — don't fight them
3. Domain context matters — housing software isn't generic CRUD
4. When unsure about domain accuracy, flag it for human review
5. Write tests before implementation (TDD)
6. Create handoff plans for anything you can't do (migrations, deployments)
7. Your PRs are always drafts — a human maintainer reviews and merges
```

### Communication Channels

| Channel | Purpose | Cadence |
|---------|---------|---------|
| GitHub Issues | Bug reports, feature requests, task tracking | Continuous |
| GitHub Discussions | Questions, ideas, RFC-style proposals | Continuous |
| Community Call | Demo, discuss priorities, welcome new contributors | Monthly |
| Maintainer Sync | Technical coordination, PR review queue, mentoring | Fortnightly |
| Steering Group | Roadmap, governance, sector strategy | Quarterly |

### Response Time Commitments

| Type | Target Response |
|------|----------------|
| Security vulnerability | 24 hours (private disclosure) |
| Bug report | 5 working days (triage) |
| Feature request | Next community call (discussion) |
| PR from new contributor | 48 hours (review) |
| PR from regular contributor | 5 working days (review) |
| Good-first-issue PR | 48 hours (review — protect momentum) |

### Intellectual Property

- All contributions are made under the project's open-source licence
- Contributors retain copyright on their contributions but grant the licence
- Include a Developer Certificate of Origin (DCO) sign-off requirement:
  - `git commit -s` adds `Signed-off-by: Name <email>` to the commit
  - This certifies the contributor has the right to submit the code under the licence
- No Contributor Licence Agreement (CLA) — the DCO is sufficient and less intimidating

---

## 17. Setup Checklist

### Phase 1: Foundation (Day 1)

- [ ] Create repository with `.gitignore` and `LICENSE` (AGPL-3.0 recommended)
- [ ] Write `MASTERPLAN.md` — vision, architecture, sector context
- [ ] Write root `CLAUDE.md` — project overview, domain context, guardrails
- [ ] Write `README.md` — shop window for the project
- [ ] Create directory structure (see Section 5)
- [ ] Create `scripts/setup.sh` for first-time environment setup
- [ ] Create `.env.example` with all required variables

### Phase 2: Community (Day 1-2)

- [ ] Write `CONTRIBUTING.md` — paths for all contributor levels
- [ ] Write `CODE_OF_CONDUCT.md` — Contributor Covenant + housing norms
- [ ] Write `GOVERNANCE.md` — roles, decisions, meetings
- [ ] Create `.github/ISSUE_TEMPLATE/` — bug, feature, good-first-issue
- [ ] Create `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] Create `docs/GLOSSARY.md` — seed with core domain terms

### Phase 3: Standards (Day 2-3)

- [ ] Write `docs/SECURITY.md` — input validation, auth, GDPR, personal data
- [ ] Write `docs/TESTING.md` — philosophy, structure, commands
- [ ] Write `docs/ACCESSIBILITY.md` — WCAG patterns, testing approach
- [ ] Write `docs/DATA-STANDARDS.md` — UPRN, sector data conventions
- [ ] Create first ADR (`001-*`) documenting foundational architecture
- [ ] Write layer-specific `CLAUDE.md` files for each major directory

### Phase 4: Enforcement (Day 3)

- [ ] Create `.claude/settings.json` with hook configuration
- [ ] Create `.claude/hooks/protect-files.sh`
- [ ] Create `.claude/hooks/restrict-commands.sh`
- [ ] `chmod +x .claude/hooks/*.sh`
- [ ] Test hooks: verify protected files are blocked

### Phase 5: CI/CD (Day 3-4)

- [ ] Create `.github/workflows/ci.yml` — lint, typecheck, test
- [ ] Create `.github/workflows/pr-check.yml` — issue reference check
- [ ] Add accessibility CI job (axe-core or equivalent)
- [ ] Add dependency security scanning
- [ ] Verify CI runs on PRs to main

### Phase 6: DX & Tooling (Day 4)

- [ ] Create `scripts/start-dev.sh`, `scripts/health-check.sh`
- [ ] Configure `.mcp.json` for task tracker integration
- [ ] Write `docs/guides/getting-started.md` — zero-to-running
- [ ] Write `docs/guides/first-contribution.md` — first PR walkthrough
- [ ] Write `docs/guides/ai-assisted-dev.md` — Claude Code guide
- [ ] Seed 3-5 `good-first-issue` tasks

### Phase 7: Community Launch (Day 5+)

- [ ] Announce on relevant channels (housing sector forums, social media)
- [ ] Schedule first community call
- [ ] Identify 2-3 early contributors from partner organisations
- [ ] Pair with first external contributor on their first PR
- [ ] Retrospect and adjust processes after first month

---

## 18. Principles

1. **Domain expertise is a first-class contribution.** The housing officer who says "that's not how allocations works" is as valuable as the developer who fixes the code.

2. **Quality protects contributors.** Tests, linting, type checking, and hooks are safety nets that let people contribute without fear. The more automated the guardrails, the more welcoming the project.

3. **Documentation is infrastructure.** Every hour spent on good docs saves ten hours of confused contributors. Every missing explanation is a barrier to entry.

4. **Enforcement over aspiration.** If a rule matters, enforce it with a hook or CI check. Documented-but-unenforced rules erode trust.

5. **Small PRs, fast reviews.** Nothing kills contributor momentum faster than a PR sitting unreviewed. 48 hours for new contributors. Always.

6. **Skills development is the long game.** The software you build today might be superseded. The capacity you build in the sector compounds. Invest in people.

7. **Openness requires structure.** Open-source without governance is a hobby project. Governance without openness is a vendor. Both together build sector-owned digital infrastructure.

8. **Start lean, add process when it hurts.** Not every section of this guide is needed on day one. Start with CLAUDE.md + hooks + CI + CONTRIBUTING.md, then add layers as the project and community grow.

9. **Accessibility is non-negotiable.** The people this software serves include some of the most vulnerable in society. Build for them first.

10. **Data protection is a design constraint, not an afterthought.** UK GDPR, the Housing Act, and basic decency all demand that personal data is handled with care. Bake it in from the start.
