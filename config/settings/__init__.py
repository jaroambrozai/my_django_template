import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

env = os.getenv("DJANGO_ENV", "dev")

if env == "prod":
    from .prod import *
elif env == "dev":
    from .dev import *
else:
    raise ValueError(f"Unknown DJANGO_ENV: {env}")