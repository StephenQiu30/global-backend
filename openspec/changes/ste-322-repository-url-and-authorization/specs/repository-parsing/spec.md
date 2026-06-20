## ADDED Requirements

### Requirement: Parse full GitHub HTTPS URL
The system SHALL parse `https://github.com/owner/repo` into `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`.

#### Scenario: Valid HTTPS URL with trailing slash
- **WHEN** input is `https://github.com/owner/repo/`
- **THEN** system returns `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`

#### Scenario: Valid HTTPS URL without trailing slash
- **WHEN** input is `https://github.com/owner/repo`
- **THEN** system returns `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`

### Requirement: Parse GitHub URL without protocol
The system SHALL parse `github.com/owner/repo` into `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`.

#### Scenario: Valid URL without protocol
- **WHEN** input is `github.com/owner/repo`
- **THEN** system returns `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`

### Requirement: Parse owner/repo shorthand
The system SHALL parse `owner/repo` into `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`.

#### Scenario: Valid owner/repo format
- **WHEN** input is `owner/repo`
- **THEN** system returns `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`

### Requirement: Reject empty input
The system SHALL reject empty or whitespace-only input with error.

#### Scenario: Empty string
- **WHEN** input is `""`
- **THEN** system raises validation error

#### Scenario: Whitespace only
- **WHEN** input is `"   "`
- **THEN** system raises validation error

### Requirement: Reject Git SSH URLs
The system SHALL reject SSH URLs like `git@github.com:owner/repo.git`.

#### Scenario: SSH URL
- **WHEN** input is `git@github.com:owner/repo.git`
- **THEN** system raises validation error

### Requirement: Reject non-GitHub URLs
The system SHALL reject URLs from non-GitHub providers.

#### Scenario: GitLab URL
- **WHEN** input is `https://gitlab.com/owner/repo`
- **THEN** system raises validation error

#### Scenario: Bitbucket URL
- **WHEN** input is `https://bitbucket.org/owner/repo`
- **THEN** system raises validation error

### Requirement: Reject GitHub subpath URLs
The system SHALL reject GitHub URLs with subpaths beyond owner/repo.

#### Scenario: Tree subpath
- **WHEN** input is `https://github.com/owner/repo/tree/main/path`
- **THEN** system raises validation error

### Requirement: Reject Gist URLs
The system SHALL reject GitHub Gist URLs.

#### Scenario: Gist URL
- **WHEN** input is `https://gist.github.com/owner/abc123`
- **THEN** system raises validation error

### Requirement: Normalize owner and repo names
The system SHALL normalize owner and repo names by stripping `.git` suffix and converting to lowercase.

#### Scenario: Repo with .git suffix
- **WHEN** input is `https://github.com/Owner/Repo.git`
- **THEN** system returns `RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")`
