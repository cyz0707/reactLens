import httpx
import base64
from typing import Optional


GITHUB_API = "https://api.github.com"

SKIP_DIRS = {
    "node_modules", ".next", "dist", "build", "coverage",
    ".git", "__tests__", ".storybook",
}


def parse_repo_url(url: str) -> tuple[str, str]:
    """Extract owner and repo name from a GitHub URL."""
    url = (
        url.rstrip("/")
        .replace("https://github.com/", "")
        .replace("http://github.com/", "")
    )
    parts = url.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return parts[0], parts[1]


async def fetch_repository_files(
    repo_url: str,
    token: Optional[str] = None,
    max_files: int = 100,
) -> list[dict]:
    """
    Fetch all .tsx and .ts source files from a GitHub repository.
    Returns list of { "path": str, "content": str }.
    """
    owner, repo = parse_repo_url(repo_url)

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get default branch
        repo_resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}",
            headers=headers,
        )
        repo_resp.raise_for_status()
        default_branch = repo_resp.json().get("default_branch", "main")

        # Get full recursive file tree
        tree_resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}",
            params={"recursive": "1"},
            headers=headers,
        )
        tree_resp.raise_for_status()
        tree = tree_resp.json().get("tree", [])

        # Filter to relevant .tsx / .ts files
        target_files = [
            item for item in tree
            if item["type"] == "blob"
            and (item["path"].endswith(".tsx") or item["path"].endswith(".ts"))
            and not any(d in item["path"].split("/") for d in SKIP_DIRS)
            and not item["path"].endswith(".d.ts")
        ][:max_files]

        # Fetch file contents
        files = []
        for item in target_files:
            try:
                resp = await client.get(
                    f"{GITHUB_API}/repos/{owner}/{repo}/contents/{item['path']}",
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                if data.get("encoding") == "base64":
                    content = base64.b64decode(data["content"]).decode(
                        "utf-8", errors="replace"
                    )
                    files.append({"path": item["path"], "content": content})
            except Exception:
                continue  # Skip files that fail to fetch

        return files
