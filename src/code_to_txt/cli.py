from datetime import datetime
from pathlib import Path

import click
import pyperclip

from .code_to_txt import CodeToText
from .config import create_default_config, load_config


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "-o",
    "--output",
    default=None,
    help="Output file path (default: codetotxt_YYYYMMDD_HHMMSS.txt)",
    type=click.Path(),
)
@click.option(
    "-e",
    "--extensions",
    default=None,
    help="File extensions to include. Space-separated list (e.g., '.py .js .ts') or comma-separated (e.g., '.py,.js,.ts')",
)
@click.option(
    "-x",
    "--exclude",
    multiple=True,
    help="Patterns to exclude (gitignore style). Can be specified multiple times.",
)
@click.option(
    "-g",
    "--glob",
    multiple=True,
    help="Glob patterns to include (e.g., '*.py' 'src/**/*.js'). Can be specified multiple times.",
)
@click.option(
    "--no-gitignore",
    is_flag=True,
    help="Don't respect .gitignore files",
)
@click.option(
    "--no-tree",
    is_flag=True,
    help="Don't include directory tree in output",
)
@click.option(
    "--separator",
    default="=" * 80,
    help="Separator between files",
)
@click.option(
    "--clipboard",
    "-c",
    is_flag=True,
    help="Copy output to clipboard in addition to saving to file",
)
@click.option(
    "--clipboard-only",
    is_flag=True,
    help="Copy output to clipboard only (don't save to file)",
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to config file (.yml or .yaml)",
)
@click.option(
    "--init-config",
    is_flag=True,
    help="Create default configuration file (.code-to-txt.yml)",
)
@click.option(
    "--timestamp",
    "-t",
    is_flag=True,
    help="Add timestamp to output filename",
)
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
) -> None:
    """
    Convert code files to a single text file for easy LLM consumption.

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
    if init_config:
        config_path = Path(".code-to-txt.yml")
        if config_path.exists():
            click.confirm(
                f"Config file {config_path} already exists. Overwrite?",
                abort=True,
            )
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

    codetotxt = CodeToText(
        root_path=path,
        output_file=output if not clipboard_only else None,
        include_extensions=include_extensions,
        exclude_patterns=list(exclude),
        glob_patterns=list(glob_patterns),
        gitignore=not no_gitignore,
    )

    try:
        if clipboard_only:
            content = codetotxt.generate_content(
                add_tree=not no_tree,
                separator=separator,
            )
            pyperclip.copy(content)
            click.echo("Content copied to clipboard")
            click.echo(f"Processed {codetotxt.file_count} files")
            click.echo(f"Content size: {len(content) / 1024:.2f} KB")
        else:
            num_files = codetotxt.convert(
                add_tree=not no_tree,
                separator=separator,
            )

            output_path = Path(output).resolve()
            click.echo(f"Successfully processed {num_files} files")
            click.echo(f"Output saved to: {output_path}")

            size_kb = output_path.stat().st_size / 1024
            click.echo(f"File size: {size_kb:.2f} KB")

            if clipboard:
                content = output_path.read_text(encoding="utf-8")
                pyperclip.copy(content)
                click.echo("Content also copied to clipboard")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
