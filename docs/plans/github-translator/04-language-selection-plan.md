# PRD 04 Language Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide target language selection and enforce language codes in backend and frontend.

**Architecture:** Backend is the source of truth for allowed language codes. Frontend mirrors the same list for user experience and displays target file previews using selected language.

**Tech Stack:** Python pure domain module, TypeScript constants, React selector.

## Global Constraints

- Supported first-version languages: `zh-CN`, `zh-TW`, `en`, `ja`, `ko`, `fr`, `de`, `es`.
- Default language is `zh-CN`.
- Language suffix is used in generated file path.
- The language selector must support search because PRD 04 requires searchable language selection.
- PRD source: `docs/prd/github-translator/04-language-selection.md`.

---

## Task 1: Backend Language Domain

**Repo:** `global-backend`

**Files:**
- Create: `app/domain/languages.py`
- Test: `tests/domain/test_languages.py`

**Steps:**
- [ ] Write failing tests for accepted `zh-CN`, rejected unknown code, and trimmed input.
- [ ] Implement `SUPPORTED_LANGUAGES`.
- [ ] Implement `validate_language_code(code: str) -> str`.
- [ ] Run: `pytest tests/domain/test_languages.py -v`; expect pass.
- [ ] Commit: `feat: 添加目标语言校验`

**Acceptance:**
- Unsupported language codes cannot reach translation task execution.

## Task 2: Backend Language API

**Repo:** `global-backend`

**Files:**
- Create: `app/api/languages.py`
- Modify: `app/main.py`
- Test: `tests/api/test_languages_api.py`

**Steps:**
- [ ] Write failing test for `GET /api/languages`.
- [ ] Return language `code` and display `label`.
- [ ] Register router in FastAPI app.
- [ ] Run: `pytest tests/api/test_languages_api.py -v`; expect pass.
- [ ] Commit: `feat: 添加语言列表接口`

**Acceptance:**
- Frontend can fetch supported language list from backend.

## Task 3: Frontend Language Constants

**Repo:** `global-frontend`

**Files:**
- Create: `src/lib/languages.ts`
- Test: `src/lib/languages.test.ts`

**Steps:**
- [ ] Write failing test that `zh-CN` is default and all required codes exist.
- [ ] Implement `SUPPORTED_LANGUAGES` and `DEFAULT_LANGUAGE`.
- [ ] Run: `npm test -- src/lib/languages.test.ts`; expect pass.
- [ ] Commit: `feat: 添加前端语言列表`

**Acceptance:**
- UI can render the first-version language list without hard-coded duplicates in components.

## Task 4: Frontend Language Selector

**Repo:** `global-frontend`

**Files:**
- Create: `src/components/LanguageSelector.tsx`
- Test: `src/components/LanguageSelector.test.tsx`

**Steps:**
- [ ] Write failing test for changing target language from `zh-CN` to `ja`.
- [ ] Write failing test for filtering the language list by typing `Japanese` or `日`.
- [ ] Implement label `目标语言`.
- [ ] Display language name and code.
- [ ] Implement a searchable combobox or input+listbox with keyboard-accessible options.
- [ ] Emit selected code through `onChange`.
- [ ] Run: `npm test -- src/components/LanguageSelector.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加目标语言选择器`

**Acceptance:**
- User can choose a supported target language and downstream file previews update.
- User can search by language label or code before selecting.

## Verification

```bash
pytest tests/domain/test_languages.py tests/api/test_languages_api.py -v
npm test -- src/lib/languages.test.ts src/components/LanguageSelector.test.tsx
```
