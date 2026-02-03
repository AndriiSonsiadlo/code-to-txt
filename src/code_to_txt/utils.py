from pathlib import Path


def load_patterns_from_file(file_path: Path) -> set[str]:
    """Load patterns from a text file, one per line."""
    patterns = set()
    if file_path.exists():
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    patterns.add(stripped)
    return patterns
