# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from pathlib import Path
from typing import Optional


class ProjectStructure:
    """Handles project directory structure and paths."""

    def __init__(self, root: Optional[Path] = None):
        self.root = self._find_project_root(root or Path.cwd())

    def _find_project_root(self, start_path: Path) -> Path:
        """Find project root by looking for marker files."""
        current = start_path.resolve()
        markers = ["restack.toml", "pyproject.toml", "package.json"]
        for _ in range(10):  # Limit depth
            for marker in markers:
                if (current / marker).exists():
                    return current
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        return start_path.resolve()

    @property
    def src_dir(self) -> Path:
        return self.root / "src"

    @property
    def tests_dir(self) -> Path:
        return self.root / "tests"

    @property
    def scripts_dir(self) -> Path:
        return self.root / "scripts"

    def get_subdir(self, subdir: str) -> Path:
        """Get subdirectory path under src/."""
        return self.src_dir / subdir

    def ensure_structure(self):
        """Create standard project structure."""
        dirs = [
            self.src_dir / "agents",
            self.src_dir / "functions",
            self.src_dir / "workflows",
            self.tests_dir,
            self.scripts_dir,
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
