import os
import yaml


def test_dockerfile_and_compose_existence():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    dockerfile_path = os.path.join(root_dir, "Dockerfile")
    compose_path = os.path.join(root_dir, "docker-compose.yml")

    assert os.path.exists(dockerfile_path), "Dockerfile missing in repository root"
    assert os.path.exists(compose_path), "docker-compose.yml missing in repository root"

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        df_content = f.read()

    assert "FROM python:3.12" in df_content
    assert "HEALTHCHECK" in df_content
    assert "uvicorn" in df_content

    with open(compose_path, "r", encoding="utf-8") as f:
        compose_content = f.read()

    assert "rip-backend" in compose_content
    assert "8000:8000" in compose_content


def test_github_actions_ci_workflow():
    ci_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            ".github",
            "workflows",
            "ci.yml",
        )
    )
    assert os.path.exists(ci_path), "CI workflow file .github/workflows/ci.yml is missing"

    with open(ci_path, "r", encoding="utf-8") as f:
        ci_yaml = yaml.safe_load(f)

    assert ci_yaml.get("name") == "Continuous Integration"
    assert "jobs" in ci_yaml
    assert "backend-test" in ci_yaml["jobs"]
    assert "extension-build" in ci_yaml["jobs"]
    assert "docker-build" in ci_yaml["jobs"]
