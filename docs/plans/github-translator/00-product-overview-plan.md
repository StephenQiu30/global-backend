# PRD 00 Product Overview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the first-version product foundation for GitHub Markdown Translator across `global-frontend` and `global-backend`.

**Architecture:** Build a two-repo product: Next.js frontend for the user workflow and FastAPI backend for GitHub App, Markdown translation, and PR submission. This plan coordinates the foundation and delegates feature-specific work to PRD 01-10 plans.

**Tech Stack:** Next.js, React, TypeScript, Tailwind CSS, Python 3.12, FastAPI, OpenAI API, GitHub App REST API, pytest, Vitest, Playwright.

## Global Constraints

- First version supports only repositories authorized through the GitHub App.
- Users input or select a GitHub repository, choose Markdown files, choose a target language, and create a translation PR.
- Source files are never overwritten.
- Output files use same-directory language suffixes.
- All GitHub writes happen through a branch and Pull Request.
- PRD source: `docs/prd/github-translator/00-product-overview.md`.

---

## Task 1: Create Product Foundation Tracking

**Repos:** `global-backend`, `global-frontend`

**Files:**
- Modify: `README.md`
- Modify: `docs/plans/README.md`
- Create: `docs/plans/github-translator/README.md`

**Steps:**
- [ ] Add a `GitHub Markdown Translator` section to each repo README that links to PRD and plan indexes.
- [ ] Create `docs/plans/github-translator/README.md` with links to plan files `00` through `10`.
- [ ] Run: `scripts/validate-repository.sh && git diff --check`
- [ ] Commit backend with `docs: 添加 GitHub 翻译产品计划索引`
- [ ] Commit frontend with `docs: 添加 GitHub 翻译产品计划索引`

**Acceptance:**
- Both repos expose PRD and plan entry points from README.
- The plan index lists every PRD-specific implementation plan.

## Task 2: Establish Cross-Repo Execution Order

**Repos:** `global-backend`, `global-frontend`

**Files:**
- Modify: `docs/plans/github-translator/README.md`

**Steps:**
- [ ] Document implementation order: PRD 01, 02, 03, 04, 06, 05, 07, 08, 09, then PRD 10 later.
- [ ] Mark PRD 10 as second-phase work outside first-version delivery.
- [ ] Add validation gate: backend tests must pass before frontend E2E is considered complete.
- [ ] Run: `rg -n "PRD 10|second-phase|GitHub App" docs/plans/github-translator/README.md`
- [ ] Commit with `docs: 明确 GitHub 翻译计划执行顺序`

**Acceptance:**
- A new worker can open the plan index and know which plan to execute first.

## Task 3: Confirm Product Scope Before Implementation

**Repos:** `global-backend`, `global-frontend`

**Files:**
- Modify: `docs/plans/github-translator/README.md`

**Steps:**
- [ ] Add first-version scope checklist: installed GitHub App only, Web flow only, PR submission only.
- [ ] Add non-goals checklist: issue comment command, fork PR, public repo write, billing, auto-merge.
- [ ] Run: `rg -n "Non-goals|installed GitHub App|auto-merge" docs/plans/github-translator/README.md`
- [ ] Commit with `docs: 补充首版范围检查清单`

**Acceptance:**
- First-version scope is explicit and matches PRD 00.

## Verification

Run in both repos:

```bash
scripts/validate-repository.sh
git diff --check
```
