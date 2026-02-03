import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import pathspec
from pathspec import PathSpec

from .utils import load_patterns_from_file


class CodeToText:
    """Convert code files to a single text file for LLM consumption."""

    def __init__(
            self,
            root_path: str,
            output_file: str | None = "output.txt",
            include_extensions: set[str] | None = None,
            exclude_patterns: list[str] | None = None,
            glob_patterns: list[str] | None = None,
            gitignore: bool = True,
            max_file_size_kb: int | None = None,
    ):
        """
        Initialize CodeToText instance.

        Args:
            root_path: Root directory to scan
            output_file: Output file path (None for clipboard-only mode)
            include_extensions: Set of file extensions to include (with dots)
            exclude_patterns: List of patterns to exclude (gitignore style)
            glob_patterns: List of glob patterns to include (e.g., '*.py', 'src/**/*.js')
            gitignore: Whether to respect .gitignore files
            max_file_size_kb: Skip files larger than this size in KB
        """
        self.root_path = Path(root_path).resolve()
        self.output_file = output_file
        self.glob_patterns = glob_patterns or []
        self.gitignore = gitignore
        self.max_file_size_kb = max_file_size_kb
        self.spec: PathSpec | None = None
        self.file_count = 0
        self.skipped_files: list[tuple[Path, str]] = []

        config_dir = Path(__file__).parent
        default_extensions = load_patterns_from_file(config_dir / ".extensions")
        default_ignore = load_patterns_from_file(config_dir / ".ignore")

        self.include_extensions = include_extensions or default_extensions
        self.exclude_patterns = exclude_patterns or []
        self.default_ignore = default_ignore

        if self.gitignore:
            self._init_pathspec()

    def _init_pathspec(self) -> None:
        """Initialize pathspec from .gitignore files and default patterns."""
        patterns = list(self.default_ignore)
        current_path = self.root_path

        for _ in range(5):
            gitignore_path = current_path / ".gitignore"
            if gitignore_path.exists():
                try:
                    with open(gitignore_path, encoding="utf-8") as f:
                        for line in f:
                            clean_line = line.strip()
                            if clean_line and not clean_line.startswith("#"):
                                patterns.append(clean_line)
                except Exception:
                    pass

            parent = current_path.parent
            if parent == current_path:
                break
            current_path = parent

        patterns.extend(self.exclude_patterns)
        self.spec = pathspec.PathSpec.from_lines("gitignore", patterns)

    def _check_glob_match(self, file_path: Path) -> bool:
        """Check if file matches any glob pattern."""
        if not self.glob_patterns:
            return False

        relative_path = file_path.relative_to(self.root_path)
        path_str = str(relative_path)

        for pattern in self.glob_patterns:
            if fnmatch(path_str, pattern):
                return True
            if fnmatch(file_path.name, pattern):
                return True
            if fnmatch(path_str.replace(os.sep, "/"), pattern):
                return True

        return False

    def _check_file_inclusion(self, file_path: Path) -> bool:
        """Determine if a file should be included in the output."""
        if self.max_file_size_kb is not None:
            try:
                file_size_kb = file_path.stat().st_size / 1024
                if file_size_kb > self.max_file_size_kb:
                    self.skipped_files.append(
                        (file_path, f"exceeds size limit ({file_size_kb:.1f}KB)")
                    )
                    return False
            except Exception:
                pass

        if self.glob_patterns:
            if not self._check_glob_match(file_path):
                return False

        if self.spec:
            try:
                relative_path = file_path.relative_to(self.root_path)
                relative_str = str(relative_path).replace(os.sep, "/")

                if self.spec.match_file(relative_str):
                    self.skipped_files.append((file_path, "matches ignore pattern"))
                    return False
            except ValueError:
                return False

        if file_path.suffix not in self.include_extensions:
            return False

        return True

    def _collect_files(self) -> list[Path]:
        """Collect all files to process based on filters."""
        files = []
        self.skipped_files = []

        for root, dirs, filenames in os.walk(self.root_path):
            root_path = Path(root)

            if self.spec:
                try:
                    relative_root = root_path.relative_to(self.root_path)
                    root_str = str(relative_root).replace(os.sep, "/") if str(relative_root) != "." else ""

                    filtered_dirs = []
                    for d in dirs:
                        dir_path = f"{root_str}/{d}" if root_str else d

                        if not self.spec.match_file(dir_path) and not self.spec.match_file(f"{dir_path}/"):
                            filtered_dirs.append(d)

                    dirs[:] = filtered_dirs
                except ValueError:
                    pass

            for filename in filenames:
                file_path = root_path / filename
                if self._check_file_inclusion(file_path):
                    files.append(file_path)

        return sorted(files)

    def calculate_statistics(self) -> dict[str, Any]:
        """
        Calculate statistics about the codebase.

        Returns:
            Dictionary containing total files, size, lines, breakdown by extension, etc.
        """
        files = self._collect_files()

        stats: dict = {
            "total_files": len(files),
            "total_size_bytes": 0,
            "total_lines": 0,
            "by_extension": {},
            "skipped_files": len(self.skipped_files),
            "largest_files": [],
        }

        file_sizes = []

        for file_path in files:
            try:
                size = file_path.stat().st_size
                stats["total_size_bytes"] += size
                file_sizes.append((file_path, size))

                try:
                    with open(file_path, encoding="utf-8") as f:
                        lines = sum(1 for _ in f)
                        stats["total_lines"] += lines
                except Exception:
                    pass

                ext = file_path.suffix or "(no extension)"
                if ext not in stats["by_extension"]:
                    stats["by_extension"][ext] = {"count": 0, "size": 0}
                stats["by_extension"][ext]["count"] += 1
                stats["by_extension"][ext]["size"] += size

            except Exception:
                pass

        file_sizes.sort(key=lambda x: x[1], reverse=True)
        stats["largest_files"] = [
            {"path": str(f.relative_to(self.root_path)), "size_kb": s / 1024}
            for f, s in file_sizes[:10]
        ]

        return stats

    def generate_content(self, add_tree: bool = True, separator: str = "=" * 80) -> str:
        """
        Generate content as string without writing to file.

        Args:
            add_tree: Whether to add directory tree at the beginning
            separator: Separator between files

        Returns:
            Generated content as string
        """
        files = self._collect_files()
        self.file_count = len(files)

        output_lines = []
        output_lines.append(f"Code Export from: {self.root_path}")
        output_lines.append(f"Total files: {len(files)}")
        output_lines.append(separator)
        output_lines.append("")

        if add_tree:
            output_lines.append("DIRECTORY TREE:")
            output_lines.append(separator)
            output_lines.append(self._build_tree_structure())
            output_lines.append("")
            output_lines.append(separator)
            output_lines.append("")

        for idx, file_path in enumerate(files, 1):
            relative_path = file_path.relative_to(self.root_path)

            output_lines.append(f"FILE {idx}/{len(files)}: {relative_path}")
            output_lines.append(separator)

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                output_lines.append(content)
            except UnicodeDecodeError:
                output_lines.append("[Binary file - skipped]")
            except Exception as e:
                output_lines.append(f"[Error reading file: {e}]")

            output_lines.append("")
            output_lines.append(separator)
            output_lines.append("")

        return "\n".join(output_lines)

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

    def _build_tree_structure(self) -> str:
        """Build a directory tree representation of included files."""
        tree_output = []
        files = self._collect_files()

        if not files:
            return "(no files to display)"

        structure: dict[str, Any] = {}
        for file_path in files:
            relative_path = file_path.relative_to(self.root_path)
            parts = relative_path.parts

            current_level = structure
            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

            if "__files__" not in current_level:
                current_level["__files__"] = []
            current_level["__files__"].append(parts[-1])

        def render_tree(node: dict[str, Any], prefix: str = "", is_final: bool = True) -> None:
            entries = []
            for key in sorted(node.keys()):
                if key != "__files__":
                    entries.append((key, True))

            if "__files__" in node:
                for file in sorted(node["__files__"]):
                    entries.append((file, False))

            for i, (name, is_directory) in enumerate(entries):
                is_last_entry = i == len(entries) - 1
                connector = "└── " if is_last_entry else "├── "
                tree_output.append(f"{prefix}{connector}{name}{'/' if is_directory else ''}")

                if is_directory:
                    extension = "    " if is_last_entry else "│   "
                    render_tree(node[name], prefix + extension, is_last_entry)

        tree_output.append(f"{self.root_path.name}/")
        render_tree(structure)

        return "\n".join(tree_output)
