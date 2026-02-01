import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import pathspec
from pathspec import PathSpec


class CodeToText:
    DEFAULT_IGNORE = {
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        ".venv",
        "venv",
        ".env",
        "*.egg-info",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "*.so",
        "*.dylib",
        "*.dll",
    }

    DEFAULT_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx",
        ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".go", ".rs", ".rb", ".php",
        ".swift", ".kt", ".scala", ".r",
        ".sql", ".sh", ".bash", ".zsh",
        ".yaml", ".yml", ".json", ".toml",
        ".xml", ".html", ".css", ".scss",
        ".md", ".txt", ".rst",
    }

    def __init__(
            self,
            root_path: str,
            output_file: str | None = "output.txt",
            include_extensions: set[str] | None = None,
            exclude_patterns: list[str] | None = None,
            glob_patterns: list[str] | None = None,
            gitignore: bool = True,
    ):
        """
        Initialize the instance of CodeToText.

        Args:
            root_path: Root directory to scan
            output_file: Output file path (None for clipboard-only mode)
            include_extensions: Set of file extensions to include (with dots)
            exclude_patterns: List of patterns to exclude (gitignore style)
            glob_patterns: List of glob patterns to include (e.g., '*.py', 'src/**/*.js')
            gitignore: Whether to respect .gitignore files
        """
        self.root_path = Path(root_path).resolve()
        self.output_file = output_file
        self.include_extensions = include_extensions or self.DEFAULT_EXTENSIONS
        self.exclude_patterns = exclude_patterns or []
        self.glob_patterns = glob_patterns or []
        self.gitignore = gitignore
        self.spec: PathSpec | None = None
        self.file_count = 0

        if self.gitignore:
            self._load_gitignore()

    def _load_gitignore(self) -> None:
        """Load .gitignore patterns if present."""
        gitignore_path = self.root_path / ".gitignore"
        patterns = list(self.DEFAULT_IGNORE)

        if gitignore_path.exists():
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)

        patterns.extend(self.exclude_patterns)
        self.spec = pathspec.PathSpec.from_lines("gitignore", patterns)

    def _matches_glob_pattern(self, file_path: Path) -> bool:
        """Check if file matches any glob pattern."""
        if not self.glob_patterns:
            return False

        relative_path = file_path.relative_to(self.root_path)
        relative_str = str(relative_path)

        for pattern in self.glob_patterns:
            if fnmatch(relative_str, pattern):
                return True
            if fnmatch(file_path.name, pattern):
                return True

        return False

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included."""
        if self.glob_patterns:
            if not self._matches_glob_pattern(file_path):
                return False
        else:
            if file_path.suffix not in self.include_extensions:
                return False

        if self.spec:
            relative_path = file_path.relative_to(self.root_path)
            if self.spec.match_file(str(relative_path)):
                return False

        return True

    def _get_files(self) -> list[Path]:
        """Get all files to process."""
        files = []
        for root, dirs, filenames in os.walk(self.root_path):
            root_path = Path(root)

            if self.spec:
                relative_root = root_path.relative_to(self.root_path)
                dirs[:] = [
                    d for d in dirs
                    if not self.spec.match_file(str(relative_root / d))
                ]

            for filename in filenames:
                file_path = root_path / filename
                if self._should_include_file(file_path):
                    files.append(file_path)

        return sorted(files)

    def generate_content(self, add_tree: bool = True, separator: str = "=" * 80) -> str:
        """
        Generate content as string (for clipboard).

        Args:
            add_tree: Whether to add directory tree at the beginning
            separator: Separator between files

        Returns:
            Generated content as string
        """
        files = self._get_files()
        self.file_count = len(files)

        lines = []
        lines.append(f"Code Export from: {self.root_path}")
        lines.append(f"Total files: {len(files)}")
        lines.append(separator)
        lines.append("")

        if add_tree:
            lines.append("DIRECTORY TREE:")
            lines.append(separator)
            lines.append(self._generate_tree())
            lines.append("")
            lines.append(separator)
            lines.append("")

        for i, file_path in enumerate(files, 1):
            relative_path = file_path.relative_to(self.root_path)

            lines.append(f"FILE {i}/{len(files)}: {relative_path}")
            lines.append(separator)

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                lines.append(content)
            except UnicodeDecodeError:
                lines.append("[Binary file - skipped]")
            except Exception as e:
                lines.append(f"[Error reading file: {e}]")

            lines.append("")
            lines.append(separator)
            lines.append("")

        return "\n".join(lines)

    def convert(self, add_tree: bool = True, separator: str = "=" * 80) -> int:
        """
        Convert files to single text file.

        Args:
            add_tree: Whether to add directory tree at the beginning
            separator: Separator between files

        Returns:
            Number of files processed
        """
        if not self.output_file:
            raise ValueError("output_file must be specified for convert()")

        content = self.generate_content(add_tree=add_tree, separator=separator)

        with open(self.output_file, "w", encoding="utf-8") as out:
            out.write(content)

        return self.file_count

    def _generate_tree(self) -> str:
        """Generate a directory tree representation."""
        tree_lines = []
        files = self._get_files()

        if not files:
            return "(no files to display)"

        dir_structure: dict[str, Any] = {}
        for file_path in files:
            relative_path = file_path.relative_to(self.root_path)
            parts = relative_path.parts

            current = dir_structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            if "__files__" not in current:
                current["__files__"] = []
            current["__files__"].append(parts[-1])

        def print_tree(structure: dict[str, Any], prefix: str = "", is_last: bool = True) -> None:
            items = []
            for key in sorted(structure.keys()):
                if key != "__files__":
                    items.append((key, True))  # directory

            if "__files__" in structure:
                for file in sorted(structure["__files__"]):
                    items.append((file, False))  # file

            for i, (name, is_dir) in enumerate(items):
                is_last_item = i == len(items) - 1
                connector = "└── " if is_last_item else "├── "
                tree_lines.append(f"{prefix}{connector}{name}{'/' if is_dir else ''}")

                if is_dir:
                    extension = "    " if is_last_item else "│   "
                    print_tree(structure[name], prefix + extension, is_last_item)

        tree_lines.append(f"{self.root_path.name}/")
        print_tree(dir_structure)

        return "\n".join(tree_lines)
