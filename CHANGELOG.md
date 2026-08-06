# Changelog

All notable changes to this project will be documented in this file.

## [0.3.1]

### Changed
- Rewrote README for clarity and tone
- Normalized line endings to CRLF across the repository

## [0.3.0]

### Added
- Version flag (`-v`, `--version`) to display current version
- Statistics mode (`--stats`) for detailed codebase analysis
- Dry-run mode (`--dry-run`) to preview files without processing
- File size limits (`--max-file-size`) to skip large files
- Token estimation in output for LLM consumption planning
- Skip tracking to see which files were excluded and why
- `calculate_statistics()` method for programmatic statistics access

### Changed
- Refactored codebase for better maintainability and readability
- Externalized default extensions to `.extensions` file
- Externalized default ignore patterns to `.ignore` file
- Renamed internal methods for clarity:
  - `_load_gitignore()` → `_init_pathspec()`
  - `_matches_glob_pattern()` → `_check_glob_match()`
  - `_should_include_file()` → `_check_file_inclusion()`
  - `_get_files()` → `_collect_files()`
  - `get_statistics()` → `calculate_statistics()`
  - `_generate_tree()` → `_build_tree_structure()`
- Improved code structure with cleaner function names
- Removed inline comments in favor of self-documenting code
- Enhanced docstrings for better contributor experience

### Fixed
- Critical gitignore bug: now properly reads `.gitignore` from current and parent directories (up to 5 levels)
- Cross-platform path handling: normalized path separators for consistent behavior on Windows, macOS, and Linux
- Directory filtering: properly excludes ignored directories early in traversal
- Glob pattern matching: improved pattern matching across different operating systems

## [0.2.0]

### Added
- Automatic timestamp generation for output files (`--timestamp`, `-t`)
- Clipboard support (`--clipboard`, `-c` and `--clipboard-only`)
- Glob pattern support (`--glob`, `-g`)
- Configuration file support (`.code-to-txt.yml`)
- Space and comma-separated extension input
- Expanded default file extensions
- Expanded default ignore patterns

### Changed
- Improved extension handling
- Better default configurations

### Fixed
- Various bug fixes and improvements

## [0.1.0]

### Added
- Initial release
- Basic directory to text conversion
- Directory tree generation
- .gitignore support
- Customizable separators
- Extension filtering
- Python API
- CLI interface

[0.3.1]: https://github.com/AndriiSonsiadlo/code-to-txt/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/AndriiSonsiadlo/code-to-txt/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/AndriiSonsiadlo/code-to-txt/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/AndriiSonsiadlo/code-to-txt/releases/tag/v0.1.0