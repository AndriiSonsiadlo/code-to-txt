import os
from pathlib import Path
from typing import List, Optional, Set
import pathspec


class CodeToText:
    DEFAULT_IGNORE = {
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd"
    }

    DEFAULT_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h"
    }

    def __init__(
            self,
            root_path: str,
            output_file: str = "output.txt",
            include_extensions: Optional[Set[str]] = None,
            exclude_patterns: Optional[List[str]] = None,
            gitignore: bool = True,
    ):
        """
        Initialize the instance of CodeToText.

        Args:
            root_path: Root directory to scan
            output_file: Output file path
            include_extensions: Set of file extensions to include (with dots)
            exclude_patterns: List of patterns to exclude (gitignore style)
            gitignore: Whether to respect .gitignore files
        """
        self.root_path = Path(root_path).resolve()
        self.output_file = output_file
        self.include_extensions = include_extensions or self.DEFAULT_EXTENSIONS
        self.exclude_patterns = exclude_patterns or []
        self.gitignore = gitignore
        self.spec = None

        if self.gitignore:
            self._load_gitignore()

    def _load_gitignore(self):
        """Load .gitignore patterns if present."""
        gitignore_path = self.root_path / ".gitignore"
        patterns = list(self.DEFAULT_IGNORE)

        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)

        patterns.extend(self.exclude_patterns)
        self.spec = pathspec.PathSpec.from_lines("gitignore", patterns)

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included."""
        # Check extension
        if file_path.suffix not in self.include_extensions:
            return False

        if self.spec:
            relative_path = file_path.relative_to(self.root_path)
            if self.spec.match_file(str(relative_path)):
                return False

        return True

    def _get_files(self) -> List[Path]:
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

    def convert(self, add_tree: bool = True, separator: str = "=" * 80) -> int:
        """
        Convert files to single text file.

        Args:
            add_tree: Whether to add directory tree at the beginning
            separator: Separator between files

        Returns:
            Number of files processed
        """
        files = self._get_files()

        with open(self.output_file, "w", encoding="utf-8") as out:
            out.write(f"Code Export from: {self.root_path}\n")
            out.write(f"Total files: {len(files)}\n")
            out.write(f"{separator}\n\n")

            if add_tree:
                out.write("DIRECTORY TREE:\n")
                out.write(separator + "\n")
                out.write(self._generate_tree())
                out.write(f"\n{separator}\n\n")

            for i, file_path in enumerate(files, 1):
                relative_path = file_path.relative_to(self.root_path)

                out.write(f"FILE {i}/{len(files)}: {relative_path}\n")
                out.write(separator + "\n")

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    out.write(content)
                except UnicodeDecodeError:
                    out.write(f"[Binary file - skipped]\n")
                except Exception as e:
                    out.write(f"[Error reading file: {e}]\n")

                out.write(f"\n{separator}\n\n")

        return len(files)

    def _generate_tree(self) -> str:
        """Generate a directory tree representation."""
        tree_lines = []
        files = self._get_files()

        dir_structure = {}
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

        def print_tree(structure, prefix="", is_last=True):
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
