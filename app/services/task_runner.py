"""Task runner that orchestrates translation and GitHub PR submission."""

from typing import Any, Protocol

from app.services.pr_description import build_translation_pr_body


class GitHubClientProtocol(Protocol):
    def create_branch(self, installation_id: int, full_name: str, base_branch: str, branch_name: str) -> str: ...
    def put_file(self, installation_id: int, full_name: str, branch: str, path: str, content: str, message: str) -> None: ...
    def create_pull_request(self, installation_id: int, full_name: str, title: str, body: str, head: str, base: str) -> dict[str, Any]: ...


class TranslationProviderProtocol(Protocol):
    def translate_markdown(self, source: str, language: str) -> str: ...


class TaskRunner:
    """Orchestrates translation task: translate all files, then write to GitHub."""

    def __init__(
        self,
        github_client: GitHubClientProtocol,
        translation_provider: TranslationProviderProtocol,
    ):
        self._github = github_client
        self._provider = translation_provider

    def _target_path(self, source_path: str, language: str) -> str:
        """Convert source path to target language path: README.md -> README.zh-CN.md."""
        if "." in source_path:
            base, ext = source_path.rsplit(".", 1)
            return f"{base}.{language}.{ext}"
        return f"{source_path}.{language}"

    def run(
        self,
        installation_id: int,
        repository_full_name: str,
        base_branch: str,
        files: list[str],
        language: str,
        task_id: str,
        *,
        provider_name: str = "unknown",
    ) -> dict[str, Any]:
        """Run translation task. Returns result dict with 'status' key."""
        branch_name = f"translate/{language}/{task_id}"

        # Phase 1: Translate all files in memory
        translated: list[dict[str, str]] = []
        try:
            for source_path in files:
                target_path = self._target_path(source_path, language)
                content = self._provider.translate_markdown(source_path, language)
                translated.append({
                    "source": source_path,
                    "target": target_path,
                    "content": content,
                })
        except Exception as exc:
            return {"status": "failed", "error": str(exc)}

        # Phase 2: GitHub writes (only if all translations succeeded)
        try:
            self._github.create_branch(
                installation_id, repository_full_name, base_branch, branch_name
            )

            for item in translated:
                self._github.put_file(
                    installation_id,
                    repository_full_name,
                    branch_name,
                    item["target"],
                    item["content"],
                    f"add {language} translation for {item['source']}",
                )

            mappings = [
                {"source": item["source"], "target": item["target"]}
                for item in translated
            ]
            pr_title = f"docs: add {language} translation for Markdown docs"
            pr_body = build_translation_pr_body(
                language=language,
                mappings=mappings,
                provider_name=provider_name,
                task_id=task_id,
            )
            pr = self._github.create_pull_request(
                installation_id,
                repository_full_name,
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch,
            )
        except Exception as exc:
            return {"status": "failed", "error": str(exc)}

        return {
            "status": "succeeded",
            "pr_url": pr["url"],
            "pr_number": pr["number"],
            "branch": branch_name,
        }
