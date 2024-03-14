import discord
import logging

from .generative import DiscordModel

intents = discord.Intents.default()
intents.message_content = True

client: discord.Client = discord.Client(intents=intents)

logger = logging.getLogger('discord.client')

class LangClient(discord.Client):
    
    model: DiscordModel
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.model = DiscordModel()
    
    # --< Gateway >-- #
    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user}")
    
    
    # --< Messages >-- #
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author == self.user:
            return
        
        if msg.content.startswith("$generate"):
            try:
                length = int(msg.content.split(" ")[1])
                await msg.channel.send(self.model.generate(length))
                logger.info(f"Message generation invoked, len: {length}")
            except Exception as e:
                await msg.channel.send(f"Invalid arguments: $generate [int: length]\nException: {e}")
            return
        
        if msg.content.startswith("$extend"):
            try:
                cmd = msg.content.split(" ")
                del cmd[0]
                length = int(cmd.pop(0))
                await msg.channel.send(self.model.extend(" ".join(cmd), length))
            except Exception as e:
                await msg.channel.send(f"Invalid argument; $extend [int: length] [*str: context]\nException: {e}")
        
        self.model.update(msg)
        