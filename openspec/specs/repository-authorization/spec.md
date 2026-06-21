## ADDED Requirements

### Requirement: Resolve authorized repository
The system SHALL return repository metadata when the repository is authorized through the GitHub App installation.

#### Scenario: Repository found in installation
- **WHEN** POST /api/repositories/resolve with `{"input": "owner/repo"}` and repository is in installation's authorized list
- **THEN** system returns `{"full_name": "owner/repo", "default_branch": "main", "private": true}`

### Requirement: Reject unauthorized repository
The system SHALL return `repository_not_installed` error when the repository is not in the GitHub App installation's authorized list.

#### Scenario: Repository not in installation
- **WHEN** POST /api/repositories/resolve with `{"input": "owner/repo"}` and repository is NOT in installation's authorized list
- **THEN** system returns `{"error": "repository_not_installed"}`

### Requirement: Reject invalid repository input
The system SHALL return parse error when the input cannot be parsed as a valid GitHub repository.

#### Scenario: Invalid URL format
- **WHEN** POST /api/repositories/resolve with `{"input": "https://gitlab.com/owner/repo"}`
- **THEN** system returns `{"error": "invalid_repository_url"}`

#### Scenario: Empty input
- **WHEN** POST /api/repositories/resolve with `{"input": ""}`
- **THEN** system returns `{"error": "invalid_repository_url"}`

### Requirement: Require installation_id parameter
The system SHALL require `installation_id` parameter to identify which GitHub App installation to check against.

#### Scenario: Missing installation_id
- **WHEN** POST /api/repositories/resolve with `{"input": "owner/repo"}` and no `installation_id`
- **THEN** system returns `{"error": "missing_installation_id"}`

### Requirement: Validate installation ownership
The system SHALL verify that the installation belongs to the configured GitHub App before checking repository authorization.

#### Scenario: Installation not found
- **WHEN** POST /api/repositories/resolve with `installation_id` that doesn't exist or belongs to another app
- **THEN** system returns `{"error": "installation_not_found"}`

### Requirement: API response format
The system SHALL return JSON responses with consistent structure.

#### Scenario: Successful response structure
- **WHEN** request succeeds
- **THEN** response contains `full_name`, `default_branch`, and `private` fields

#### Scenario: Error response structure
- **WHEN** request fails
- **THEN** response contains `error` field with string error code
