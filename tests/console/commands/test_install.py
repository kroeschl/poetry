from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from cleo.testers.command_tester import CommandTester
    from pytest_mock import MockerFixture

    from poetry.poetry import Poetry
    from tests.types import CommandTesterFactory
    from tests.types import ProjectFactory


PYPROJECT_CONTENT = """\
[tool.poetry]
name = "simple-project"
version = "1.2.3"
description = "Some description."
authors = [
    "Python Poetry <tests@python-poetry.org>"
]
license = "MIT"
readme = "README.rst"

[tool.poetry.dependencies]
python = "~2.7 || ^3.4"
fizz = { version = "^1.0", optional = true }
buzz = { version = "^2.0", optional = true }

[tool.poetry.extras]
extras_a = [ "fizz" ]
extras_b = [ "buzz" ]
"""


@pytest.fixture
def poetry(project_factory: ProjectFactory) -> Poetry:
    return project_factory(name="export", pyproject_content=PYPROJECT_CONTENT)


@pytest.fixture
def tester(
    command_tester_factory: CommandTesterFactory, poetry: Poetry
) -> CommandTester:
    return command_tester_factory("install")


def test_no_all_extras_doesnt_populate_installer(
    tester: CommandTester, mocker: MockerFixture
):
    """
    Not passing --all-extras means the installer doesn't see any extras.
    """
    mocker.patch.object(tester._command.installer, "run", return_value=1)

    tester.execute()

    assert not tester._command.installer._extras


def test_all_extras_populates_installer(tester: CommandTester, mocker: MockerFixture):
    """
    The --all-extras option results in extras passed to the installer.
    """
    mocker.patch.object(tester._command.installer, "run", return_value=1)

    tester.execute("--all-extras")

    assert tester._command.installer._extras == ["extras_a", "extras_b"]


def test_extras_conlicts_all_extras(tester: CommandTester, mocker: MockerFixture):
    """
    The --extras doesn't make sense with --all-extras.
    """
    mocker.patch.object(tester._command.installer, "run", return_value=0)

    tester.execute("--extras foo --all-extras")

    assert tester.status_code == 1
    assert (
        tester.io.fetch_error()
        == "You cannot specify explicit `--extras` while installing using"
        " `--all-extras`.\n"
    )
