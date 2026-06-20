# Agent Governance

## Purpose

Define the accepted long-lived governance baseline for the Claude agent standards template, including how OpenSpec-driven SDD execution, project boundaries, Agent Review, and repository validation work together.

## Requirements

### Requirement: OpenSpec Baseline Must Exist
The repository MUST keep an OpenSpec baseline under `openspec/specs/` for long-lived governance and workflow requirements.

#### Scenario: Fresh clone inspects normative assets
- **GIVEN** a contributor clones the repository
- **WHEN** the contributor reviews the normative files
- **THEN** the repository includes `openspec/config.yaml`
- **AND** the repository includes at least one tracked spec under `openspec/specs/`
- **AND** those files describe the accepted governance baseline

### Requirement: SDD Updates Must Precede Normative Changes
Any change that alters long-lived behavior, contracts, review gates, or role responsibilities MUST update OpenSpec specs before the corresponding implementation or normative rewrite is considered complete.

#### Scenario: Governance rule changes
- **GIVEN** a change modifies `CLAUDE.md`, `WORKFLOW.md`, role definitions, or validation expectations
- **WHEN** the change affects durable repository behavior
- **THEN** the change creates or updates proposal/specs/design/tasks under `openspec/changes/` before implementation
- **AND** the accepted result is eventually synchronized back into `openspec/specs/`

### Requirement: Every Task Must Run Inside an OpenSpec Loop
Each task MUST execute inside one OpenSpec loop: create or continue a change, implement against its artifacts with TDD evidence, pass Agent Review, archive the change, and only then move forward.

#### Scenario: Task starts without an OpenSpec change
- **GIVEN** a task is ready for implementation
- **WHEN** there is no active OpenSpec change covering that task
- **THEN** implementation does not start
- **AND** the task must first create or continue the appropriate OpenSpec change

### Requirement: Agent Review Must Validate Against OpenSpec
Agent Review MUST compare the delivered implementation against the linked OpenSpec change artifacts and baseline specs before the task can move to Human Review.

#### Scenario: Review checks for drift
- **GIVEN** a task enters `Agent Review`
- **WHEN** the reviewer validates the task
- **THEN** the reviewer compares implementation, workpad, PR evidence, and validation output against the current OpenSpec proposal/specs/design/tasks
- **AND** any missing requirement, scope drift, or over-implementation is treated as a review failure

### Requirement: OpenSpec Change Must Be Archived Before Human Review
A task MUST NOT move from Agent Review to Human Review until the corresponding OpenSpec change has been verified and archived.

#### Scenario: Review passes but OpenSpec change is still active
- **GIVEN** implementation and validation appear complete
- **WHEN** the OpenSpec change has not yet been archived
- **THEN** the task remains blocked from entering `Human Review`
- **AND** the reviewer requires archive completion before approval

### Requirement: Rework Must Re-enter the Same Engineering Loop
When a task enters Rework, it MUST re-enter the OpenSpec-driven SDD and TDD loop until it passes Agent Review and archive gates.

#### Scenario: Review finds deviation
- **GIVEN** Agent Review finds missing requirements, scope drift, or implementation deviation
- **WHEN** the task is moved to `Rework`
- **THEN** the OpenSpec change is updated before more implementation continues
- **AND** TDD red/green validation is rerun for the corrected scope
- **AND** the task returns to `Agent Review` instead of skipping directly to `Human Review`

### Requirement: Tests Must Stay Inside Accepted Boundary
The repository MUST reject compatibility-only tests and MUST keep automated checks aligned to the current accepted project boundary.

#### Scenario: Compatibility fallback test is proposed
- **GIVEN** a change adds tests for legacy fallback behavior, dual-track compatibility, or unaccepted historical branches
- **WHEN** that behavior is not explicitly required by the repository norms
- **THEN** the change is treated as out of scope
- **AND** the compatibility-only test is not part of the accepted baseline

### Requirement: Validation Must Check OpenSpec Assets
Repository validation MUST fail when the required OpenSpec baseline or OpenSpec skills are missing.

#### Scenario: Required OpenSpec asset removed
- **GIVEN** `openspec/config.yaml`, `openspec/specs/agent-governance/spec.md`, or required `.claude/skills/openspec-*` skill files are missing
- **WHEN** `bash scripts/validate-repository.sh` runs
- **THEN** `scripts/validate-repository.sh` fails
- **AND** the repository is not considered ready for review
