from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = {
    "output": "code_output.txt",
    "extensions": None,  # None means use defaults
    "exclude": [
        "tests/*",
        "*.test.js",
        "*.test.ts",
        "*.spec.js",
        "*.spec.ts",
    ],
    "glob": [],  # e.g., ["*.py", "src/**/*.js"]
    "no_gitignore": False,
    "no_tree": False,
    "separator": "=" * 80,
    "clipboard": False,
    "clipboard_only": False,
    "timestamp": False,
}


def load_config(config_path: str) -> dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary with configuration values
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        config = {}

    validated_config: dict[str, Any] = {}

    if "output" in config:
        validated_config["output"] = str(config["output"])

    if "separator" in config:
        validated_config["separator"] = str(config["separator"])

    if "extensions" in config:
        ext = config["extensions"]
        if isinstance(ext, str):
            validated_config["extensions"] = ext
        elif isinstance(ext, list):
            validated_config["extensions"] = " ".join(str(e) for e in ext)
        elif ext is not None:
            validated_config["extensions"] = str(ext)

    for field in ["exclude", "glob"]:
        if field in config:
            value = config[field]
            if isinstance(value, list):
                validated_config[field] = value
            elif isinstance(value, str):
                validated_config[field] = [value]
            elif value is not None:
                validated_config[field] = [str(value)]

    for field in ["no_gitignore", "no_tree", "clipboard", "clipboard_only", "timestamp"]:
        if field in config:
            validated_config[field] = bool(config[field])

    return validated_config


def create_default_config(config_path: Path) -> None:
    """
    Create a default configuration file.

    Args:
        config_path: Path where to create the config file
    """
    config_content = """# Code-to-Txt Configuration File
# This file defines default settings for code-to-txt
# CLI arguments will override these settings

# Output file name (supports strftime formatting)
# Use timestamp: true to automatically add timestamp
output: code_output.txt

# File extensions to include
# Can be a list or space/comma-separated string
# Leave as null to use default extensions
# extensions: [.py, .js, .ts]
# extensions: ".py .js .ts"
extensions: null

# Patterns to exclude (gitignore-style)
# These are in addition to .gitignore patterns
exclude:
  - "tests/*"
  - "*.test.js"
  - "*.test.ts"
  - "*.spec.js"
  - "*.spec.ts"
  - "node_modules/*"
  - "__pycache__/*"
  - "*.pyc"

# Glob patterns to include (alternative to extensions)
# If specified, only files matching these patterns will be included
# glob:
#   - "*.py"
#   - "src/**/*.js"
#   - "**/*.tsx"
glob: []

# Ignore .gitignore files
no_gitignore: false

# Don't include directory tree in output
no_tree: false

# Separator between files
separator: "================================================================================"

# Copy output to clipboard
clipboard: false

# Copy to clipboard only (don't save file)
clipboard_only: false

# Add timestamp to output filename
timestamp: false

# Example configurations:
#
# For Python projects:
# extensions: [.py]
# exclude: ["tests/*", "*.pyc", "__pycache__/*", "venv/*"]
#
# For JavaScript/TypeScript projects:
# extensions: [.js, .ts, .jsx, .tsx]
# exclude: ["node_modules/*", "dist/*", "build/*", "*.test.js"]
#
# For C/C++ projects:
# extensions: [.c, .cpp, .h, .hpp]
# exclude: ["build/*", "*.o", "*.a"]
#
# Using glob patterns:
# glob: ["src/**/*.py", "lib/**/*.py", "*.md"]
# extensions: null
"""

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
