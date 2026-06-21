# Specs: Markdown File Discovery

## Domain Rules

### Requirement: Supported Extensions
The system MUST support `.md` and `.markdown` file extensions.

#### Scenario: Valid markdown file
- **GIVEN** a file path `docs/guide.md`
- **WHEN** checking extension support
- **THEN** the file is identified as supported

#### Scenario: Valid markdown extension
- **GIVEN** a file path `README.markdown`
- **WHEN** checking extension support
- **THEN** the file is identified as supported

#### Scenario: Unsupported extension
- **GIVEN** a file path `src/index.ts`
- **WHEN** checking extension support
- **THEN** the file is NOT identified as supported

### Requirement: Translated Variant Detection
The system MUST detect and exclude files with language suffix patterns.

#### Scenario: Chinese variant
- **GIVEN** a file path `README.zh-CN.md`
- **WHEN** checking if it is a translated variant
- **THEN** the file is identified as a translated variant

#### Scenario: English variant
- **GIVEN** a file path `docs/guide.en.md`
- **WHEN** checking if it is a translated variant
- **THEN** the file is identified as a translated variant

#### Scenario: Not a variant
- **GIVEN** a file path `README.md`
- **WHEN** checking if it is a translated variant
- **THEN** the file is NOT identified as a translated variant

### Requirement: Unsafe Path Rejection
The system MUST reject paths containing directory traversal or absolute paths.

#### Scenario: Directory traversal
- **GIVEN** a file path `../../../etc/passwd.md`
- **WHEN** validating path safety
- **THEN** the path is rejected as unsafe

#### Scenario: Absolute path
- **GIVEN** a file path `/etc/passwd.md`
- **WHEN** validating path safety
- **THEN** the path is rejected as unsafe

#### Scenario: Safe relative path
- **GIVEN** a file path `docs/guide.md`
- **WHEN** validating path safety
- **THEN** the path is accepted as safe

### Requirement: Target Path Preview
The system MUST generate target translation paths using same-directory language suffix.

#### Scenario: Root README
- **GIVEN** source path `README.md` and language `zh-CN`
- **WHEN** generating target path
- **THEN** target is `README.zh-CN.md`

#### Scenario: Nested file
- **GIVEN** source path `docs/guide.md` and language `zh-CN`
- **WHEN** generating target path
- **THEN** target is `docs/guide.zh-CN.md`

### Requirement: Selection Limits
The system MUST enforce file count and total size limits.

#### Scenario: Within limits
- **GIVEN** 5 selected files totaling 100KB
- **WHEN** validating selection
- **THEN** selection is accepted

#### Scenario: Exceeds file count
- **GIVEN** 11 selected files
- **WHEN** validating selection
- **THEN** selection is rejected with file count exceeded error

#### Scenario: Exceeds total size
- **GIVEN** 5 selected files totaling 250KB
- **WHEN** validating selection
- **THEN** selection is rejected with total size exceeded error

## Discovery Service

### Requirement: Directory Exclusions
The discovery service MUST exclude specified directories before evaluating file extensions.

#### Scenario: node_modules exclusion
- **GIVEN** a tree containing `node_modules/pkg/README.md`
- **WHEN** discovering eligible files
- **THEN** the file is excluded

#### Scenario: .git exclusion
- **GIVEN** a tree containing `.git/config.md`
- **WHEN** discovering eligible files
- **THEN** the file is excluded

#### Scenario: Build output exclusion
- **GIVEN** a tree containing `dist/README.md`
- **WHEN** discovering eligible files
- **THEN** the file is excluded

### Requirement: Default README Priority
Root `README.md` MUST be marked as default and sorted first.

#### Scenario: Root README exists
- **GIVEN** a tree with `README.md` and `docs/guide.md`
- **WHEN** sorting results
- **THEN** `README.md` is first and marked as default

#### Scenario: No root README
- **GIVEN** a tree with only `docs/guide.md`
- **WHEN** sorting results
- **THEN** no file is marked as default

### Requirement: Size Limit Marking
Files exceeding size limit MUST be marked with `disabled_reason` instead of silently dropped.

#### Scenario: Oversized file
- **GIVEN** a file of 300KB (limit is 200KB total)
- **WHEN** processing results
- **THEN** the file has `disabled_reason` set to indicate size limit

## API Contract

### Requirement: Authorization Required
The API endpoint MUST require repository authorization.

#### Scenario: Unauthorized repository
- **GIVEN** a request for a repo without installation
- **WHEN** calling the API
- **THEN** response is `repository_not_installed`

#### Scenario: Authorized repository
- **GIVEN** a request for an authorized repo
- **WHEN** calling the API
- **THEN** response contains eligible Markdown files

### Requirement: Language Parameter
The API MUST accept optional `language` query parameter for target path previews.

#### Scenario: Default language
- **GIVEN** a request without language parameter
- **WHEN** calling the API
- **THEN** target paths use `zh-CN` as default

#### Scenario: Custom language
- **GIVEN** a request with `language=ja`
- **WHEN** calling the API
- **THEN** target paths use `ja` language suffix
