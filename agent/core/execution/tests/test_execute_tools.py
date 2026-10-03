from agent.core.tools.execute_tools import execute_command


def test_execute_command_success():
    result = execute_command("printf 'hello'")

    assert result["success"] is True
    assert result["stdout"] == "hello"
    assert result["stderr"] == ""
    assert result["exit_code"] == 0
    assert result["timed_out"] is False


def test_execute_command_failure():
    result = execute_command("sh -c 'exit 3'")

    assert result["success"] is False
    assert result["exit_code"] == 3


def test_execute_command_timeout():
    result = execute_command("sleep 2", timeout=1)

    assert result["success"] is False
    assert result["timed_out"] is True
