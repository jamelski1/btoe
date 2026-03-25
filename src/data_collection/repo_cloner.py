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
            subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=repo_path,
                capture_output=True,
                check=False,
            )
        else:
            url = f"https://github.com/{owner}/{name}.git"
            logger.info(f"Cloning {url} to {repo_path}")
            subprocess.run(
                ["git", "clone", "--depth=1", url, str(repo_path)],
                capture_output=True,
                check=True,
            )

        return repo_path

    def get_repo_path(self, owner: str, name: str) -> Path | None:
        """Get path to an existing local clone."""
        repo_path = self.clone_dir / f"{owner}_{name}"
        return repo_path if repo_path.exists() else None
