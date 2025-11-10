import pytest
from restack_gen.core.project import ProjectStructure
from pathlib import Path


def test_project_structure_init_default():
    proj = ProjectStructure()
    assert proj.root == Path.cwd()


def test_project_structure_init_with_root(tmp_path):
    proj = ProjectStructure(tmp_path)
    assert proj.root == tmp_path


def test_project_structure_find_root_with_marker(tmp_path):
    # Create a marker file
    marker = tmp_path / "restack.toml"
    marker.write_text("")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    proj = ProjectStructure(subdir)
    assert proj.root == tmp_path


def test_project_structure_find_root_no_marker(tmp_path):
    proj = ProjectStructure(tmp_path)
    assert proj.root == tmp_path


def test_project_structure_properties(tmp_path):
    proj = ProjectStructure(tmp_path)
    assert proj.src_dir == tmp_path / "src"
    assert proj.tests_dir == tmp_path / "tests"
    assert proj.scripts_dir == tmp_path / "scripts"


def test_project_structure_get_subdir(tmp_path):
    proj = ProjectStructure(tmp_path)
    assert proj.get_subdir("agents") == tmp_path / "src" / "agents"


def test_project_structure_ensure_structure(tmp_path):
    proj = ProjectStructure(tmp_path)
    proj.ensure_structure()
    assert (tmp_path / "src" / "agents").exists()
    assert (tmp_path / "src" / "functions").exists()
    assert (tmp_path / "src" / "workflows").exists()
    assert (tmp_path / "tests").exists()
    assert (tmp_path / "scripts").exists()
