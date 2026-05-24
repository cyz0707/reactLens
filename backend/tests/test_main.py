"""
Integration tests for the ReactLens FastAPI application.
Run: pytest tests/test_main.py -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)


# ── Health checks ─────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "ReactLens" in response.json()["message"]

    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ── Input validation ──────────────────────────────────────────────────

class TestInputValidation:
    def test_invalid_url_returns_400(self):
        response = client.post("/api/analyse", json={"repo_url": "not-a-github-url"})
        assert response.status_code == 400
        assert "GitHub" in response.json()["detail"]

    def test_non_github_url_returns_400(self):
        response = client.post("/api/analyse", json={"repo_url": "https://gitlab.com/user/repo"})
        assert response.status_code == 400

    def test_missing_repo_url_returns_422(self):
        response = client.post("/api/analyse", json={})
        assert response.status_code == 422


# ── Successful analysis ───────────────────────────────────────────────

MOCK_FILES = [
    {
        "path": "src/Button.tsx",
        "content": """
interface ButtonProps {
  label: string;
  onClick: () => void;
}
const Button = ({ label, onClick }: ButtonProps): JSX.Element => {
  return <button onClick={onClick}>{label}</button>;
};
export default Button;
""",
    },
    {
        "path": "src/Dashboard.tsx",
        "content": """
interface DashboardProps {
  data: any;
  loading: boolean;
  error: any;
  onSubmit: (val: any) => void;
  onCancel: () => void;
  theme: string;
  locale: string;
}
const Dashboard = (props: DashboardProps) => {
  // TODO: refactor
  console.log(props);
  return <div />;
};
export default Dashboard;
""",
    },
]


class TestAnalyseEndpoint:
    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_successful_analysis(self, mock_fetch):
        mock_fetch.return_value = MOCK_FILES

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/facebook/react",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["repo_name"] == "react"
        assert data["total_files"] == 2
        assert isinstance(data["components"], list)
        assert len(data["components"]) == 2

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_response_contains_required_fields(self, mock_fetch):
        mock_fetch.return_value = MOCK_FILES

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/facebook/react",
        })

        data = response.json()
        assert "repo_name" in data
        assert "total_files" in data
        assert "high_debt_count" in data
        assert "medium_debt_count" in data
        assert "low_debt_count" in data
        assert "components" in data

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_component_fields_present(self, mock_fetch):
        mock_fetch.return_value = MOCK_FILES

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/facebook/react",
        })

        component = response.json()["components"][0]
        for field in ["filename", "filepath", "loc", "props_count", "any_count",
                      "todo_count", "debt_score", "debt_level", "issues"]:
            assert field in component, f"Missing field: {field}"

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_debt_counts_add_up(self, mock_fetch):
        mock_fetch.return_value = MOCK_FILES

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/facebook/react",
        })

        data = response.json()
        total = data["high_debt_count"] + data["medium_debt_count"] + data["low_debt_count"]
        assert total == data["total_files"]

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_sorted_by_debt_score_descending(self, mock_fetch):
        mock_fetch.return_value = MOCK_FILES

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/facebook/react",
        })

        components = response.json()["components"]
        scores = [c["debt_score"] for c in components]
        assert scores == sorted(scores, reverse=True)

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_no_ai_key_returns_results_without_ai(self, mock_fetch):
        mock_fetch.return_value = MOCK_FILES

        # No anthropic_key in request, no env var set
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            response = client.post("/api/analyse", json={
                "repo_url": "https://github.com/facebook/react",
            })

        assert response.status_code == 200
        data = response.json()
        assert data["ai_summary"] is None or isinstance(data["ai_summary"], str)

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_github_fetch_failure_returns_400(self, mock_fetch):
        mock_fetch.side_effect = Exception("Repository not found")

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/fake/nonexistent-repo-xyz",
        })

        assert response.status_code == 400
        assert "Failed to fetch" in response.json()["detail"]

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_empty_repo_returns_404(self, mock_fetch):
        mock_fetch.return_value = []

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/facebook/react",
        })

        assert response.status_code == 404

    @patch("app.main.fetch_repository_files", new_callable=AsyncMock)
    def test_repo_name_extracted_correctly(self, mock_fetch):
        mock_fetch.return_value = MOCK_FILES

        response = client.post("/api/analyse", json={
            "repo_url": "https://github.com/vercel/next.js",
        })

        assert response.json()["repo_name"] == "next.js"
