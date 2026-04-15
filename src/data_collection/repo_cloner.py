"""Clone and manage local copies of target repositories for PyDriller analysis."""

import logging
import subprocess
from pathlib import Path

from src.utils.config import get_data_dir

logger = logging.getLogger(__name__)


class RepoCloner:
    """Manages local clones of target repositories."""

    def __init__(self):
        self.clone_dir = get_data_dir() / "repos"
        self.clone_dir.mkdir(parents=True, exist_ok=True)

    def clone_or_update(self, owner: str, name: str) -> Path:
        """Clone a repository or pull latest changes if already cloned.

        Returns the local path to the repository.
        """
        repo_path = self.clone_dir / f"{owner}_{name}"

        if repo_path.exists():
            logger.info(f"Updating existing clone at {repo_path}")
            # If the existing clone is shallow, unshallow it so we have full history
            shallow_marker = repo_path / ".git" / "shallow"
            if shallow_marker.exists():
                logger.info(f"  Existing clone is shallow, fetching full history...")
                result = subprocess.run(
                    ["git", "fetch", "--unshallow"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    logger.warning(f"  Unshallow failed: {result.stderr.strip()}")
            subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=repo_path,
                capture_output=True,
                check=False,
            )
        else:
            url = f"https://github.com/{owner}/{name}.git"
            logger.info(f"Cloning {url} to {repo_path} (full history)")
            result = subprocess.run(
                ["git", "clone", url, str(repo_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                logger.error(f"  Clone failed (exit {result.returncode}): {result.stderr.strip()}")
                raise subprocess.CalledProcessError(
                    result.returncode, result.args, result.stdout, result.stderr
                )

        return repo_path

    def get_repo_path(self, owner: str, name: str) -> Path | None:
        """Get path to an existing local clone."""
        repo_path = self.clone_dir / f"{owner}_{name}"
        return repo_path if repo_path.exists() else None
