from datetime import datetime
from pathlib import Path

import click
import pyperclip

from . import __version__
from .code_to_txt import CodeToText
from .config import create_default_config, load_config


def display_statistics(stats: dict) -> None:
    """Display statistics about the codebase."""
    divider = "=" * 60
    click.echo(f"\n{divider}")
    click.echo("CODEBASE STATISTICS")
    click.echo(divider)
    click.echo(f"Total files: {stats['total_files']}")
    click.echo(f"Total size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
    click.echo(f"Total lines: {stats['total_lines']:,}")

    if stats["skipped_files"] > 0:
        click.echo(f"Skipped files: {stats['skipped_files']}")

    click.echo("\nFiles by extension:")
    by_ext = sorted(stats["by_extension"].items(), key=lambda x: x[1]["count"], reverse=True)
    for ext, data in by_ext[:10]:
        size_mb = data["size"] / 1024 / 1024
        click.echo(f"  {ext:15} {data['count']:5} files  {size_mb:8.2f} MB")

    if len(by_ext) > 10:
        click.echo(f"  ... and {len(by_ext) - 10} more extensions")

    if stats["largest_files"]:
        click.echo("\nLargest files:")
        for file_info in stats["largest_files"][:5]:
            click.echo(f"  {file_info['size_kb']:8.2f} KB  {file_info['path']}")

    click.echo(f"{divider}\n")


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("-o", "--output", default=None, type=click.Path(),
              help="Output file path (default: codetotxt_YYYYMMDD_HHMMSS.txt)")
@click.option("-e", "--extensions", default=None, help="File extensions to include (space or comma separated)")
@click.option("-x", "--exclude", multiple=True, help="Patterns to exclude (can be used multiple times)")
@click.option("-g", "--glob", multiple=True, help="Glob patterns to include (can be used multiple times)")
@click.option("--no-gitignore", is_flag=True, help="Don't respect .gitignore files")
@click.option("--no-tree", is_flag=True, help="Don't include directory tree in output")
@click.option("--separator", default="=" * 80, help="Separator between files")
@click.option("-c", "--clipboard", is_flag=True, help="Copy output to clipboard in addition to file")
@click.option("--clipboard-only", is_flag=True, help="Copy to clipboard only (don't save file)")
@click.option("--config", type=click.Path(exists=True), help="Path to config file (.yml or .yaml)")
@click.option("--init-config", is_flag=True, help="Create default configuration file")
@click.option("-t", "--timestamp", is_flag=True, help="Add timestamp to output filename")
@click.option("-v", "--version", is_flag=True, help="Show version and exit")
@click.option("--dry-run", is_flag=True, help="Show which files would be processed without creating output")
@click.option("--stats", is_flag=True, help="Show detailed statistics about the codebase")
@click.option("--max-file-size", type=int, default=None, help="Skip files larger than N KB")
def main(
        path: str,
        output: str | None,
        extensions: str | None,
        exclude: tuple[str, ...],
        glob: tuple[str, ...],
        no_gitignore: bool,
        no_tree: bool,
        separator: str,
        clipboard: bool,
        clipboard_only: bool,
        config: str | None,
        init_config: bool,
        timestamp: bool,
        version: bool,
        dry_run: bool,
        stats: bool,
        max_file_size: int | None,
) -> None:
    """
    Convert code files to a single text file for LLM consumption.

    PATH: Directory to scan (default: current directory)

    Examples:

        # Convert all code files in current directory with timestamp
        code-to-txt -t

        # Convert specific directory to custom output
        code-to-txt ./my-project -o project.txt

        # Include Python, C, and header files (space or comma separated)
        code-to-txt -e ".py .c .h"
        code-to-txt -e ".py,.c,.h"

        # Use glob patterns
        code-to-txt -g "*.py" -g "src/**/*.js"

        # Exclude test files
        code-to-txt -x "tests/*" -x "*.test.js"

        # Copy to clipboard
        code-to-txt --clipboard

        # Copy to clipboard only (no file)
        code-to-txt --clipboard-only

        # Create default config file
        code-to-txt --init-config

        # Use config file
        code-to-txt --config .code-to-txt.yml
    """
    if version:
        click.echo(f"v{__version__}")
        return

    if init_config:
        config_path = Path(".code-to-txt.yml")
        if config_path.exists():
            click.confirm(f"Config file {config_path} already exists. Overwrite?", abort=True)
        create_default_config(config_path)
        click.echo(f"Created default config file: {config_path}")
        click.echo("You can now edit this file and use it with --config flag")
        return

    config_data = {}
    if config:
        config_data = load_config(config)
        click.echo(f"Using config file: {config}")

    output = output or config_data.get("output")
    extensions = extensions or config_data.get("extensions")
    exclude = exclude or config_data.get("exclude", [])
    glob_patterns = glob or config_data.get("glob", [])
    no_gitignore = no_gitignore or config_data.get("no_gitignore", False)
    no_tree = no_tree or config_data.get("no_tree", False)
    separator = separator if separator == "=" * 80 else separator
    separator = config_data.get("separator", separator)
    clipboard = clipboard or config_data.get("clipboard", False)
    clipboard_only = clipboard_only or config_data.get("clipboard_only", False)
    timestamp = timestamp or config_data.get("timestamp", False)
    max_file_size = max_file_size or config_data.get("max_file_size")

    if not output or timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output:
            output_path = Path(output)
            stem = output_path.stem
            suffix = output_path.suffix or ".txt"
            output = str(output_path.parent / f"{stem}_{timestamp_str}{suffix}")
        else:
            output = f"codetotxt_{timestamp_str}.txt"

    click.echo(f"Scanning: {path}")

    include_extensions = None
    if extensions:
        if "," in extensions:
            ext_list = [e.strip() for e in extensions.split(",")]
        else:
            ext_list = extensions.split()

        include_extensions = set()
        for ext in ext_list:
            ext = ext.strip()
            if ext and not ext.startswith("."):
                ext = "." + ext
            if ext:
                include_extensions.add(ext)

    code_to_txt = CodeToText(
        root_path=path,
        output_file=output if not clipboard_only and not dry_run and not stats else None,
        include_extensions=include_extensions,
        exclude_patterns=list(exclude),
        glob_patterns=list(glob_patterns),
        gitignore=not no_gitignore,
        max_file_size_kb=max_file_size,
    )

    try:
        if stats or dry_run:
            statistics = code_to_txt.calculate_statistics()
            display_statistics(statistics)

            if stats:
                return

            if dry_run:
                files = code_to_txt._collect_files()
                click.echo("Files that would be processed:")
                for i, file_path in enumerate(files, 1):
                    relative_path = file_path.relative_to(Path(path).resolve())
                    size_kb = file_path.stat().st_size / 1024
                    click.echo(f"  {i:4}. {relative_path} ({size_kb:.1f} KB)")

                if code_to_txt.skipped_files:
                    click.echo(f"\nSkipped {len(code_to_txt.skipped_files)} files:")
                    for file_path, reason in code_to_txt.skipped_files[:20]:
                        relative_path = file_path.relative_to(Path(path).resolve())
                        click.echo(f"  - {relative_path} ({reason})")
                    if len(code_to_txt.skipped_files) > 20:
                        click.echo(f"  ... and {len(code_to_txt.skipped_files) - 20} more")

            if not stats or dry_run:
                return

        if clipboard_only:
            content = code_to_txt.generate_content(add_tree=not no_tree, separator=separator)
            pyperclip.copy(content)
            click.echo("Content copied to clipboard")
            click.echo(f"Processed {code_to_txt.file_count} files")
            click.echo(f"Content size: {len(content) / 1024:.2f} KB")

            estimated_tokens = len(content) / 4
            click.echo(f"Estimated tokens: ~{estimated_tokens:,.0f}")
        else:
            num_files = code_to_txt.convert(add_tree=not no_tree, separator=separator)

            output_path = Path(output).resolve()
            click.echo(f"Successfully processed {num_files} files")
            click.echo(f"Output saved to: {output_path}")

            size_kb = output_path.stat().st_size / 1024
            click.echo(f"File size: {size_kb:.2f} KB")

            estimated_tokens = size_kb * 1024 / 4
            click.echo(f"Estimated tokens: ~{estimated_tokens:,.0f}")

            if clipboard:
                content = output_path.read_text(encoding="utf-8")
                pyperclip.copy(content)
                click.echo("Content also copied to clipboard")

            if code_to_txt.skipped_files:
                click.echo(f"\nNote: Skipped {len(code_to_txt.skipped_files)} files (use --dry-run to see details)")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
