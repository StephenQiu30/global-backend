# Specs: GitHub App Installation Verification & Authorized Repositories

## Requirement: Configuration Must Be Environment-Driven

The application MUST load GitHub App credentials from environment variables using pydantic-settings.

### Scenario: Valid configuration loads
- **GIVEN** environment variables `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_APP_WEBHOOK_SECRET` are set
- **WHEN** the application starts
- **THEN** configuration is loaded without error
- **AND** `github_app_id` is an integer
- **AND** `github_app_private_key` is a non-empty string

### Scenario: Missing required configuration fails
- **GIVEN** `GITHUB_APP_ID` is not set
- **WHEN** the application starts
- **THEN** a validation error is raised

## Requirement: Installation Verification Must Call GitHub API

The `POST /api/github/installations/verify` endpoint MUST verify the installation exists and belongs to the configured GitHub App.

### Scenario: Valid installation returns account info
- **GIVEN** a valid `installation_id` is provided
- **WHEN** the verify endpoint is called
- **THEN** the response contains `installation_id`, `account_login`, `account_type`, `repository_selection`
- **AND** the response does NOT contain any tokens or secrets

### Scenario: Invalid installation returns 404
- **GIVEN** an `installation_id` that does not exist
- **WHEN** the verify endpoint is called
- **THEN** the response is 404 with a safe error message
- **AND** no internal error details are leaked

### Scenario: GitHub API failure returns 502
- **GIVEN** the GitHub API is unreachable or returns an error
- **WHEN** the verify endpoint is called
- **THEN** the response is 502 with a safe error message

## Requirement: Repository Listing Must Return Authorized Repos

The `GET /api/github/installations/{installation_id}/repositories` endpoint MUST return the list of repositories accessible to the installation.

### Scenario: Installation with repos returns list
- **GIVEN** an installation authorized for multiple repositories
- **WHEN** the repositories endpoint is called
- **THEN** the response contains a list of repositories
- **AND** each repository has `full_name`, `default_branch`, `private` fields
- **AND** no tokens or secrets appear in the response

### Scenario: Installation with no repos returns empty list
- **GIVEN** an installation with no authorized repositories
- **WHEN** the repositories endpoint is called
- **THEN** the response contains an empty list

### Scenario: Invalid installation_id returns 404
- **GIVEN** an `installation_id` that does not exist
- **WHEN** the repositories endpoint is called
- **THEN** the response is 404

## Requirement: Tokens Must Never Appear in Responses

All API responses MUST NOT include GitHub App secrets, installation tokens, or webhook secrets.

### Scenario: Response field audit
- **GIVEN** any successful or error response from installation endpoints
- **WHEN** the response body is inspected
- **THEN** it does NOT contain fields named `token`, `secret`, `private_key`, `access_token`
- **AND** it does NOT contain JWT-format strings
