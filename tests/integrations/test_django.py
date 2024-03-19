# SPDX-FileCopyrightText: 2023 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import pytest

import svcs

from tests.helpers import nop
from tests.ifaces import AnotherService, Interface, Service


try:
    from django import apps
    from django.conf import settings
    from django.core.wsgi import get_wsgi_application
    from django.http import HttpRequest, JsonResponse
    from django.test import Client as TestClient
    from django.urls import path

    import svcs.django
except ImportError:
    pytest.skip("Django not installed", allow_module_level=True)


def tl_view(request: HttpRequest) -> JsonResponse:
    svc = svcs.django.get(request, Service)
    svcs.django.get(request, float)

    assert (
        svc
        is svcs.django.get(request, Service)
        is svcs.django.svcs_from(request).get(Service)
        is svcs.django.get_abstract(request, Service)
    )
    assert (
        request.registry["svcs_registry"]
        is svcs.django.get_registry()
        is svcs.django.get_registry(request)
    )
    assert (
        request.svcs_container
        is svcs.django.svcs_from()
        is svcs.django.svcs_from(request)
    )

    return {"svc": svc}


urlpatterns = [
    path("tl", tl_view),
]


class ExampleAppConfig(svcs.django.DjangoSvcsAppConfigMixin, apps.AppConfig):
    name = "example"
    path = "."


@pytest.fixture(name="config")
def _config():
    settings.configure(
        DEBUG=True,
        ALLOWED_HOSTS=["*"],
        ROOT_URLCONF=__name__,  # Make this module the urlconf
        SECRET_KEY="noop",  # noqa: S106
        INSTALLED_APPS=["svcs.django"],
        MIDDLEWARE=[
            "django.middleware.common.CommonMiddleware",
            "svcs.django.SvcsMiddleware",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "file::memory:",
            }
        },
    )


@pytest.fixture(name="app")
def _app(config):
    app_config = ExampleAppConfig("example", "example")
    _ = get_wsgi_application()
    return app_config


@pytest.fixture(name="clean_app_ctx")
def _clean_app_ctx(
    request,
    registry: svcs.Registry,
    app: svcs.django.DjangoSvcsAppConfigMixin,
):
    app.registry = registry


# @pytest.fixture(name="container")
# def _container(clean_app_ctx):
#     return svcs.django.svcs_from()


@pytest.mark.usefixtures("clean_app_ctx")
class TestDjango:
    def test_get(self, registry: svcs.Registry, client: TestClient):
        """
        Service acquisition via svcs_get and thread locals works.
        """
        registry.register_value(Service, 42)
        registry.register_value(AnotherService, 23)

        assert {"svc": 42} == client.get("/tl").json()
