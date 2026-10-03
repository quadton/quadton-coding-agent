from pathlib import Path

from agent.core.tools.default import create_default_registry


def test_default_registry_contains_expected_tools(tmp_path: Path):
    registry = create_default_registry(tmp_path)

    expected_tools = [
        "list_directory",
        "read_file",
        "search_files",
        "write_file",
        "edit_file",
        "execute_command",
    ]

    registered_tools = [
        tool.name
        for tool in registry.all()
    ]

    assert registered_tools == expected_tools


def test_default_registry_returns_project_root(tmp_path: Path):
    registry = create_default_registry(tmp_path)

    execute_tool = registry.get("execute_command")

    assert execute_tool is not None
    assert execute_tool.context.project_root == tmp_path


def test_default_registry_execute_command(tmp_path: Path):
    registry = create_default_registry(tmp_path)

    result = registry.execute(
        "execute_command",
        {
            "command": "printf 'hello'",
        },
    )

    assert result["success"] is True
    assert result["stdout"] == "hello"
    assert result["stderr"] == ""
    assert result["exit_code"] == 0
