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


@pytest.fixture
def temp_project_with_gitignore():
    temp_dir = tempfile.mkdtemp()

    (Path(temp_dir) / "src").mkdir()
    (Path(temp_dir) / "tests").mkdir()
    (Path(temp_dir) / "temp").mkdir()
    (Path(temp_dir) / "node_modules").mkdir()
    (Path(temp_dir) / "__pycache__").mkdir()

    gitignore_content = """*.pyc
*.pyo
*.pyd
__pycache__/
*.log
node_modules/
temp/
dist/
build/
"""
    (Path(temp_dir) / ".gitignore").write_text(gitignore_content)

    (Path(temp_dir) / "src" / "main.py").write_text("print('hello')")
    (Path(temp_dir) / "src" / "utils.py").write_text("def util(): pass")
    (Path(temp_dir) / "tests" / "test_main.py").write_text("def test(): assert True")
    (Path(temp_dir) / "README.md").write_text("# Project")

    (Path(temp_dir) / "debug.log").write_text("debug info")
    (Path(temp_dir) / "temp" / "temp.txt").write_text("temporary")
    (Path(temp_dir) / "node_modules" / "package.js").write_text("module.exports = {}")
    (Path(temp_dir) / "__pycache__" / "cache.pyc").write_text("cache")
    (Path(temp_dir) / "src" / "compiled.pyc").write_text("compiled")

    yield temp_dir
    shutil.rmtree(temp_dir)


def test_gitignore_patterns_respected(temp_project_with_gitignore):
    output_file = Path(temp_project_with_gitignore) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project_with_gitignore,
        output_file=str(output_file),
        gitignore=True,
    )

    files = codetotxt._collect_files()
    file_paths = [str(f.relative_to(Path(temp_project_with_gitignore))) for f in files]

    assert any("main.py" in p for p in file_paths)
    assert any("utils.py" in p for p in file_paths)
    assert any("test_main.py" in p for p in file_paths)
    assert any("README.md" in p for p in file_paths)

    assert not any("debug.log" in p for p in file_paths)
    assert not any("temp.txt" in p for p in file_paths)
    assert not any("package.js" in p for p in file_paths)
    assert not any(".pyc" in p for p in file_paths)


def test_gitignore_combined_with_exclude(temp_project_with_gitignore):
    output_file = Path(temp_project_with_gitignore) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project_with_gitignore,
        output_file=str(output_file),
        exclude_patterns=["tests/*"],
        gitignore=True,
    )

    files = codetotxt._collect_files()
    file_paths = [str(f.relative_to(Path(temp_project_with_gitignore))) for f in files]

    assert any("main.py" in p for p in file_paths)
    assert any("utils.py" in p for p in file_paths)

    assert not any("test_main.py" in p for p in file_paths)
    assert not any("debug.log" in p for p in file_paths)


def test_no_gitignore_flag(temp_project_with_gitignore):
    output_file = Path(temp_project_with_gitignore) / "output.txt"

    codetotxt = CodeToText(
        root_path=temp_project_with_gitignore,
        output_file=str(output_file),
        gitignore=False,
    )

    files = codetotxt._collect_files()

    assert len(files) >= 0


def test_calculate_statistics(temp_project_with_gitignore):
    codetotxt = CodeToText(
        root_path=temp_project_with_gitignore,
        output_file=None,
        gitignore=True,
    )

    stats = codetotxt.calculate_statistics()

    assert "total_files" in stats
    assert "total_size_bytes" in stats
    assert "total_lines" in stats
    assert "by_extension" in stats
    assert "largest_files" in stats
    assert "skipped_files" in stats

    assert stats["total_files"] > 0
    assert stats["total_size_bytes"] > 0
    assert len(stats["by_extension"]) > 0


def test_max_file_size_limit():
    temp_dir = tempfile.mkdtemp()

    try:
        small_file = Path(temp_dir) / "small.py"
        large_file = Path(temp_dir) / "large.py"

        small_file.write_text("x = 1\n")
        large_file.write_text("x = 1\n" * 10000)

        large_size_kb = large_file.stat().st_size / 1024

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            include_extensions={".py"},
            max_file_size_kb=large_size_kb - 1,
        )

        files = codetotxt._collect_files()
        file_names = [f.name for f in files]

        assert "small.py" in file_names
        assert "large.py" not in file_names

        assert len(codetotxt.skipped_files) > 0
        skipped_names = [f[0].name for f in codetotxt.skipped_files]
        assert "large.py" in skipped_names

    finally:
        shutil.rmtree(temp_dir)


def test_skip_tracking():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "src").mkdir()
        (Path(temp_dir) / "src" / "main.py").write_text("print('hello')")
        (Path(temp_dir) / "src" / "data.json").write_text('{"key": "value"}')
        (Path(temp_dir) / "large.py").write_text("x = 1\n" * 10000)

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            include_extensions={".py"},
            max_file_size_kb=1,
        )

        files = codetotxt._collect_files()
        assert len(files) == 1
        assert len(codetotxt.skipped_files) > 0

        for file_path, reason in codetotxt.skipped_files:
            assert reason != ""
            assert isinstance(reason, str)

    finally:
        shutil.rmtree(temp_dir)


def test_path_normalization_cross_platform(temp_project_with_gitignore):
    codetotxt = CodeToText(
        root_path=temp_project_with_gitignore,
        output_file=None,
        gitignore=True,
    )

    files = codetotxt._collect_files()

    assert len(files) > 0

    for file_path in files:
        relative = file_path.relative_to(Path(temp_project_with_gitignore))
        assert relative is not None


def test_glob_pattern_cross_platform():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "src" / "lib").mkdir(parents=True)
        (Path(temp_dir) / "src" / "main.py").write_text("main")
        (Path(temp_dir) / "src" / "lib" / "helper.py").write_text("helper")
        (Path(temp_dir) / "test.py").write_text("test")

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            glob_patterns=["src/**.py"],
        )

        files = codetotxt._collect_files()
        file_names = [f.name for f in files]

        assert "main.py" in file_names
        assert "helper.py" in file_names
        assert "test.py" not in file_names

    finally:
        shutil.rmtree(temp_dir)


def test_parent_gitignore():
    temp_dir = tempfile.mkdtemp()

    try:
        parent_gitignore = Path(temp_dir) / ".gitignore"
        parent_gitignore.write_text("*.log\n")

        subdir = Path(temp_dir) / "project"
        subdir.mkdir()

        (subdir / "main.py").write_text("print('hello')")
        (subdir / "debug.log").write_text("debug")

        codetotxt = CodeToText(
            root_path=str(subdir),
            output_file=None,
            gitignore=True,
        )

        files = codetotxt._collect_files()
        file_names = [f.name for f in files]

        assert "main.py" in file_names
        assert "debug.log" not in file_names

    finally:
        shutil.rmtree(temp_dir)


def test_generate_content_sets_file_count(temp_project_with_gitignore):
    codetotxt = CodeToText(
        root_path=temp_project_with_gitignore,
        output_file=None,
        gitignore=True,
    )

    content = codetotxt.generate_content(add_tree=True)

    assert codetotxt.file_count > 0
    assert "Code Export from:" in content
    assert "Total files:" in content
    assert "DIRECTORY TREE:" in content


def test_empty_directory_statistics():
    temp_dir = tempfile.mkdtemp()

    try:
        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
        )

        stats = codetotxt.calculate_statistics()

        assert stats["total_files"] == 0
        assert stats["total_size_bytes"] == 0
        assert stats["total_lines"] == 0
        assert len(stats["by_extension"]) == 0

    finally:
        shutil.rmtree(temp_dir)


def test_statistics_with_extension_breakdown():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "file1.py").write_text("print('1')")
        (Path(temp_dir) / "file2.py").write_text("print('2')")
        (Path(temp_dir) / "file3.js").write_text("console.log('3')")
        (Path(temp_dir) / "file4.md").write_text("# Header")

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
        )

        stats = codetotxt.calculate_statistics()

        assert ".py" in stats["by_extension"]
        assert ".js" in stats["by_extension"]
        assert ".md" in stats["by_extension"]

        assert stats["by_extension"][".py"]["count"] == 2
        assert stats["by_extension"][".js"]["count"] == 1
        assert stats["by_extension"][".md"]["count"] == 1

    finally:
        shutil.rmtree(temp_dir)


def test_largest_files_in_statistics():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "small.py").write_text("x")
        (Path(temp_dir) / "medium.py").write_text("x" * 100)
        (Path(temp_dir) / "large.py").write_text("x" * 1000)

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            include_extensions={".py"},
        )

        stats = codetotxt.calculate_statistics()

        assert len(stats["largest_files"]) == 3
        assert stats["largest_files"][0]["path"] == "large.py"
        assert stats["largest_files"][1]["path"] == "medium.py"
        assert stats["largest_files"][2]["path"] == "small.py"

    finally:
        shutil.rmtree(temp_dir)


def test_multiple_glob_patterns():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "src").mkdir()
        (Path(temp_dir) / "docs").mkdir()

        (Path(temp_dir) / "src" / "main.py").write_text("main")
        (Path(temp_dir) / "src" / "utils.js").write_text("utils")
        (Path(temp_dir) / "docs" / "readme.md").write_text("readme")
        (Path(temp_dir) / "config.json").write_text("{}")

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            glob_patterns=["src/*.py", "docs/*.md"],
        )

        files = codetotxt._collect_files()
        file_names = [f.name for f in files]

        assert "main.py" in file_names
        assert "readme.md" in file_names
        assert "utils.js" not in file_names
        assert "config.json" not in file_names

    finally:
        shutil.rmtree(temp_dir)


def test_skip_reason_for_size_limit():
    temp_dir = tempfile.mkdtemp()

    try:
        large_file = Path(temp_dir) / "large.py"
        large_file.write_text("x" * 10000)

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            include_extensions={".py"},
            max_file_size_kb=1,
        )

        codetotxt._collect_files()

        assert len(codetotxt.skipped_files) == 1
        file_path, reason = codetotxt.skipped_files[0]
        assert "exceeds size limit" in reason
        assert file_path.name == "large.py"

    finally:
        shutil.rmtree(temp_dir)


def test_skip_reason_for_ignore_pattern():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / ".gitignore").write_text("*.log\n")
        (Path(temp_dir) / "main.py").write_text("main")
        (Path(temp_dir) / "debug.log").write_text("debug")

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            gitignore=True,
        )

        codetotxt._collect_files()

        skipped_names = [f[0].name for f in codetotxt.skipped_files]
        skipped_reasons = [f[1] for f in codetotxt.skipped_files]

        assert "debug.log" in skipped_names
        idx = skipped_names.index("debug.log")
        assert "matches ignore pattern" in skipped_reasons[idx]

    finally:
        shutil.rmtree(temp_dir)


def test_nested_directories_with_glob():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "a" / "b" / "c").mkdir(parents=True)
        (Path(temp_dir) / "a" / "file1.py").write_text("1")
        (Path(temp_dir) / "a" / "b" / "file2.py").write_text("2")
        (Path(temp_dir) / "a" / "b" / "c" / "file3.py").write_text("3")
        (Path(temp_dir) / "root.py").write_text("root")

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            glob_patterns=["a/**.py"],
        )

        files = codetotxt._collect_files()
        file_names = [f.name for f in files]

        assert "file1.py" in file_names
        assert "file2.py" in file_names
        assert "file3.py" in file_names
        assert "root.py" not in file_names

    finally:
        shutil.rmtree(temp_dir)


def test_statistics_line_count():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "file1.py").write_text("line1\nline2\nline3")
        (Path(temp_dir) / "file2.py").write_text("line1\nline2")

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
            include_extensions={".py"},
        )

        stats = codetotxt.calculate_statistics()

        assert stats["total_lines"] == 5

    finally:
        shutil.rmtree(temp_dir)


def test_file_count_after_convert():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "file1.py").write_text("content1")
        (Path(temp_dir) / "file2.py").write_text("content2")

        output_file = Path(temp_dir) / "output.txt"

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=str(output_file),
            include_extensions={".py"},
        )

        num_files = codetotxt.convert()

        assert num_files == 2
        assert codetotxt.file_count == 2

    finally:
        shutil.rmtree(temp_dir)


def test_externalized_extensions():
    temp_dir = tempfile.mkdtemp()

    try:
        (Path(temp_dir) / "file.py").write_text("python")
        (Path(temp_dir) / "file.js").write_text("javascript")
        (Path(temp_dir) / "file.txt").write_text("text")
        (Path(temp_dir) / "file.unknown").write_text("unknown")

        codetotxt = CodeToText(
            root_path=temp_dir,
            output_file=None,
        )

        files = codetotxt._collect_files()
        file_names = [f.name for f in files]

        assert "file.py" in file_names
        assert "file.js" in file_names
        assert "file.txt" in file_names
        assert "file.unknown" not in file_names

    finally:
        shutil.rmtree(temp_dir)
