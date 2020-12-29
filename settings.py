from envparse import env

API_TOKEN = env.str("API_TOKEN", default="")
ADMIN_CHAT_ID = env.str("ADMIN_CHAT_ID", default="")
WEBHOOK_HOST = env.str("WEBHOOK_HOST", default="https://your.domain")
WEBHOOK_PATH = env.str("WEBHOOK_PATH", default="/path/to/api")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

POSTGRES_HOST = env.str("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = env.int("POSTGRES_PORT", default=5432)
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD", default="post_bot")
POSTGRES_USER = env.str("POSTGRES_USER", default="post_bot")
POSTGRES_DB = env.str("POSTGRES_DB", default="post_bot")
POSTGRES_URI = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}