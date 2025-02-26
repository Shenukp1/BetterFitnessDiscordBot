import os
import pathlib
from dotenv import load_dotenv 
import discord




load_dotenv()


BASE_DIR = pathlib.Path(__file__).parent #this is the overaching folder
CMDS_DIR = BASE_DIR / "cmds" #now we are going into cmds folder

GUILDS_ID =discord.Object(id=int(os.getenv("GUILDS")))

DISCORD_API_SECRET= os.getenv("DISCORD_API_TOKEN")

MONGODB = os.getenv("MONGODB_PASSWORD")
DB_USERNAME = os.getenv("DB_username")
DB_PASSWORD = os.getenv("DB_password")