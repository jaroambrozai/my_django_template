import os

env = os.getenv("DJANGO_ENV", "dev")

if env == "prod":
    from .prod import *
elif env == "dev":
    from .dev import *
else:
    raise ValueError(f"Unknown DJANGO_ENV: {env}")