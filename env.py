import os
from alembic import context
from sqlalchemy import engine_from_config, pool

# This line fetches the DATABASE_URL from the environment and sets it in the config
config = context.config
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
