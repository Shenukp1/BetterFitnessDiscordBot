import setting #allows us to use the variables in settings
import discord
from discord.ext import commands
import asyncio
from db import users_collection

"""
RESOURCES:
    1. Discord:https://www.youtube.com/watch?v=eLcAZIeqLu8&list=PLESMQx4LeD3N0-KKPPDaToZhBsom2E_Ju&index=3&ab_channel=RichardSchwabe
    2. Mongodb:https://www.youtube.com/watch?v=UpsZDGutpZc&ab_channel=TechWithTim

"""
#function to load all user from database


#function to compare all user from database with new users






#==================Discord Stuff==================#

#initalizes the bot
def run():
    #discord required commands to make bot work
    intents = discord.Intents.default()
    intents.message_content = True #THIS IS A MUST, allows bot to read user messages
    intents.messages = True
    intents.guilds = True
    bot = commands.Bot(command_prefix='!', intents=intents)#prefix used for commands

    #registering all users
    #first we need to load old users into an array
    #then we need to compare that array with the new set of user we want to add
    """
    Example of how to inset into db:
        users = [
        {"name": "Alice", "email": "alice@example.com", "age": 30},
        {"name": "Bob", "email": "bob@example.com", "age": 28},
        {"name": "Charlie", "email": "charlie@example.com", "age": 22}
        ]

        result = users_collection.insert_many(users)
        print(f"Inserted user IDs: {result.inserted_ids}")


    Thinking:
        users = [
        {"User_id": "Discord_id", "Push(OW)": "link_to_push_collection", "age": 30},
        {"name": "Bob", "email": "bob@example.com", "age": 28},
        {"name": "Charlie", "email": "charlie@example.com", "age": 22}
        ]
    """
    



    @bot.event
    async def on_ready():
        print("We Are Running!")

        
        #going over all the files in cmds folder
        for cmd_file in setting.CMDS_DIR.glob("*.py"):
            if cmd_file.name != "__init__.py": #dont want init.py
                await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")#:-3 is do not give last three character(.py)
        
        starting = bot.get_channel(1137190101684850768)
        await starting.send("Hello!")

        print("Loaded commands:", [command.name for command in bot.commands])# shows the loaded commands - a check
        bot.tree.copy_global_to(guild=setting.GUILDS_ID)
        await bot.tree.sync(guild=setting.GUILDS_ID)#need this for tree stuff
    #starting bot
    bot.run(setting.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()