
import os

from app import INSTANCE

CLIENT_TOKEN = os.environ.get("LANG_BOT_DISCORD_TOKEN", None)

INSTANCE.run(
    token = CLIENT_TOKEN
)