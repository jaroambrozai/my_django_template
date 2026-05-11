# core/management/commands/mystartapp.py

import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Create a new app in apps/ directory with boilerplate"

    def add_arguments(self, parser):
        parser.add_argument("app_name", type=str, help="Name of the app")

    def handle(self, *args, **options):
        app_name = options["app_name"]
        base_dir = settings.BASE_DIR
        apps_dir = base_dir / "apps"
        app_dir = apps_dir / app_name

        # 1. vytvorit apps/ ak neexistuje
        if not apps_dir.exists():
            apps_dir.mkdir()
            self.stdout.write(self.style.SUCCESS("Created apps/"))

        # 2. skontrolovat ci app uz existuje
        if app_dir.exists():
            self.stderr.write(self.style.ERROR(f"App '{app_name}' already exists."))
            return

        # 3. vytvorit strukturu app
        app_dir.mkdir()
        (app_dir / "migrations").mkdir()
        (app_dir / "migrations" / "__init__.py").touch()

        # 4. zapisat subory
        self._write_init(app_dir)
        self._write_apps(app_dir, app_name)
        self._write_models(app_dir, app_name)
        self._write_views(app_dir, app_name)
        self._write_urls(app_dir, app_name)
        self._write_admin(app_dir, app_name)

        # 5. vytvorit templates
        self._write_templates(base_dir, app_name)

        # 6. pridať do INSTALLED_APPS
        self._add_to_installed_apps(base_dir, app_name)

        # 7. pridať do config/urls.py
        self._add_to_urls(base_dir, app_name)

        self.stdout.write(self.style.SUCCESS(f"App '{app_name}' created successfully."))

    def _write_init(self, app_dir):
        (app_dir / "__init__.py").touch()

    def _write_apps(self, app_dir, app_name):
        class_name = app_name.capitalize() + "Config"
        content = f"""from django.apps import AppConfig


class {class_name}(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.{app_name}"
    verbose_name = "{app_name.capitalize()}"
"""
        (app_dir / "apps.py").write_text(content)

    def _write_models(self, app_dir, app_name):
        class_name = app_name.capitalize()
        content = f"""from django.db import models


class {class_name}(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "{app_name.capitalize()}"
        verbose_name_plural = "{app_name.capitalize()}s"

    def __str__(self):
        return self.title
"""
        (app_dir / "models.py").write_text(content)

    def _write_views(self, app_dir, app_name):
        class_name = app_name.capitalize()
        content = f"""from django.views.generic import ListView, DetailView, TemplateView
from .models import {class_name}


class {class_name}ListView(ListView):
    model = {class_name}
    template_name = "{app_name}/{app_name}_list.html"
    context_object_name = "{app_name}_list"


class {class_name}DetailView(DetailView):
    model = {class_name}
    template_name = "{app_name}/{app_name}_detail.html"
    context_object_name = "{app_name}"


class {class_name}TemplateView(TemplateView):
    template_name = "{app_name}/{app_name}_template.html"
"""
        (app_dir / "views.py").write_text(content)

    def _write_urls(self, app_dir, app_name):
        class_name = app_name.capitalize()
        content = f"""from django.urls import path
from . import views

app_name = "{app_name}"

urlpatterns = [
    path("", views.{class_name}ListView.as_view(), name="list"),
    path("<int:pk>/", views.{class_name}DetailView.as_view(), name="detail"),
    path("info/", views.{class_name}TemplateView.as_view(), name="template"),
]
"""
        (app_dir / "urls.py").write_text(content)

    def _write_admin(self, app_dir, app_name):
        class_name = app_name.capitalize()
        content = f"""from django.contrib import admin
from .models import {class_name}


@admin.register({class_name})
class {class_name}Admin(admin.ModelAdmin):
    list_display = ["title"]
"""
        (app_dir / "admin.py").write_text(content)

    def _write_templates(self, base_dir, app_name):
        template_dir = base_dir / "templates" / app_name
        template_dir.mkdir(parents=True, exist_ok=True)

        (template_dir / f"{app_name}_list.html").write_text(
            f"{{% extends 'base.html' %}}\n\n{{% block content %}}\n<h1>{app_name.capitalize()} list</h1>\n{{% endblock %}}\n"
        )
        (template_dir / f"{app_name}_detail.html").write_text(
            f"{{% extends 'base.html' %}}\n\n{{% block content %}}\n<h1>{{{{ {app_name}.title }}}}</h1>\n{{% endblock %}}\n"
        )
        (template_dir / f"{app_name}_template.html").write_text(
            f"{{% extends 'base.html' %}}\n\n{{% block content %}}\n<h1>{app_name.capitalize()} info</h1>\n{{% endblock %}}\n"
        )

    def _add_to_installed_apps(self, base_dir, app_name):
        settings_path = base_dir / "config" / "settings" / "base.py"
        content = settings_path.read_text()
        app_string = f'"apps.{app_name}.apps.{app_name.capitalize()}Config"'

        if app_string in content:
            return

        content = content.replace(
            "    # local",
            f"    # local\n    {app_string},"
        )
        settings_path.write_text(content)

    def _add_to_urls(self, base_dir, app_name):
        urls_path = base_dir / "config" / "urls.py"
        content = urls_path.read_text()
        include_string = f'path("{app_name}/", include("apps.{app_name}.urls")),'

        if include_string in content:
            return

        content = content.replace(
            'path("admin/", admin.site.urls),',
            f'path("admin/", admin.site.urls),\n    {include_string}'
        )
        urls_path.write_text(content)