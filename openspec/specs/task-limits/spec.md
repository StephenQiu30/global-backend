# Spec: Task Limits

## Requirements

1. Tasks with more than 10 files must be rejected
2. Tasks with total source size exceeding 200KB must be rejected
3. File sizes must be calculated from fetched GitHub contents, not request payloads
4. Limit violations return non-retryable error

## Test Cases

- 11 files -> rejected with `task_too_many_files`
- 10 files -> accepted
- Total size 201KB -> rejected with `task_too_large`
- Total size 200KB -> accepted
- Size from request payload ignored -> uses GitHub data
