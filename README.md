# CodeToTxt

CodeToTxt is a small Python tool that flattens a codebase into a single text file. It's built for feeding code into
LLMs, but it works just as well for code review, documentation, or just having a searchable snapshot of a project.

## Features

- Convert an entire directory of code into one text file
- Optional directory tree at the top of the output
- Respects `.gitignore` automatically (including parent directories)
- Filter files by extension or glob pattern
- Custom separators and output formatting
- Copy straight to the clipboard instead of (or in addition to) writing a file
- Dry-run and stats modes to see what you're about to process before you commit to it
- Config file support so you don't have to repeat the same flags every time
- Token estimate in the output, since that's usually what people actually care about

## Installation

```bash
pip install code-to-txt
```

Or with Poetry:

```bash
poetry add code-to-txt
```

## Quick start

```bash
# Show version
code-to-txt --version

# Convert everything in the current directory, with a timestamped filename
code-to-txt -t

# See what would be processed without writing anything
code-to-txt --dry-run

# Get a quick summary of the codebase
code-to-txt --stats

# Convert a specific directory
code-to-txt ./my-project -o project.txt

# Skip the file and just copy the result to the clipboard
code-to-txt --clipboard-only
```

### Choosing file types

```bash
# Multiple extensions (space or comma separated, both work)
code-to-txt -e ".py .js .ts"
code-to-txt -e ".py,.js,.ts"

# Or use glob patterns instead
code-to-txt -g "*.py" -g "src/**/*.js"
```

### More options

```bash
# Skip files above a certain size (handy for staying under token limits)
code-to-txt --max-file-size 500

# Exclude specific patterns
code-to-txt -x "tests/*" -x "*.test.js"

# Ignore .gitignore entirely
code-to-txt --no-gitignore

# Leave out the directory tree
code-to-txt --no-tree

# Use a different separator between files
code-to-txt --separator "---"

# Combine whatever you need
code-to-txt -t -c -e ".py .js" -x "tests/*"
```

## Configuration file

Rather than typing the same flags every time, you can generate a config file:

```bash
code-to-txt --init-config
```

This creates `.code-to-txt.yml`:

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
glob: []

# Options
no_gitignore: false
no_tree: false
separator: "================"
clipboard: false
clipboard_only: false
timestamp: true
max_file_size: null
```

Then point the CLI at it:

```bash
code-to-txt --config .code-to-txt.yml
```

Any CLI flag you pass will override the matching setting in the config file.

### A few example configs

**Python project:**

```yaml
extensions: [ .py ]
exclude: [ "tests/*", "*.pyc", "__pycache__/*", "venv/*", ".venv/*" ]
timestamp: true
max_file_size: 500
```

**JavaScript/TypeScript project:**

```yaml
extensions: [ .js, .ts, .jsx, .tsx ]
exclude: [ "node_modules/*", "dist/*", "build/*", "*.test.js", "*.spec.ts" ]
no_tree: false
max_file_size: 1000
```

**Tuned for LLM input:**

```yaml
extensions: [ .py, .js, .md ]
exclude: [ "tests/*", "*.test.*", "node_modules/*", "dist/*", "build/*" ]
timestamp: true
clipboard: true
max_file_size: 200
no_tree: false
```

## Command line options

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

## Using it as a library

You don't need the CLI. Everything is available directly from the `CodeToText` class.

### Basic conversion

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

### Generating content without writing to disk

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

### Getting statistics

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

### Using glob patterns

```python
from code_to_txt import CodeToText

code_to_txt = CodeToText(
    root_path="./my-project",
    output_file="output.txt",
    glob_patterns=["*.py", "src/**/*.js", "**/*.md"],
)

num_files = code_to_txt.convert()
```

## Default file extensions

If you don't specify extensions or glob patterns, CodeToTxt includes these by default:

- Python: `.py`
- JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx`
- Systems languages: `.c`, `.cpp`, `.h`, `.hpp`, `.java`, `.cs`, `.go`, `.rs`
- Web: `.html`, `.css`, `.scss`
- Config: `.yaml`, `.yml`, `.json`, `.toml`, `.xml`
- Docs: `.md`, `.txt`, `.rst`
- Scripts: `.sh`, `.bash`, `.zsh`
- Other: `.rb`, `.php`, `.swift`, `.kt`, `.scala`, `.r`, `.sql`

## Default ignore patterns

These are excluded automatically, on top of whatever's in your `.gitignore` (parent directories included, up to five
levels up):

- `__pycache__`, `*.pyc`, `*.pyo`, `*.pyd`
- `.git`, `.svn`, `.hg`
- `node_modules`
- `.venv`, `venv`, `.env`
- `*.egg-info`, `dist`, `build`
- `.pytest_cache`, `.mypy_cache`, `.ruff_cache`
- `*.so`, `*.dylib`, `*.dll`

## Output format

The generated file has three parts:

1. A header with the source directory and total file count
2. An optional directory tree
3. Each file's contents, labeled with its relative path

For example:

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

## Where this is useful

- Sharing a whole codebase with someone in one file, for review
- Feeding a project into ChatGPT, Claude, or another AI assistant
- Generating a quick reference document for a project
- Doing plain-text search across an entire codebase at once
- Producing input for other code analysis tools
- Keeping a simple, flat backup of a project's source

## Tips

### Preparing input for an LLM

```bash
# See what you're dealing with first
code-to-txt --stats

# Preview with a size cap
code-to-txt --dry-run --max-file-size 200

# Then copy it straight to the clipboard
code-to-txt --clipboard-only --max-file-size 200 -e ".py .md"
```

### Working with large projects

```bash
# Narrow it down to the extensions you actually care about
code-to-txt -e ".py" -t --max-file-size 500

# Cut out the usual heavy directories
code-to-txt -x "node_modules/*" -x "venv/*" -x "dist/*"

# Check the size before generating anything
code-to-txt --stats --max-file-size 300
```

### Debugging what's being skipped

```bash
# See exactly which files are excluded and why
code-to-txt --dry-run

# Compare with .gitignore turned off
code-to-txt --dry-run --no-gitignore
```

## Requirements

- Python 3.10+
- Dependencies: `click`, `gitpython`, `pathspec`, `pyperclip`, `pyyaml`

## Development

```bash
# Clone the repository
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

Contributions are welcome. Feel free to open a pull request.

## License

MIT License. See the LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history of changes.

## Author

Created by Andrii Sonsiadlo.
