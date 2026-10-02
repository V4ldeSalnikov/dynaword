"""Run the maintainer workflows against a small, disposable corpus."""

import os
from pathlib import Path
import shutil
import subprocess
import sys


def test_dummy_repository_workflow(tmp_path: Path):
    repo = tmp_path / "dummy_dynaword"
    shutil.copytree(Path(__file__).parent / "fixtures" / "dummy_dynaword", repo)
    env = {
        **os.environ,
        "DYNAWORD_REPO": str(repo),
        "HF_HOME": str(tmp_path / "huggingface"),
        "HF_HUB_OFFLINE": "1",
        "HF_DATASETS_OFFLINE": "1",
        "MPLBACKEND": "Agg",
        "PYTHONUTF8": "1",
    }
    commands = [
        [sys.executable, "create.py"],
        ["git", "init", "--quiet"],
        ["git", "add", "."],
        [
            "git",
            "-c",
            "user.name=Dynaword smoke test",
            "-c",
            "user.email=smoke@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Create dummy corpus",
        ],
        [sys.executable, "-m", "dynaword.update_descriptive_statistics"],
        [sys.executable, "-m", "dynaword.bump_version"],
        [
            sys.executable,
            "-m",
            "pytest",
            "--pyargs",
            "dynaword.tests",
            "--rootdir=.",
            "-q",
        ],
    ]
    for command in commands:
        result = subprocess.run(
            command,
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        assert result.returncode == 0, (
            f"Command failed: {' '.join(command)}\n{result.stdout}\n{result.stderr}"
        )
