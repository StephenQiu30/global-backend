# GitHub Markdown Translator Plan Index

This directory maps each PRD file to its own implementation plan. Execute plans in order unless a later plan is explicitly marked as second-phase work.

## First-Version Plans

1. [PRD 00 Product Overview Plan](00-product-overview-plan.md)
2. [PRD 01 GitHub App Installation Plan](01-github-app-installation-plan.md)
3. [PRD 02 Repository URL And Authorization Plan](02-repository-url-and-authorization-plan.md)
4. [PRD 03 Markdown File Discovery Plan](03-markdown-file-discovery-plan.md)
5. [PRD 04 Language Selection Plan](04-language-selection-plan.md)
6. [PRD 05 Translation Task Plan](05-translation-task-plan.md)
7. [PRD 06 Markdown Fidelity Plan](06-markdown-fidelity-plan.md)
8. [PRD 07 Pull Request Submission Plan](07-pr-submission-plan.md)
9. [PRD 08 Task Status And Results Plan](08-task-status-and-results-plan.md)
10. [PRD 09 Security And Permissions Plan](09-security-and-permissions-plan.md)

## Second-Phase Plan

11. [PRD 10 Public Repository Preview Future Plan](10-public-repository-preview-future-plan.md)

## Execution Notes

1. Start with PRD 00 to establish cross-repo planning and documentation links.
2. Implement PRD 01-04 before translation task execution, because task creation depends on installation, repository authorization, file discovery, and language selection.
3. Implement PRD 06 before production model calls, because Markdown fidelity is a core quality gate.
4. Implement PRD 05 and PRD 07 together when wiring the full backend task flow.
5. Implement PRD 08 for user-visible result handling.
6. Keep PRD 09 active throughout implementation; security tests should be added before expanding write capability.
7. Do not implement PRD 10 until first-version GitHub App flow is complete.

## Validation Gate

Before starting implementation from these plans, run in each repo:

```bash
scripts/validate-repository.sh
git status --short --branch
```
