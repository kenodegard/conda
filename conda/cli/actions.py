# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""
Collection of custom argparse actions.
"""

from __future__ import annotations

from argparse import Action, _CountAction, _StoreAction
from typing import TYPE_CHECKING

from ..common.constants import NULL
from ..deprecations import deprecated

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence
    from typing import Any


class NullCountAction(_CountAction):
    @staticmethod
    @deprecated("26.9", "27.3")
    def _ensure_value(namespace, name, value):
        if getattr(namespace, name, NULL) in (NULL, None):
            setattr(namespace, name, value)
        return getattr(namespace, name)

    def __call__(self, parser, namespace, values, option_string=None):
        count = getattr(namespace, self.dest, NULL)
        if not isinstance(count, int):
            count = 0
        setattr(namespace, self.dest, count + 1)


class ExtendConstAction(Action):
    """
    A derivative of _AppendConstAction and Python 3.8's _ExtendAction
    """

    def __init__(
        self,
        option_strings,
        dest,
        const,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs="*",
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = [] if items is None else items[:]
        items.extend(values or [self.const])
        setattr(namespace, self.dest, items)


class lazyproperty:
    def __set_name__(self, owner, name):
        self.__name__ = name

    @property
    def __key__(self) -> str:
        return f"_{self.__name__}"

    @property
    def __factory__(self) -> str:
        return f"_{self.__name__}_factory"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return getattr(instance, self.__key__)
        except AttributeError:
            pass
        factory = getattr(instance, self.__factory__, None)
        value = factory() if factory else None
        setattr(instance, self.__key__, value)
        return value

    def __set__(self, instance, value):
        factory = getattr(instance, self.__factory__, None)
        if value is not None or not factory:
            setattr(instance, self.__key__, value)

    def __delete__(self, instance):
        delattr(instance, self.__key__)


class LazyAction(Action):
    choices: Iterable[Any] | None = lazyproperty()
    help: str | None = lazyproperty()

    @deprecated.argument(
        "26.9",
        "27.3",
        "choices_func",
        rename="choices_factory",
    )
    def __init__(
        self,
        *,  # force keyword-only arguments
        choices: Iterable[Any] | None = None,
        choices_factory: Callable[[], Sequence[Any] | None] | None = None,
        help: str | None = None,
        help_factory: Callable[[], str | None] | None = None,
        **kwargs,
    ):
        if choices and choices_factory:
            raise ValueError("choices and choices_factory are mutually exclusive")
        self._choices_factory = choices_factory

        if help and help_factory:
            raise ValueError("help and help_factory are mutually exclusive")
        self._help_factory = help_factory

        super().__init__(choices=choices, help=help, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        valid_choices = self.choices
        if values not in valid_choices:
            choices_string = ", ".join(f"'{val}'" for val in valid_choices)
            # Use the same format as argparse for consistency
            option_display = "/".join(self.option_strings)
            parser.error(
                f"argument {option_display}: invalid choice: {values!r} (choose from {choices_string})"
            )
        setattr(namespace, self.dest, values)


class _ValidatePackages(_StoreAction):
    """
    Used to validate match specs of packages
    """

    @staticmethod
    def _validate_no_denylist_channels(packages_specs):
        """
        Ensure the packages do not contain denylist_channels
        """
        from ..base.context import validate_channels
        from ..models.match_spec import MatchSpec

        if not isinstance(packages_specs, (list, tuple)):
            packages_specs = [packages_specs]

        validate_channels(
            channel
            for spec in map(MatchSpec, packages_specs)
            if (channel := spec.get_exact_value("channel"))
        )

    def __call__(self, parser, namespace, values, option_string=None):
        self._validate_no_denylist_channels(values)
        super().__call__(parser, namespace, values, option_string)
