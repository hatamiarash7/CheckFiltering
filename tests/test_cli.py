from typer.testing import CliRunner
from check_filter import cli, __app_name__, __version__

runner = CliRunner()


def test_cli_callbacks():
    result = runner.invoke(cli.app, ["-v",])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__} 💥" in result.stdout

    result = runner.invoke(cli.app, ["--version",])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__} 💥" in result.stdout


def test_cli_commands(tmp_path):
    result = runner.invoke(cli.app, ["domain", "example.com"])
    assert result.exit_code == 0
    assert "The `example.com` is free in Iran 😃" in result.stdout

    result = runner.invoke(cli.app, ["domain", "twitter.com"])
    assert result.exit_code == 0
    assert "The `twitter.com` is blocked in Iran ❌" in result.stdout

    result = runner.invoke(cli.app, ["domains", "example.com,twitter.com"])
    assert result.exit_code == 0
    assert "│ example.com │ Free       │" in result.stdout
    assert "│ twitter.com │ Blocked ❌ │" in result.stdout

    file = tmp_path / "file.txt"
    file.write_text("example.com\ntwitter.com")
    assert file.read_text() == "example.com\ntwitter.com"

    result = runner.invoke(cli.app, ["file", f"{file.absolute()}"])
    assert result.exit_code == 0
    assert "│ example.com │ Free       │" in result.stdout
    assert "│ twitter.com │ Blocked ❌ │" in result.stdout
