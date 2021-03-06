import pytest
from _pytest.main import ExitCode

from schemathesis.cli import reset_targets


@pytest.fixture()
def new_target(testdir, cli):
    module = testdir.make_importable_pyfile(
        hook="""
            import schemathesis
            import click

            @schemathesis.register_target
            def new_target(context) -> float:
                click.echo("NEW TARGET IS CALLED")
                return float(len(context.response.content))
            """
    )
    yield module
    reset_targets()
    # To verify that "new_target" is unregistered
    result = cli.run("--help")
    lines = result.stdout.splitlines()
    assert "  -t, --target [response_time|all]" in lines


@pytest.mark.usefixtures("new_target")
@pytest.mark.endpoints("success")
def test_custom_target(testdir, cli, new_target, openapi3_schema_url):
    # When `--pre-run` hook is passed to the CLI call
    # And it contains registering a new target
    result = cli.main("--pre-run", new_target.purebasename, "run", "-t", "new_target", openapi3_schema_url)
    # Then the test run should be successful
    assert result.exit_code == ExitCode.OK, result.stdout
    # And the specified target is called
    assert "NEW TARGET IS CALLED" in result.stdout
