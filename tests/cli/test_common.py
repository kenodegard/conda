# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from contextlib import nullcontext
from io import StringIO
from typing import TYPE_CHECKING

import pytest

from conda.base.context import conda_tests_ctxt_mgmt_def_pol, context, reset_context
from conda.cli.common import check_non_admin, confirm, confirm_yn, is_active_prefix
from conda.common.io import captured, env_vars
from conda.exceptions import CondaSystemExit, DryRunExit, OperationNotAllowed

if TYPE_CHECKING:
    from pytest import MonkeyPatch
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


def test_confirm_yn_yes(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("sys.stdin", StringIO("blah\ny\n"))

    with env_vars(
        {
            "CONDA_ALWAYS_YES": "false",
            "CONDA_DRY_RUN": "false",
        },
        stack_callback=conda_tests_ctxt_mgmt_def_pol,
    ), captured() as cap:
        assert not context.always_yes
        assert not context.dry_run

        assert confirm_yn()

    assert "Invalid choice" in cap.stdout


def test_confirm_yn_no(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("sys.stdin", StringIO("n\n"))

    with env_vars(
        {
            "CONDA_ALWAYS_YES": "false",
            "CONDA_DRY_RUN": "false",
        },
        stack_callback=conda_tests_ctxt_mgmt_def_pol,
    ), pytest.raises(CondaSystemExit):
        assert not context.always_yes
        assert not context.dry_run

        confirm_yn()


def test_confirm_yn_dry_run_exit():
    with env_vars(
        {"CONDA_DRY_RUN": "true"},
        stack_callback=conda_tests_ctxt_mgmt_def_pol,
    ), pytest.raises(DryRunExit):
        assert context.dry_run

        confirm_yn()


def test_confirm_dry_run_exit():
    with env_vars(
        {"CONDA_DRY_RUN": "true"},
        stack_callback=conda_tests_ctxt_mgmt_def_pol,
    ), pytest.raises(DryRunExit):
        assert context.dry_run

        confirm()


def test_confirm_yn_always_yes():
    with env_vars(
        {
            "CONDA_ALWAYS_YES": "true",
            "CONDA_DRY_RUN": "false",
        },
        stack_callback=conda_tests_ctxt_mgmt_def_pol,
    ):
        assert context.always_yes
        assert not context.dry_run

        assert confirm_yn()


@pytest.mark.parametrize("prefix,active", [("", False), ("active_prefix", True)])
def test_is_active_prefix(prefix, active):
    if prefix == "active_prefix":
        prefix = context.active_prefix
    assert is_active_prefix(prefix) is active
