# Proposal: STE-329 Security, Permissions, and Abuse Prevention

## Problem

The global-backend lacks enforcement of security boundaries defined in PRD 09:
- No path traversal rejection for file inputs
- No file type enforcement (Markdown-only)
- No dedicated secret leakage regression tests
- No task size limits before model calls

## Solution

Add backend-enforced security boundaries as domain validators and service-layer checks:

1. **Path/File Safety** - Domain validator rejecting `..`, absolute paths, and non-Markdown files
2. **Authorization Enforcement** - Shared authorization check for all task-related endpoints
3. **Secret Leakage Regression** - Dedicated test suite ensuring API responses never expose credentials
4. **Task Size Limits** - Service-layer enforcement of 10-file/200KB limits before translation

## Scope

- In scope: path safety, authorization enforcement, secret leakage tests, task size limits
- Out of scope: frontend messaging, billing, org RBAC, audit dashboard, frequency limiting

## PRD Reference

`docs/prd/github-translator/09-security-and-permissions.md`
