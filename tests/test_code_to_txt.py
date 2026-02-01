import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from code_to_txt import CodeToText
from code_to_txt.config import create_default_config, load_config


@pytest.fixture
def temp_project():
    temp_dir = tempfile.mkdtemp()

    (Path(temp_dir) / "src").mkdir()
    (Path(temp_dir) / "tests").mkdir()
    (Path(temp_dir) / "lib").mkdir()

    (Path(temp_dir) / "src" / "main.py").write_text("print('hello')")
    (Path(temp_dir) / "src" / "utils.py").write_text("def util(): pass")
    (Path(temp_dir) / "lib" / "helper.py").write_text("def helper(): return True")
    (Path(temp_dir) / "tests" / "test_main.py").write_text("def test(): assert True")
    (Path(temp_dir) / "README.md").write_text("# Project")
    (Path(temp_dir) / "config.json").write_text('{"key": "value"}')
    (Path(temp_dir) / "script.sh").write_text("#!/bin/bash\necho 'test'")

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
    assert num_files == 4

    content = output_file.read_text()
    assert ".py" in content
    assert "README.md" not in content or content.count("README.md") == 1  # Only in header


def test_codetotxt_exclusion(temp_project):
    output_file = Path(temp_project) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
        exclude_patterns=["tests/*"],
    )

    num_files = codetotxt.convert()
    content = output_file.read_text()

    assert num_files == 6
    assert "test_main.py" not in content or "Binary file" in content


def test_codetotxt_glob_patterns(temp_project):
    output_file = Path(temp_project) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
        glob_patterns=["*.py", "*.sh"],
    )

    num_files = codetotxt.convert()
    assert num_files == 5

    content = output_file.read_text()
    assert "main.py" in content
    assert "script.sh" in content
    assert content.count("README.md") <= 1
    assert content.count("config.json") <= 1


def test_codetotxt_glob_patterns_subdirs(temp_project):
    output_file = Path(temp_project) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
        glob_patterns=["src/*.py"],
    )

    num_files = codetotxt.convert()
    assert num_files == 2

    content = output_file.read_text()
    assert "main.py" in content
    assert "utils.py" in content
    assert "test_main.py" not in content or content.count("test_main.py") == 1
    assert "helper.py" not in content or content.count("helper.py") == 1


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


def test_generate_content_for_clipboard(temp_project):
    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=None,
        include_extensions={".py"},
    )

    content = codetotxt.generate_content(add_tree=True)

    assert isinstance(content, str)
    assert len(content) > 0
    assert "Code Export from:" in content
    assert "main.py" in content
    print("content", content)
    assert codetotxt.file_count == 4


def test_config_loading(temp_project):
    config_path = Path(temp_project) / "test_config.yml"

    config_data = {
        "output": "custom_output.txt",
        "extensions": ".py .js",
        "exclude": ["tests/*", "*.test.py"],
        "no_gitignore": True,
        "timestamp": True,
    }

    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    loaded_config = load_config(str(config_path))

    assert loaded_config["output"] == "custom_output.txt"
    assert loaded_config["extensions"] == ".py .js"
    assert "tests/*" in loaded_config["exclude"]
    assert loaded_config["no_gitignore"] is True
    assert loaded_config["timestamp"] is True


def test_create_default_config(temp_project):
    config_path = Path(temp_project) / ".code-to-txt.yml"

    create_default_config(config_path)

    assert config_path.exists()

    content = config_path.read_text()
    assert "output:" in content
    assert "extensions:" in content
    assert "exclude:" in content


def test_empty_directory():
    temp_dir = tempfile.mkdtemp()
    output_file = Path(temp_dir) / "output.txt"

    try:
        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=str(output_file),
        )

        num_files = codetotxt.convert()

        assert num_files == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "Total files: 0" in content

    finally:
        shutil.rmtree(temp_dir)


def test_separator_customization(temp_project):
    output_file = Path(temp_project) / "output.txt"
    custom_sep = "-" * 60

    codetotxt = CodeToText(
        root_path=temp_project,
        output_file=str(output_file),
        include_extensions={".py"},
    )

    codetotxt.convert(separator=custom_sep)

    content = output_file.read_text()
    assert custom_sep in content
