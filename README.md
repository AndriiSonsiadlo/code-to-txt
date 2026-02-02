# CodeToTxt

A small Python package to convert code to text.
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
# Convert all code files in current directory with timestamp
code-to-txt -t

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
output: codetotxt.txt

# File extensions to include (null = use defaults)
extensions: null

# Patterns to exclude
exclude:
  - "tests/*"
  - "*.test.js"
  - "node_modules/*"

# Glob patterns (alternative to extensions)
glob: [ ]

# Options
no_gitignore: false
no_tree: false
separator: "================"
clipboard: false
clipboard_only: false
timestamp: false
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
```

**JavaScript/TypeScript Project:**

```yaml
extensions: [ .js, .ts, .jsx, .tsx ]
exclude: [ "node_modules/*", "dist/*", "build/*", "*.test.js", "*.spec.ts" ]
no_tree: false
```

**C/C++ Project:**

```yaml
extensions: [ .c, .cpp, .h, .hpp ]
exclude: [ "build/*", "*.o", "*.a", "cmake-build-*" ]
```

**Using Glob Patterns:**

```yaml
glob: [ "src/**/*.py", "lib/**/*.py", "*.md" ]
extensions: null  # Ignore extensions when using glob
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
  --separator TEXT        Separator between files (default: ====...)
  -c, --clipboard         Copy output to clipboard in addition to file
  --clipboard-only        Copy to clipboard only (don't save file)
  --config PATH           Path to config file (.yml or .yaml)
  --init-config           Create default configuration file
  -t, --timestamp         Add timestamp to output filename
  --help                  Show this message and exit
```

## Python API

### Basic Usage

```python
from code_to_txt import CodeToText

# Create instance
code_to_text = CodeToText(
    root_path="./my-project",
    output_file="output.txt",
    include_extensions={".py", ".js"},
)

# Convert to file
num_files = code_to_text.convert(add_tree=True)
print(f"Processed {num_files} files")
```

### Generate Content for Clipboard

```python
from code_to_txt import CodeToText

# Generate content without writing to file
code_to_text = CodeToText(
    root_path="./my-project",
    output_file=None,  # No file needed
    include_extensions={".py"},
)

content = code_to_text.generate_content(add_tree=True)
print(f"Generated {len(content)} characters")

# Copy to clipboard using pyperclip
import pyperclip

pyperclip.copy(content)
```

### Using Glob Patterns

```python
from code_to_txt import CodeToText

code_to_text = CodeToText(
    root_path="./my-project",
    output_file="output.txt",
    glob_patterns=["*.py", "src/**/*.js", "**/*.md"],
)

num_files = code_to_text.convert()
```

### Advanced Configuration

```python
from code_to_txt import CodeToText

code_to_text = CodeToText(
    root_path="./my-project",
    output_file="detailed_output.txt",
    include_extensions={".py", ".js", ".ts"},
    exclude_patterns=["tests/*", "*.test.js", "node_modules/*"],
    gitignore=True,  # Respect .gitignore (default)
)

num_files = code_to_text.convert(
    add_tree=True,
    separator="=" * 100,
)
```
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

### For Large Projects

```bash
# Use specific extensions to reduce size
code-to-txt -e ".py" -t

# Exclude heavy directories
code-to-txt -x "node_modules/*" -x "venv/*" -x "dist/*"
```

### For LLM Consumption

```bash
# Copy directly to clipboard for pasting into ChatGPT/Claude
code-to-txt --clipboard-only -e ".py .md"

# Or save and copy
code-to-txt -t -c -e ".py .js"
```

### For Specific Features

```bash
# Only include source files, exclude tests
code-to-txt -g "src/**/*.py" -g "lib/**/*.py"

# Only documentation
code-to-txt -e ".md .rst .txt"
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
### v0.1.0

- 🎉 Initial release
- 📁 Basic directory to text conversion
- 🌳 Directory tree generation
- 🚫 .gitignore support
- 🎨 Customizable separators

## Acknowledgments

Created by Andrii Sonsiadlo
