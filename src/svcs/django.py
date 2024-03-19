# SPDX-FileCopyrightText: 2023 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Callable, Protocol, overload

from django.apps import apps, AppConfig
from django.http import HttpRequest

import svcs

from ._core import (
    _KEY_CONTAINER,
    T1,
    T2,
    T3,
    T4,
    T5,
    T6,
    T7,
    T8,
    T9,
    T10,
    Container,
    Registry,
    ServicePing,
)


def svcs_from(request: HttpRequest) -> Container:
    """
    Get the current container from *request*.

    Args:
        request: The Django request object.
    """
    return getattr(request, _KEY_CONTAINER)


def get_registry(app: DjangoSvcsAppConfigMixin) -> Registry:
    """
    Get the registry from the main Django *app*.
    """
    if not app.registry:
        raise ValueError
    return app.registry


def register_factory(
    config: DjangoRegistryHaver,
    svc_type: type,
    factory: Callable,
    *,
    enter: bool = True,
    ping: Callable | None = None,
    on_registry_close: Callable | None = None,
) -> None:
    """
    Same as :meth:`svcs.Registry.register_factory()`, but uses registry on
    *app* that has been put there by :func:`init_app()`.
    """
    config.registry.register_factory(
        svc_type,
        factory,
        enter=enter,
        ping=ping,
        on_registry_close=on_registry_close,
    )


def register_value(
    config: DjangoRegistryHaver,
    svc_type: type,
    value: object,
    *,
    enter: bool = False,
    ping: Callable | None = None,
    on_registry_close: Callable | None = None,
) -> None:
    """
    Same as :meth:`svcs.Registry.register_value()`, but uses registry on *app*
    that has been put there by :func:`init_app()`.
    """
    config.registry.register_value(
        svc_type,
        value,
        enter=enter,
        ping=ping,
        on_registry_close=on_registry_close,
    )


def overwrite_factory(
    request: HttpRequest,
    svc_type: type,
    factory: Callable,
    *,
    enter: bool = True,
    ping: Callable | None = None,
    on_registry_close: Callable | None = None,
) -> None:
    """
    Obtain the currently active container on ``g`` and overwrite the factory
    for *svc_type*.

    Afterwards resets the instantiation cache on ``g``.

    See Also:
        - :meth:`svcs.Registry.register_factory()`
        - :meth:`svcs.Container.close()`
    """
    container = svcs_from(request)
    container.registry.register_factory(
        svc_type,
        factory,
        enter=enter,
        ping=ping,
        on_registry_close=on_registry_close,
    )
    container.close()


class DjangoRegistryHaver(Protocol):
    """
    An object with a :class:`pyramid.registry.Registry` as a ``registry``
    attribute. For example a :class:`~pyramid.config.Configurator` or an
    application.
    """

    registry: Registry


class DjangoSvcsAppConfigMixin(DjangoRegistryHaver):
    registry: Registry | None = None

    def ready(self) -> None:
        # ready may run more than once in some cases
        if not self.registry:
            self.registry = Registry()

    # TODO: add teardown method?


class DjangoSvcsAppConfig(DjangoSvcsAppConfigMixin, AppConfig):
    name = "svcs.django"


class SvcsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        container = svcs.Container(self._get_registry())
        setattr(request, _KEY_CONTAINER, container)
        return self.get_response(request)

    def _get_registry(self) -> Registry:
        app = apps.get_app_config(
            "django"
        )  # TODO: fix app config label for DjangoSvcsAppConfig
        if not app:
            raise ValueError(app)
        if not isinstance(app, DjangoSvcsAppConfigMixin):
            raise TypeError(app)
        return get_registry(app)


@overload
def get(request: HttpRequest, svc_type: type[T1], /) -> T1: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    /,
) -> tuple[T1, T2]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    /,
) -> tuple[T1, T2, T3]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    /,
) -> tuple[T1, T2, T3, T4]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    /,
) -> tuple[T1, T2, T3, T4, T5]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    svc_type9: type[T9],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...


@overload
def get(
    request: HttpRequest,
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    svc_type9: type[T9],
    svc_type10: type[T10],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]: ...


def get(request: HttpRequest, *svc_types: type) -> object:
    """
    Same as :meth:`svcs.Container.get()`, but uses container on :obj:`flask.g`.
    """
    return svcs_from(request).get(*svc_types)
