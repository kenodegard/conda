# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from contextlib import nullcontext
from io import StringIO
from typing import TYPE_CHECKING

import pytest

from conda.base.context import context, reset_context
from conda.cli.common import check_non_admin, confirm, confirm_yn, is_active_prefix
from conda.exceptions import CondaSystemExit, DryRunExit, OperationNotAllowed

if TYPE_CHECKING:
    from pytest import CaptureFixture, MonkeyPatch
    from pytest_mock import MockerFixture


@pytest.mark.parametrize("non_admin_enabled", [True, False])
@pytest.mark.parametrize("is_admin", [True, False])
def test_check_non_admin(
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    is_admin: bool,
    non_admin_enabled: bool,
) -> None:
    monkeypatch.setenv("CONDA_NON_ADMIN_ENABLED", str(non_admin_enabled))
    reset_context()
    assert context.non_admin_enabled is non_admin_enabled

    mocker.patch("conda.common._os.is_admin", return_value=is_admin)

    with nullcontext() if non_admin_enabled or is_admin else pytest.raises(
        OperationNotAllowed
    ):
        check_non_admin()


@pytest.mark.parametrize("always_yes", [True, False])
@pytest.mark.parametrize("dry_run", [True, False])
@pytest.mark.parametrize(
    "stdin,raises",
    [
        ("blah\ny\n", None),
        ("n\n", CondaSystemExit),
    ],
)
def test_confirm_yn(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture,
    always_yes: bool,
    dry_run: bool,
    stdin: str,
    raises: type[Exception] | None,
) -> None:
    monkeypatch.setattr("sys.stdin", StringIO(stdin))

    monkeypatch.setenv("CONDA_ALWAYS_YES", str(always_yes))
    monkeypatch.setenv("CONDA_DRY_RUN", str(dry_run))
    reset_context()
    assert context.always_yes is always_yes
    assert context.dry_run is dry_run

    # precedence: dry-run > always-yes > stdin
    if dry_run:
        raises = DryRunExit
    elif always_yes:
        raises = None

    with pytest.raises(raises) if raises else nullcontext():
        assert confirm_yn()

        # only checking output if no exception was raised
        stdout, stderr = capsys.readouterr()
        if not always_yes:
            assert "Invalid choice" in stdout
        else:
            assert not stdout
        assert not stderr


def test_confirm_dry_run_exit(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("CONDA_DRY_RUN", "true")
    reset_context()
    assert context.dry_run

    with pytest.raises(DryRunExit):
        confirm()


@pytest.mark.parametrize("prefix,active", [("", False), ("active_prefix", True)])
def test_is_active_prefix(prefix, active):
    if prefix == "active_prefix":
        prefix = context.active_prefix
    assert is_active_prefix(prefix) is active
