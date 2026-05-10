# core/management/commands/check_env.py

import os
from django.core.management.base import BaseCommand


REQUIRED_ENV_VARS = [
    "SECRET_KEY",
    "DJANGO_ENV",
]

PROD_ENV_VARS = [
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "EMAIL_HOST",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
]


class Command(BaseCommand):
    help = "Check that all required environment variables are set"

    def handle(self, *args, **options):
        env = os.getenv("DJANGO_ENV", "dev")
        missing = []

        vars_to_check = REQUIRED_ENV_VARS
        if env == "prod":
            vars_to_check = REQUIRED_ENV_VARS + PROD_ENV_VARS

        for var in vars_to_check:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            self.stderr.write(self.style.ERROR("Missing environment variables:"))
            for var in missing:
                self.stderr.write(self.style.ERROR(f"  - {var}"))
        else:
            self.stdout.write(self.style.SUCCESS("All required environment variables are set."))