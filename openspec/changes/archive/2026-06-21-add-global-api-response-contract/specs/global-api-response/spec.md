## ADDED Requirements

### Requirement: Unified success response envelope
All API success responses SHALL use the outer envelope structure `{"code": "SUCCESS", "message": "OK", "data": <payload>, "trace_id": "<uuid>"}`.

#### Scenario: Successful GET request
- **WHEN** a GET endpoint returns a valid payload
- **THEN** the response body SHALL be `{"code": "SUCCESS", "message": "OK", "data": <payload>, "trace_id": "<uuid>"}`

#### Scenario: Successful POST request
- **WHEN** a POST endpoint creates a resource successfully
- **THEN** the response body SHALL be `{"code": "SUCCESS", "message": "OK", "data": <created_resource>, "trace_id": "<uuid>"}`

#### Scenario: Successful request with empty data
- **WHEN** a DELETE endpoint succeeds with no response body
- **THEN** the response body SHALL be `{"code": "SUCCESS", "message": "OK", "data": null, "trace_id": "<uuid>"}`

### Requirement: Unified error response envelope
All API error responses SHALL use the outer envelope structure `{"code": "<RESPONSE_CODE>", "message": "<human_readable>", "data": null, "trace_id": "<uuid>"}`.

#### Scenario: Validation error
- **WHEN** request body fails validation
- **THEN** the response body SHALL be `{"code": "VALIDATION_ERROR", "message": "<validation detail>", "data": null, "trace_id": "<uuid>"}` with HTTP 422

#### Scenario: Resource not found
- **WHEN** a requested resource does not exist
- **THEN** the response body SHALL be `{"code": "<NOT_FOUND_CODE>", "message": "<detail>", "data": null, "trace_id": "<uuid>"}` with HTTP 404

#### Scenario: Internal error
- **WHEN** an unhandled exception occurs
- **THEN** the response body SHALL be `{"code": "INTERNAL_ERROR", "message": "An unexpected error occurred", "data": null, "trace_id": "<uuid>"}` with HTTP 500

### Requirement: Response code enum
The system SHALL define a `ResponseCode` enum with uppercase string values. The enum SHALL include: `SUCCESS`, `VALIDATION_ERROR`, `INTERNAL_ERROR`, `GITHUB_API_ERROR`, `TASK_NOT_FOUND`, `INSTALLATION_NOT_FOUND`, `REPOSITORY_NOT_FOUND`, `REPOSITORY_NOT_INSTALLED`, `GITHUB_RATE_LIMITED`, `TRANSLATION_ERROR`, `UNSUPPORTED_LANGUAGE`.

#### Scenario: All required codes present
- **WHEN** the `ResponseCode` enum is imported
- **THEN** it SHALL contain exactly 11 members matching the required codes

#### Scenario: Enum values are uppercase strings
- **WHEN** a `ResponseCode` member is serialized
- **THEN** its value SHALL be an uppercase string (e.g., `"GITHUB_API_ERROR"`)

### Requirement: HTTP status codes keep semantic meaning
Error responses SHALL NOT be forced into HTTP 200. HTTP status codes SHALL reflect the error category: 400 for bad request, 401 for unauthorized, 403 for forbidden, 404 for not found, 422 for validation, 429 for rate limit, 500 for internal, 502 for upstream, 504 for timeout.

#### Scenario: GitHub API error
- **WHEN** the GitHub API returns an error
- **THEN** the response SHALL use HTTP 502 with `code: "GITHUB_API_ERROR"`

#### Scenario: Rate limit exceeded
- **WHEN** GitHub rate limit is exceeded
- **THEN** the response SHALL use HTTP 429 with `code: "GITHUB_RATE_LIMITED"`

#### Scenario: Task not found
- **WHEN** a translation task ID does not exist
- **THEN** the response SHALL use HTTP 404 with `code: "TASK_NOT_FOUND"`

### Requirement: No local error maps in controllers
Controllers SHALL NOT maintain local error-to-status mappings (e.g., `_ERROR_STATUS_MAP`). Controllers SHALL NOT parse exception strings as the cross-layer error contract.

#### Scenario: Controller receives AppError
- **WHEN** a controller endpoint catches an `AppError`
- **THEN** it SHALL delegate to the centralized exception handler, NOT manually map error codes to HTTP status

#### Scenario: Controller receives unknown exception
- **WHEN** a controller endpoint catches an unexpected exception
- **THEN** it SHALL let the centralized handler produce the `INTERNAL_ERROR` response, NOT construct a local error dict

### Requirement: Response envelope model
The system SHALL provide a `ResponseEnvelope[T]` generic Pydantic model with fields: `code: ResponseCode`, `message: str`, `data: T | None`, `trace_id: str`.

#### Scenario: Envelope serialization
- **WHEN** a `ResponseEnvelope` is serialized to JSON
- **THEN** it SHALL produce `{"code": "<code>", "message": "<msg>", "data": <payload_or_null>, "trace_id": "<uuid>"}`

#### Scenario: Envelope with data
- **WHEN** `ResponseEnvelope` wraps a success payload
- **THEN** `data` SHALL contain the payload, `code` SHALL be `"SUCCESS"`, `message` SHALL be `"OK"`

#### Scenario: Envelope without data
- **WHEN** `ResponseEnvelope` wraps an error
- **THEN** `data` SHALL be `null`, `code` SHALL be the error code, `message` SHALL be the error detail

### Requirement: Centralized exception handler
The system SHALL register a centralized exception handler on the FastAPI app that converts `AppError` to the unified error envelope response.

#### Scenario: AppError with known code
- **WHEN** an `AppError` with `code="github_api_error"` is raised
- **THEN** the handler SHALL return `{"code": "GITHUB_API_ERROR", "message": "<original_message>", "data": null, "trace_id": "<uuid>"}` with the appropriate HTTP status

#### Scenario: Unhandled exception
- **WHEN** an unhandled `Exception` is raised
- **THEN** the handler SHALL return `{"code": "INTERNAL_ERROR", "message": "An unexpected error occurred", "data": null, "trace_id": "<uuid>"}` with HTTP 500

### Requirement: Response code to HTTP status mapping
The system SHALL define a mapping from `ResponseCode` to HTTP status codes.

#### Scenario: Known code mapping
- **WHEN** `ResponseCode.VALIDATION_ERROR` is used
- **THEN** the HTTP status SHALL be 422

#### Scenario: Unknown code fallback
- **WHEN** a response code has no explicit HTTP status mapping
- **THEN** the HTTP status SHALL default to 500

### Requirement: Security - no sensitive data in error responses
Error responses SHALL NOT contain `token`, `private_key`, `OPENAI_API_KEY`, `traceback`, `stack`, `password`, or `authorization` fields.

#### Scenario: Exception with sensitive context
- **WHEN** an exception message contains API key references
- **THEN** the response SHALL use the generic `INTERNAL_ERROR` message, NOT the raw exception text
