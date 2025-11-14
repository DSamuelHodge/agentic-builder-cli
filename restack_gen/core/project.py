# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from pathlib import Path


class ProjectStructure:
    """Handles project directory structure and paths."""

    def __init__(self, project_root: Path | None = None):
        # Use provided project_root or default to current working directory
        if project_root is None:
            start_path = Path.cwd().resolve()
        else:
            start_path = project_root.resolve()

        # Search for marker file (restack.toml) in current and parent directories
        marker = "restack.toml"
        root = start_path
        for parent in [start_path] + list(start_path.parents):
            if (parent / marker).exists():
                root = parent
                break
        self.root = root
        self.src_dir = self.root / "src"
        self.tests_dir = self.root / "tests"
        self.scripts_dir = self.root / "scripts"

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
