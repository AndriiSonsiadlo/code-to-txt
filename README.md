# CodeToTxt

A powerful Python package to convert code files into a single text file, perfect for feeding into Large Language
Models (LLMs) or for easy code review and documentation.

## Features

**Core Features:**

- 📁 Convert entire directories of code into a single text file
- 🌳 Optional directory tree visualization
- 🚫 Respects `.gitignore` patterns automatically
- 🎨 Customizable file separators and output format
- 🔧 Flexible file filtering by extension or glob patterns
- 📦 Easy to use CLI and Python API

## Installation

```bash
pip install code-to-txt
```

Or with Poetry:

```bash
poetry add code-to-txt
```

## Quick Start

### Basic Usage

```bash
# Show version
code-to-txt --version

# Convert all code files with timestamp
code-to-txt -t

# Preview what would be processed
code-to-txt --dry-run

# Get codebase statistics
code-to-txt --stats

# Convert specific directory
code-to-txt ./my-project -o project.txt

# Copy to clipboard instead of saving
code-to-txt --clipboard-only
```

### Specify File Types

```bash
# Multiple extensions (space or comma separated)
code-to-txt -e ".py .js .ts"
code-to-txt -e ".py,.js,.ts"

# Using glob patterns
code-to-txt -g "*.py" -g "src/**/*.js"
code-to-txt -g "*.py" -g "*.md"
```

### Advanced Usage

```bash
# Limit file sizes (useful for LLM token limits)
code-to-txt --max-file-size 500

# Exclude patterns
code-to-txt -x "tests/*" -x "*.test.js"

# Don't use .gitignore
code-to-txt --no-gitignore

# Don't show directory tree
code-to-txt --no-tree

# Custom separator
code-to-txt --separator "---"

# Combine options
code-to-txt -t -c -e ".py .js" -x "tests/*"
```

## Configuration File

Create a default configuration file:

```bash
code-to-txt --init-config
```

This creates `.code-to-txt.yml` with default settings:

```yaml
# Output file name
output: code-to-txt.txt

# File extensions to include (null = use defaults)
extensions: null

# Patterns to exclude
exclude:
  - "tests/*"
  - "*.test.js"
  - "*.test.ts"
  - "*.spec.js"
  - "*.spec.ts"
  - "node_modules/*"
  - "__pycache__/*"
  - "*.pyc"

# Glob patterns (alternative to extensions)
glob: [ ]

# Options
no_gitignore: false
no_tree: false
separator: "================"
clipboard: false
clipboard_only: false
timestamp: false
max_file_size: null
```

Use the config file:

```bash
code-to-txt --config .code-to-txt.yml
```

**Note:** CLI arguments override config file settings.

### Example Configurations

**Python Project:**

```yaml
extensions: [ .py ]
exclude: [ "tests/*", "*.pyc", "__pycache__/*", "venv/*", ".venv/*" ]
timestamp: true
max_file_size: 500
```

**JavaScript/TypeScript Project:**

```yaml
extensions: [ .js, .ts, .jsx, .tsx ]
exclude: [ "node_modules/*", "dist/*", "build/*", "*.test.js", "*.spec.ts" ]
no_tree: false
max_file_size: 1000
```

**LLM-Optimized:**

```yaml
extensions: [ .py, .js, .md ]
exclude: [ "tests/*", "*.test.*", "node_modules/*", "dist/*", "build/*" ]
timestamp: true
clipboard: true
max_file_size: 200
no_tree: false
```

## Command Line Options

```
Usage: code-to-txt [OPTIONS] [PATH]

Arguments:
  PATH                    Directory to scan (default: current directory)

Options:
  -o, --output PATH       Output file path (default: codetotxt_YYYYMMDD_HHMMSS.txt)
  -e, --extensions TEXT   File extensions to include (space or comma separated)
  -x, --exclude TEXT      Patterns to exclude (can be used multiple times)
  -g, --glob TEXT         Glob patterns to include (can be used multiple times)
  --no-gitignore          Don't respect .gitignore files
  --no-tree               Don't include directory tree in output
  --separator TEXT        Separator between files
  -c, --clipboard         Copy output to clipboard in addition to file
  --clipboard-only        Copy to clipboard only (don't save file)
  --config PATH           Path to config file (.yml or .yaml)
  --init-config           Create default configuration file
  -t, --timestamp         Add timestamp to output filename
  -v, --version           Show version and exit
  --dry-run               Show which files would be processed
  --stats                 Show detailed statistics
  --max-file-size INT     Skip files larger than N KB
  --help                  Show this message and exit
```

## Python API

### Basic Usage

```python
from code_to_txt import CodeToText

code_to_txt = CodeToText(
    root_path="./my-project",
    output_file="output.txt",
    include_extensions={".py", ".js"},
)

num_files = code_to_txt.convert(add_tree=True)
print(f"Processed {num_files} files")
```

### Generate Content for Clipboard

```python
from code_to_txt import CodeToText
import pyperclip

code_to_txt = CodeToText(
    root_path="./my-project",
    output_file=None,
    include_extensions={".py"},
)

content = code_to_txt.generate_content(add_tree=True)
pyperclip.copy(content)
```

### Get Statistics

```python
from code_to_txt import CodeToText

code_to_txt = CodeToText(
    root_path="./my-project",
    output_file=None,
    max_file_size_kb=500,
)

stats = code_to_txt.calculate_statistics()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
print(f"Total lines: {stats['total_lines']:,}")
```

### Using Glob Patterns

```python
from code_to_txt import CodeToText

code_to_txt = CodeToText(
    root_path="./my-project",
    output_file="output.txt",
    glob_patterns=["*.py", "src/**/*.js", "**/*.md"],
)

num_files = code_to_txt.convert()
```

## Default File Extensions

When no extensions are specified, CodeToTxt includes these file types by default:

- **Python:** `.py`
- **JavaScript/TypeScript:** `.js`, `.ts`, `.jsx`, `.tsx`
- **Systems:** `.c`, `.cpp`, `.h`, `.hpp`, `.java`, `.cs`, `.go`, `.rs`
- **Web:** `.html`, `.css`, `.scss`
- **Config:** `.yaml`, `.yml`, `.json`, `.toml`, `.xml`
- **Documentation:** `.md`, `.txt`, `.rst`
- **Scripts:** `.sh`, `.bash`, `.zsh`
- **Other:** `.rb`, `.php`, `.swift`, `.kt`, `.scala`, `.r`, `.sql`

## Default Ignore Patterns

CodeToTxt automatically ignores common build artifacts and dependencies:

- `__pycache__`, `*.pyc`, `*.pyo`, `*.pyd`
- `.git`, `.svn`, `.hg`
- `node_modules`
- `.venv`, `venv`, `.env`
- `*.egg-info`, `dist`, `build`
- `.pytest_cache`, `.mypy_cache`, `.ruff_cache`
- `*.so`, `*.dylib`, `*.dll`

Plus any patterns in your `.gitignore` file (including parent directories).

## Output Format

The generated file includes:

1. **Header:** Source directory and file count
2. **Directory Tree:** Visual representation of the file structure (optional)
3. **File Contents:** Each file with its relative path and content

Example output:

```
Code Export from: /path/to/project
Total files: 4
================================================================================

DIRECTORY TREE:
================================================================================
my-project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md

================================================================================

FILE 1/4: src/main.py
================================================================================
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()

================================================================================
...
```

## Use Cases

- 📚 **Code Review:** Share entire codebase in a single file
- 🤖 **LLM Input:** Feed code to ChatGPT, Claude, or other AI assistants
- 📖 **Documentation:** Create comprehensive code documentation
- 🔍 **Code Search:** Easy text-based search across entire project
- 📊 **Analysis:** Input for code analysis tools
- 💾 **Archival:** Simple code backup format

## Tips & Tricks

### For LLM Consumption

```bash
# Step 1: Check what you're working with
code-to-txt --stats

# Step 2: Preview files
code-to-txt --dry-run --max-file-size 200

# Step 3: Copy to clipboard with size limit
code-to-txt --clipboard-only --max-file-size 200 -e ".py .md"

# See token estimate:
# Estimated tokens: ~95,000
```

### For Large Projects

```bash
# Use specific extensions to reduce size
code-to-txt -e ".py" -t --max-file-size 500

# Exclude heavy directories
code-to-txt -x "node_modules/*" -x "venv/*" -x "dist/*"

# Get statistics first
code-to-txt --stats --max-file-size 300
```

### Debug Ignore Patterns

```bash
# See which files are being skipped and why
code-to-txt --dry-run

# Compare with and without gitignore
code-to-txt --dry-run --no-gitignore
```

## Requirements

- Python 3.10+
- Dependencies: `click`, `gitpython`, `pathspec`, `pyperclip`, `pyyaml`

## Development

```bash
# Clone repository
git clone https://github.com/AndriiSonsiadlo/code-to-txt.git
cd code-to-txt

# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .
poetry run mypy src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.3.0

- 🔧 Refactored codebase for better maintainability
- 📁 Externalized default extensions and ignore patterns to separate files
- 🐛 Fixed critical gitignore bug (now checks parent directories)
- 🔍 Improved cross-platform path handling
- 📊 Added `--stats` flag for detailed codebase statistics
- 🎯 Added `--dry-run` mode to preview without processing
- 📏 Added `--max-file-size` to skip large files
- 🔢 Added token estimation for LLM consumption
- 📝 Added skip tracking to see which files were excluded
- 🚀 Improved method naming and code structure
- ✅ Enhanced test coverage

### v0.2.0

- ✨ Added automatic timestamp generation for output files
- 📋 Added clipboard support (`--clipboard` and `--clipboard-only`)
- 🎯 Improved extension handling (space/comma separated)
- 🔍 Added glob pattern support
- ⚙️ Added configuration file support (`.code-to-txt.yml`)
- 🚀 Expanded default file extensions and ignore patterns
- 🐛 Various bug fixes and improvements

### v0.1.0

- 🎉 Initial release
- 📁 Basic directory to text conversion
- 🌳 Directory tree generation
- 🚫 .gitignore support
- 🎨 Customizable separators

## Acknowledgments

Created by Andrii Sonsiadlo
