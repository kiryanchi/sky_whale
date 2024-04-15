import asyncio
import os

from dotenv import load_dotenv

from sky_whale.extended_bot import ExtendedBot

load_dotenv()
bot = ExtendedBot()

if __name__ == "__main__":
    asyncio.run(bot.start(token=os.environ.get("DISCORD_BOT_TOKEN")))
