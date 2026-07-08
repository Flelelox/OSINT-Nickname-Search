from __future__ import annotations

import importlib
import inspect
import pkgutil

import plugins

from plugins.base import BasePlugin
from core.logger import get_logger

log = get_logger("PLUGINS")


def load_plugins() -> list[BasePlugin]:

    loaded_plugins: list[BasePlugin] = []

    for _, module_name, _ in pkgutil.iter_modules(
        plugins.__path__
    ):

        if module_name in (
            "__init__",
            "base",
            "loader",
            "existence",
        ):
            continue

        try:

            module = importlib.import_module(
                f"plugins.{module_name}"
            )

        except Exception as e:

            log.error(
                f"Cannot load plugin '{module_name}': {e}"
            )

            continue

        for _, obj in inspect.getmembers(
            module,
            inspect.isclass
        ):

            if (
                issubclass(obj, BasePlugin)
                and obj is not BasePlugin
                # только классы, объявленные В ЭТОМ модуле,
                # чтобы не инстанцировать импортированные базы
                # (BasePlugin, ExistencePlugin)
                and obj.__module__ == module.__name__
                # пропускаем внутренние базовые классы (_Blocking и т.п.)
                and not obj.__name__.startswith("_")
            ):

                try:

                    loaded_plugins.append(obj())

                except Exception as e:

                    log.error(
                        f"Cannot initialize '{module_name}': {e}"
                    )

    return loaded_plugins