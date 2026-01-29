import pytest
from pathlib import Path
import tempfile
import shutil
from code_to_txt import CodeToText


@pytest.fixture
def temp_project():
    temp_dir = tempfile.mkdtemp()

    (Path(temp_dir) / "src").mkdir()
    (Path(temp_dir) / "tests").mkdir()

    (Path(temp_dir) / "src" / "main.py").write_text("print('hello')")
    (Path(temp_dir) / "src" / "utils.py").write_text("def util(): pass")
    (Path(temp_dir) / "tests" / "test_main.py").write_text("def test(): assert True")
    (Path(temp_dir) / "README.md").write_text("# Project")

    yield temp_dir

    shutil.rmtree(temp_dir)


def test_codetotxt_basic(temp_project):
    output_file = Path(temp_project) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
    )

    num_files = codetotxt.convert()

    assert num_files > 0
    assert output_file.exists()

    content = output_file.read_text()
    assert "Code Export from:" in content
    assert "main.py" in content


def test_codetotxt_with_extensions(temp_project):
    output_file = Path(temp_project) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
        include_extensions={".py"},
    )

    num_files = codetotxt.convert()

    content = output_file.read_text()
    assert ".py" in content
    assert "README.md" not in content or content.count("README.md") < 2


def test_codetotxt_exclusion(temp_project):
    output_file = Path(temp_project) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
        exclude_patterns=["tests/*"],
    )

    num_files = codetotxt.convert()

    content = output_file.read_text()
    assert "test_main.py" not in content or "Binary file" in content


def test_tree_generation(temp_project):
    output_file = Path(temp_project) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
    )

    codetotxt.convert(add_tree=True)

    content = output_file.read_text()
    assert "DIRECTORY TREE:" in content
    assert "├──" in content or "└──" in content
