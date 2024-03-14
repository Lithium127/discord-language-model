
import os

from .client import LangClient, intents
from .generative import BaseModel
from .generative import DiscordModel

try:
    os.remove(f"{BaseModel._models_folder}/lang_bot.json")
except FileNotFoundError:
    pass

if not os.path.exists(BaseModel._models_folder):
    os.mkdir(BaseModel._models_folder)



INSTANCE = LangClient(intents=intents)

INSTANCE.model.base_training([
    "pride_and_prejudice.txt"
])

