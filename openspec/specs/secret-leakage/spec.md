# Spec: Secret Leakage Regression

## Requirements

1. API responses must not contain `token`, `private_key`, `OPENAI_API_KEY`
2. Error responses must not contain raw Python stack traces
3. GitHub API errors must be logged but not exposed to clients

## Test Cases

- All endpoints: response body does not contain sensitive keywords
- Error responses: no `Traceback` or `.py` file references
- 502 responses: generic error message, no internal details
