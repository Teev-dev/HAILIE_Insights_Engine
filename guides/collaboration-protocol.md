# Collaboration Protocol

How to work with us — whether you're a housing organisation, an individual contributor, a domain expert, or an AI agent. This protocol applies to any open-source project built by the UK housing sector using the [Rigorous Project Setup Guide](rigorous-project-setup-guide.md).

---

## Table of Contents

1. [Who This Is For](#1-who-this-is-for)
2. [For Housing Organisations](#2-for-housing-organisations)
3. [For Individual Contributors](#3-for-individual-contributors)
4. [For Domain Experts (Non-Coders)](#4-for-domain-experts-non-coders)
5. [For AI Agents](#5-for-ai-agents)
6. [Contributor Ladder](#6-contributor-ladder)
7. [How We Work Together Day-to-Day](#7-how-we-work-together-day-to-day)
8. [Communication Channels & Cadence](#8-communication-channels--cadence)
9. [Review Standards & Response Times](#9-review-standards--response-times)
10. [Pair Programming](#10-pair-programming)
11. [Handling Disagreements](#11-handling-disagreements)
12. [Intellectual Property & Licensing](#12-intellectual-property--licensing)
13. [Security Disclosure](#13-security-disclosure)
14. [Leaving & Succession](#14-leaving--succession)

---

## 1. Who This Is For

This protocol covers four types of collaborator. You might be more than one.

| Type | You Are... | You Bring... |
|------|-----------|-------------|
| **Housing Organisation** | A housing association, ALMO, or local authority housing team | Operational knowledge, user needs, testing capacity, potential developer time |
| **Individual Contributor** | A developer, designer, tester, or student | Technical skills at any level, from first PR to architecture |
| **Domain Expert** | A housing officer, repairs manager, allocations specialist, resident | Deep knowledge of how housing actually works — the most valuable and rarest input |
| **AI Agent** | Claude Code, GitHub Copilot, or another AI dev tool | Speed, consistency, tireless test-writing — within guardrails |

You don't need to write code to collaborate. Some of the most valuable contributions are:

- "That's not how allocations works — here's what actually happens"
- "This screen would confuse our residents because..."
- "We tried something similar and it failed because..."
- "Our organisation would use this if it also handled..."

---

## 2. For Housing Organisations

### Getting Started

```
Phase 1: CONNECT
├── Open a GitHub Discussion or email maintainers
├── Tell us: your organisation, what you need, what you might contribute
├── We'll invite you to the next community call
└── Timeline: anytime

Phase 2: EXPLORE
├── File issues from your operational experience
├── Review existing features for domain accuracy
├── Have your team try the software (staging environment available)
├── Send us feedback — even "this doesn't make sense" is valuable
└── Timeline: first 1-2 months

Phase 3: CONTRIBUTE
├── Assign a champion (part-time is fine — even 2 hours/week)
├── Champion attends community calls and represents your org's needs
├── Your team picks up good-first-issues to learn the codebase
├── We pair with your developers on their first PRs
└── Timeline: months 2-4

Phase 4: CO-OWN
├── After sustained contribution, join the steering group
├── Propose features via the ADR process
├── Help prioritise the roadmap based on sector needs
├── Mentor other organisations joining later
└── Timeline: 6+ months of active participation
```

### What We Ask of Participating Organisations

- **One named champion** who can speak for your org's needs and relay information internally
- **Honest feedback** about whether the software matches your operational reality
- **Patience** with the open-source process — it's slower than buying a product but you get something you actually own
- **Willingness to test** pre-release features against your real workflows (in staging, not production)

### What You Get

- Software that reflects your actual needs, not a vendor's assumptions
- Technical capacity building within your team
- A seat at the table for roadmap decisions
- Reduced dependency on proprietary vendors
- A community of housing organisations facing the same challenges

### Data & Privacy Commitments

- Your organisation's data never leaves your control — you deploy your own instance
- No telemetry, analytics, or data collection by the project
- The open-source code is auditable — you can verify what it does
- Security vulnerabilities are disclosed responsibly (see Section 13)

---

## 3. For Individual Contributors

### Your First Day

```
1. READ    → README.md → CONTRIBUTING.md → docs/guides/getting-started.md
2. SETUP   → git clone, then run scripts/setup.sh
3. EXPLORE → Browse issues labelled `good-first-issue`
             Attend a community call (monthly — low-pressure, cameras optional)
4. CLAIM   → Comment on an issue: "I'd like to work on this"
             A maintainer will acknowledge within 48 hours
5. BRANCH  → Create a feature branch from main
6. BUILD   → Write tests first, then implement
7. PR      → Open a pull request referencing the issue
8. LEARN   → Read review feedback, ask questions, iterate
9. MERGE   → A maintainer merges when ready
10. GROW   → Pick up the next issue. You're a contributor now.
```

### What to Expect on Your First PR

- A maintainer will review within **48 hours**
- Feedback will be **constructive and educational** — we explain *why*, not just *what*
- You'll likely get 1-3 rounds of feedback. This is normal and healthy.
- If you're stuck, say so in the PR comments. We'll help.
- **Pair programming is available** — ask and a maintainer will schedule time

### What We Expect from You

- Follow the git workflow (branch from main, conventional commits, reference issues)
- Write tests for your changes (we'll help if you're new to testing)
- Be respectful of other contributors and the code of conduct
- Ask when you're unsure — there are no stupid questions in this project
- If you claim an issue and can't finish it, that's fine — just unclaim it so others can pick it up

### Don't Know Where to Start?

| Interest | Look For |
|----------|----------|
| "I want to write code" | `good-first-issue` label |
| "I want to learn testing" | `test` label + `help-wanted` |
| "I know housing, not code" | `domain-review-needed` label |
| "I want to improve docs" | `documentation` label |
| "I want to fix bugs" | `bug` label + `help-wanted` |
| "I want to improve accessibility" | `accessibility` label |

---

## 4. For Domain Experts (Non-Coders)

**You are the most valuable contributor we have.** Software developers can learn to code housing features. They cannot learn 15 years of allocations experience from a tutorial.

### How You Can Contribute Without Writing Code

#### Review Features for Domain Accuracy

When a new feature is proposed or built, we need someone who knows the domain to answer:

- "Is this how it actually works in practice?"
- "What edge cases are we missing?"
- "Would this confuse a housing officer / resident?"
- "Does this comply with [relevant regulation]?"

We'll tag issues and PRs with `domain-review-needed` when we need your input.

#### Write User Stories

The best feature requests come from people who do the job. A user story from you might look like:

```
As a housing officer processing a mutual exchange,
I need to verify that both properties meet the Decent Homes Standard
because a mutual exchange cannot proceed if either property fails.

Edge cases:
- What if one property has outstanding repairs that would bring it to standard?
- What if the properties are in different local authorities?
- What if one tenant has an introductory tenancy (different rights)?
```

This is gold. No developer can write this without you.

#### Build the Domain Glossary

Help us maintain `docs/GLOSSARY.md` — ensuring the codebase uses correct housing terminology and that technical documentation is accurate.

#### Test Pre-Release Features

Try new features against your real workflows (in a staging environment) and tell us:
- What worked as expected
- What was confusing
- What's missing
- What would make your colleagues reject this

#### Attend Community Calls

Share what you're seeing in the sector. Upcoming regulatory changes, common pain points, trends in how housing is managed — this shapes the roadmap.

### How to Get Started as a Domain Expert

1. **GitHub account** — free, takes 2 minutes
2. **Watch the repository** — you'll get notifications when domain review is needed
3. **Join a community call** — introduce yourself, hear what's being built
4. **Comment on issues** — your operational perspective is always welcome
5. **File issues** — "the system should handle X because in practice Y happens"

No git, no code, no terminal required.

---

## 5. For AI Agents

AI agents (Claude Code, GitHub Copilot, Cursor, etc.) are collaborators with specific capabilities and constraints. This section defines how they operate within the project.

### Constitution

1. **CLAUDE.md is law.** Read it first. Follow it always. It contains domain context, patterns, guardrails, and anti-patterns specific to this project.

2. **Domain context is mandatory.** Housing software is not generic CRUD. Before implementing a feature:
   - Read `docs/GLOSSARY.md` for terminology
   - Read `docs/guides/housing-context.md` for operational background
   - Check if the feature has regulatory implications

3. **Hooks are non-negotiable.** The project uses enforcement hooks that block:
   - Edits to protected files (governance docs, ADRs, security standards, migrations)
   - Destructive git commands (force push, hard reset, clean without dry-run)
   - Database migrations and production deployments
   - Don't fight them. Create a handoff plan instead.

4. **TDD is required.** Write tests before implementation. Tests are the proof that code does what was intended, especially important when a human didn't write the code.

5. **PRs are always drafts.** AI-generated code is reviewed by a human maintainer before merging. No exceptions.

6. **When unsure, flag it.** If you're uncertain about:
   - Domain accuracy ("Is this how allocations works?")
   - Data protection implications ("Should this be logged?")
   - Accessibility ("Is this keyboard-navigable?")

   Flag it explicitly in the PR description. A domain expert or maintainer will review.

### Autonomous Sessions

When an AI agent operates without real-time human supervision:

```
1. PLAN     → Write a plan file before any code changes
2. ISOLATE  → Work in a git worktree, never on main
3. TEST     → Red-Green-Refactor — tests before implementation
4. PR       → Create a DRAFT PR with full context
5. HANDOFF  → Document anything that needs human action
6. CLEAN UP → Update task status, note what was done and what remains
```

### What AI Agents Must Never Do

| Action | Why | Instead |
|--------|-----|---------|
| Edit governance documents | These require human consensus | Create handoff plan |
| Run database migrations | Irreversible, affects live data | Document in handoff plan |
| Deploy to production | Requires human verification | Document in handoff plan |
| Skip tests or hooks | Undermines quality guarantees | Fix the underlying issue |
| Guess at domain logic | Housing rules have legal implications | Flag for domain review |
| Log personal data | GDPR violation | Use entity IDs only |
| Commit to main | Bypasses review process | Use feature branch + PR |

### AI + Human Pairing

The most effective pattern for AI-assisted housing software development:

```
Human (Domain Expert)          AI Agent (Technical)
─────────────────────          ─────────────────────
Describes the feature          Implements the code
Reviews for accuracy           Writes tests
Validates edge cases           Handles boilerplate
Checks regulatory fit          Ensures patterns are followed
Approves and merges            Creates PR as draft
```

This pairing lets domain experts contribute technical features without writing code, while ensuring AI output is grounded in operational reality.

---

## 6. Contributor Ladder

A clear progression from observer to maintainer. Movement up the ladder is based on **sustained contribution and demonstrated judgement**, not on coding speed or volume.

### Level 0: Observer

**What you do:** Watch the repo, read issues and PRs, attend community calls.

**What you learn:** How the project works, what's being built, how decisions are made.

**How to progress:** Start commenting on issues — questions, operational context, feedback.

### Level 1: Reporter

**What you do:** File issues (bugs, feature requests), suggest improvements, review docs.

**Skills you're building:** Clear problem articulation, GitHub basics.

**How to progress:** Your issues consistently contain actionable information. Other contributors reference your reports.

### Level 2: Documenter

**What you do:** Write or improve docs, maintain the glossary, add housing context to technical decisions, review features for domain accuracy.

**Skills you're building:** Technical writing, bridging domain ↔ technical language.

**How to progress:** Documentation you write reduces questions from new contributors. You can explain technical decisions in housing terms.

### Level 3: First-Time Coder

**What you do:** Pick up `good-first-issue` tasks. Pair with a maintainer on first PR. Write tests.

**Skills you're building:** Git workflow, testing, reading existing code, writing code that follows project patterns.

**How to progress:** You've shipped 3-5 PRs that were merged with decreasing amounts of feedback.

### Level 4: Regular Contributor

**What you do:** Take on `help-wanted` issues independently. Review others' PRs for domain accuracy and code quality. Mentor Level 3 contributors.

**Skills you're building:** Architecture awareness, code review, mentoring.

**How to progress:** You're consistently producing quality work. Other contributors trust your reviews. You understand the architectural rationale (ADRs) behind the codebase.

### Level 5: Maintainer

**What you do:** Merge authority on `main`. Shape technical direction. Mentor contributors at all levels. Represent the project's technical standards.

**How you got here:** Nominated by an existing maintainer, confirmed by the steering group. Based on:
- Sustained contribution over 6+ months
- Demonstrated good judgement (not just volume)
- Ability to mentor others
- Understanding of the housing domain, not just the code

**Responsibilities:**
- Review PRs within response time commitments (Section 9)
- Maintain the quality bar (tests, accessibility, security, domain accuracy)
- Be welcoming to new contributors — your first review sets their impression of the project
- Attend maintainer syncs (fortnightly)
- Raise architectural concerns via ADR process, not unilateral changes

### Recognition

Every release includes a contributors section in the CHANGELOG. All contribution types are recognised — not just code.

---

## 7. How We Work Together Day-to-Day

### Claiming Work

1. Browse open issues. Filter by labels that match your interest and level.
2. Comment "I'd like to work on this" on the issue.
3. A maintainer will assign it to you within 48 hours.
4. If you haven't started within 2 weeks, we'll check in. If you can't continue, unclaim it — no judgement.

### Branches and PRs

```
main (protected — no direct commits)
  └── feature/allocations-bidding-weight    ← your work happens here
  └── fix/void-property-uprn-handling
  └── docs/glossary-tenure-types
```

- One branch per issue
- One issue per PR (keeps reviews focused)
- Reference the issue: `Closes #123`
- Keep PRs under 400 lines where possible

### Code Review Culture

Code review is **teaching, not gatekeeping**. Our review norms:

**For reviewers:**
- Explain *why*, not just *what* — "This should use a parameterised query because [SQL injection risk]" not "Change this"
- Distinguish between blocking issues and suggestions: prefix with `nit:` for non-blocking feedback
- Acknowledge good work — "Nice approach here, I hadn't considered that edge case"
- If a PR from a new contributor needs major rework, offer to pair rather than leaving a wall of comments
- Review the domain accuracy, not just the code quality

**For PR authors:**
- Don't take feedback personally — it's about the code, not you
- Ask questions if feedback is unclear
- If you disagree with feedback, explain your reasoning — healthy technical discussion is good
- Mark conversations as resolved when you've addressed them

### Working on Shared Files

Some files are touched by many features (shared types, config, migrations). When working on these:

1. Check for open PRs that touch the same files
2. If overlap: coordinate in the issue comments or PR comments
3. Keep your changes to shared files minimal and merge quickly
4. If two PRs conflict: the one opened first has priority; the second rebases after merge

---

## 8. Communication Channels & Cadence

| Channel | Purpose | Who | Cadence |
|---------|---------|-----|---------|
| **GitHub Issues** | Bug reports, feature requests, task tracking | Everyone | Continuous |
| **GitHub Discussions** | Questions, ideas, proposals, show-and-tell | Everyone | Continuous |
| **Community Call** | Demo new features, discuss priorities, welcome newcomers | Everyone (open) | Monthly |
| **Maintainer Sync** | PR queue, technical coordination, mentoring pipeline | Maintainers | Fortnightly |
| **Steering Group** | Roadmap, governance, sector strategy, budget | Steering group | Quarterly |

### Community Call Format (60 minutes)

```
0-5 min    Welcome, new faces introduce themselves
5-20 min   Demo: what shipped since last call
20-35 min  Discussion: upcoming priorities, open questions
35-50 min  Lightning talks: anyone can share something (2-5 min each)
50-60 min  What's next: who's working on what, where help is needed
```

Calls are recorded (with consent) and notes posted to GitHub Discussions.

### Asynchronous by Default

Most collaboration happens asynchronously via GitHub. This is intentional:

- Contributors are in different organisations with different schedules
- Housing professionals contribute around their day jobs
- Async-first creates a written record that future contributors can reference
- Time zones and working patterns shouldn't be barriers

Synchronous channels (calls, pairing sessions) are for:
- Complex technical discussions that would be painful in text
- Mentoring and skill transfer
- Building relationships and trust
- Resolving disagreements that have stalled in text

---

## 9. Review Standards & Response Times

### Response Time Commitments

| Type | Target | Why This Matters |
|------|--------|-----------------|
| **Security vulnerability** | 24 hours (private disclosure) | Resident data may be at risk |
| **Good-first-issue PR** | 48 hours | Protect new contributor momentum — slow reviews kill engagement |
| **PR from new contributor** | 48 hours | First impression sets the tone |
| **Bug report** | 5 working days (triage) | Acknowledge, label, assess severity |
| **PR from regular contributor** | 5 working days | Trusted contributors can wait slightly longer |
| **Feature request** | Next community call | Discussed with community input |
| **ADR proposal** | 5 working days (open for comment) + steering group | Architectural decisions need considered input |

### What "Review" Means

A review is not just a rubber stamp. A quality review checks:

| Dimension | What to Check |
|-----------|--------------|
| **Correctness** | Does the code do what the issue describes? |
| **Tests** | Are there tests? Do they cover the key paths and edge cases? |
| **Domain accuracy** | Does this match how housing actually works? |
| **Security** | Is personal data handled correctly? Input validated? Queries parameterised? |
| **Accessibility** | Keyboard-navigable? Screen-reader-friendly? Sufficient contrast? |
| **Patterns** | Does it follow the project's established patterns (CLAUDE.md)? |
| **Simplicity** | Is there unnecessary complexity? Could this be simpler? |

### Review Escalation

If a PR hasn't been reviewed within the target time:

1. Author comments: "@maintainers — this PR is waiting for review"
2. Any maintainer picks it up within 24 hours of the nudge
3. If still stuck: raise at next maintainer sync
4. If chronic: the steering group addresses maintainer capacity

---

## 10. Pair Programming

Pair programming is the fastest way to transfer both technical and domain knowledge. It's encouraged, not just tolerated.

### When to Pair

| Scenario | Who Pairs |
|----------|-----------|
| **First PR from a new contributor** | Maintainer + new contributor (mandatory) |
| **Complex feature spanning multiple layers** | Two contributors or contributor + maintainer |
| **Domain logic implementation** | Developer + domain expert |
| **Debugging a production issue** | Two maintainers (different perspectives) |
| **Onboarding a new organisation's team** | Existing maintainer + new org's champion |

### How It Works

1. **Schedule:** Agree a 60-90 minute slot. Short enough to stay focused.
2. **Prep:** Both parties read the relevant issue and any linked docs beforehand.
3. **Setup:** Screen share via your preferred tool (VS Code Live Share, Tuple, Google Meet, Teams — whatever works).
4. **Roles:**
   - **Driver** — types, makes micro-decisions
   - **Navigator** — guides strategy, catches mistakes, thinks ahead
   - **Swap every 20-30 minutes**
5. **For skill-building pairs:** The less experienced person drives MORE. Typing builds muscle memory and forces active engagement.
6. **Capture:** After the session, the less experienced person writes the commit message and PR description. Writing crystallises understanding.

### Pairing Across the Skill Gap

| Contributor Level | Maintainer's Role |
|-------------------|-------------------|
| Level 0-1 (Observer/Reporter) | Walk through the codebase, explain architecture, show how issues become code |
| Level 3 (First-Time Coder) | Guide through git workflow, first PR, test writing. Let them drive. |
| Level 4 (Regular) | Discuss design trade-offs, review approach before implementation, mostly navigate |
| Domain Expert (non-coder) | Domain expert navigates ("that's not how it works..."), developer drives |

### Remote Pairing Tips

- Turn cameras on if comfortable — it builds rapport
- Use an editor with cursor sharing so both people can point at code
- Take breaks every 45 minutes — pairing is intense
- End with "what did we learn?" — both parties should answer

---

## 11. Handling Disagreements

Disagreements are healthy. They mean people care. Here's how we resolve them constructively.

### Technical Disagreements

```
1. DISCUSS in the issue or PR — give each perspective a fair hearing
2. EVIDENCE — "I think X because of [data/experience/precedent]"
3. DECIDE — if consensus isn't reached in 3 rounds of discussion:
   a. The maintainer(s) reviewing the PR make the call
   b. For architectural decisions: go through the ADR process
   c. The decision is documented so it doesn't need to be re-argued
4. MOVE ON — once decided, everyone commits to the decision
```

### Domain Disagreements

When domain experts disagree about how housing works:

```
1. Both perspectives are documented in the issue
2. Check: is there a regulatory or statutory answer?
3. If not: which approach covers more organisations' practices?
4. If still stuck: raise at community call for wider sector input
5. Consider: can the system support both approaches via configuration?
```

### Personal Conflicts

Covered by the Code of Conduct. If someone's behaviour makes you uncomfortable:

1. If comfortable: address it directly with the person
2. If not: contact a maintainer or steering group member privately
3. The steering group investigates and acts per the Code of Conduct
4. Confidentiality is maintained throughout

### When to Escalate

| Situation | Escalate To |
|-----------|-------------|
| Technical disagreement on a PR | Maintainers |
| Architectural direction question | ADR process → Steering group |
| Unresponsive maintainer | Other maintainers → Steering group |
| Code of conduct violation | Steering group (private) |
| Licensing or IP concern | Steering group + legal advice |

---

## 12. Intellectual Property & Licensing

### The Basics

- The project uses an open-source licence (specified in `LICENSE` at the repo root)
- **You retain copyright** on your contributions
- By contributing, you grant the project the right to use your contribution under the project's licence
- This is certified via the **Developer Certificate of Origin (DCO)**

### Developer Certificate of Origin

Every commit must include a `Signed-off-by` line:

```
git commit -s -m "feat(allocations): add bidding preference weighting"
```

This produces:
```
feat(allocations): add bidding preference weighting

Signed-off-by: Jo Smith <jo.smith@example-ha.org.uk>
```

The DCO certifies that:
1. You wrote the contribution (or have the right to submit it)
2. You're submitting it under the project's open-source licence
3. You understand your contribution is public and a record is kept

**We don't use a CLA (Contributor Licence Agreement).** CLAs are heavier, sometimes transfer copyright, and can discourage participation. The DCO is sufficient.

### What About Employer IP?

If you're contributing during work time or using work equipment:

- Check with your employer that they're happy for you to contribute
- Most UK housing organisations are supportive of open-source contributions that benefit the sector
- If your employer wants a formal arrangement, the steering group can provide a standard letter of participation

### Third-Party Code

- Don't copy code from proprietary codebases (including your employer's unless explicitly permitted)
- If you include code from another open-source project, check licence compatibility
- Flag any licence concerns in your PR — a maintainer will help assess

---

## 13. Security Disclosure

### If You Find a Security Vulnerability

**Do NOT open a public issue.** Security vulnerabilities must be disclosed privately.

```
1. Email: [security contact email — set up a dedicated address]
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact (especially regarding personal data)
   - Suggested fix (if you have one)
3. A maintainer will acknowledge within 24 hours
4. We'll coordinate a fix and disclosure timeline with you
```

### Our Commitment

- Acknowledge within 24 hours
- Assess severity within 48 hours
- Fix critical vulnerabilities (personal data exposure, auth bypass) within 5 working days
- Credit the reporter in the security advisory (unless they prefer anonymity)
- Publish a security advisory via GitHub once the fix is released

### Severity Levels

| Level | Examples | Response |
|-------|----------|----------|
| **Critical** | Personal data exposure, auth bypass, SQL injection | Fix within 5 working days, emergency release |
| **High** | Cross-tenant data leakage, privilege escalation | Fix within 10 working days |
| **Medium** | Information disclosure (non-personal), CSRF | Next scheduled release |
| **Low** | Minor information leak, non-exploitable weakness | Backlog, fix when convenient |

---

## 14. Leaving & Succession

People move on. Organisations change priorities. This section ensures the project survives transitions.

### For Contributors

No commitment is permanent. If you need to step away:

- Unclaim any issues assigned to you
- If you have open PRs, either finish them or mark as draft with a note: "Stepping away — feel free to take over"
- No explanation needed. Life happens.

### For Maintainers

If you're stepping down as a maintainer:

1. Give at least 4 weeks' notice to the other maintainers
2. Hand off any in-progress work (document state in issues)
3. Help identify a successor if possible
4. Transfer any credentials or access (repo admin, infrastructure, etc.)
5. You remain a welcome contributor at any level

### For Organisations

If your organisation needs to reduce involvement:

1. Let the steering group know (formal or informal)
2. Hand off your champion role if someone else in your org can take it
3. Your past contributions remain — the code is open source
4. You're welcome back anytime

### Bus Factor

The project should always have at least **two active maintainers** from **different organisations**. If this drops below two:

1. The steering group treats it as a priority
2. Actively recruit from regular contributors (Level 4)
3. If no candidates: announce at community call and sector channels
4. If the project cannot sustain two maintainers: discuss archiving or handoff to another group

---

## Quick Reference Card

Print this. Stick it on a wall. Share it with new contributors.

```
HOW TO COLLABORATE
──────────────────────────────────────────────────────────

  FIRST TIME?
  → README.md → CONTRIBUTING.md → scripts/setup.sh
  → Find a good-first-issue → Comment to claim it
  → A maintainer will pair with you on your first PR

  KNOW HOUSING, NOT CODE?
  → File issues from your experience
  → Review features for domain accuracy
  → Help build the glossary
  → Attend community calls

  READY TO CODE?
  → Branch from main → Write tests → Implement → PR
  → Reference the issue → Wait for review (48h max)
  → Read feedback → Iterate → Merge

  GOT A QUESTION?
  → GitHub Discussions (async)
  → Community call (monthly, open to all)
  → Tag @maintainers on an issue

  FOUND A BUG?
  → Open an issue with steps to reproduce

  FOUND A SECURITY ISSUE?
  → DO NOT open a public issue
  → Email [security contact] privately

  RESPONSE TIMES
  → Security: 24 hours
  → New contributor PR: 48 hours
  → Bug report: 5 working days

──────────────────────────────────────────────────────────
```
