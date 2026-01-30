import click
from pathlib import Path
from .code_to_txt import CodeToText


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "-o",
    "--output",
    default="code_output.txt",
    help="Output file path",
    type=click.Path(),
)
@click.option(
    "-e",
    "--extensions",
    multiple=True,
    help="File extensions to include (e.g., .py .js). Can be specified multiple times.",
)
@click.option(
    "-x",
    "--exclude",
    multiple=True,
    help="Patterns to exclude (gitignore style). Can be specified multiple times.",
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
def main(path, output, extensions, exclude, no_gitignore, no_tree, separator):
    """
    Convert code files to a single text file for easy LLM consumption.

    PATH: Directory to scan (default: current directory)

    Examples:

        # Convert all code files in current directory
        code-to-txt

        # Convert specific directory to custom output
        code-to-txt ./my-project -o project.txt

        # Only include Python and JavaScript files
        code-to-txt -e .py -e .js

        # Exclude test files
        code-to-txt -x "tests/*" -x "*.test.js"

        # Don't use .gitignore and don't show tree
        code-to-txt --no-gitignore --no-tree
    """
    click.echo(f"Scanning: {path}")

    include_extensions = set(extensions) if extensions else None

    codetotxt = CodeToText(
        root_path=path,
        output_file=output,
        include_extensions=include_extensions,
        exclude_patterns=list(exclude),
        gitignore=not no_gitignore,
    )

    try:
        num_files = codetotxt.convert(
            add_tree=not no_tree,
            separator=separator,
        )

        output_path = Path(output).resolve()
        click.echo(f"Successfully processed {num_files} files")
        click.echo(f"Output saved to: {output_path}")

        size_kb = output_path.stat().st_size / 1024
        click.echo(f"File size: {size_kb:.2f} KB")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
