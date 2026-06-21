# Public Repository Preview

## Purpose

Provide read-only translation previews for public GitHub repositories without GitHub App write access.

## Requirements

### Requirement: Public preview endpoint

The system SHALL expose `POST /api/public-preview` accepting `repository`, `files`, and `language`.

#### Scenario: Successful preview

- **WHEN** the repository is public and files are valid Markdown paths
- **THEN** the API returns translated preview content and target filenames
- **AND** the response MUST NOT include a PR URL

### Requirement: No GitHub write operations

Public preview flows MUST NOT call GitHub write APIs (branch, file write, pull request).

#### Scenario: Service-level safety

- **WHEN** a public preview is generated
- **THEN** no GitHub write methods are invoked

### Requirement: Shared validation limits

Public preview MUST reuse repository parsing, path safety, and translation validation rules from the first-version flow.

#### Scenario: Invalid repository

- **WHEN** the repository cannot be found or accessed
- **THEN** the API returns a structured 404 error

#### Scenario: Validation failure

- **WHEN** file paths are unsafe or unsupported
- **THEN** the API returns a structured 400 error
