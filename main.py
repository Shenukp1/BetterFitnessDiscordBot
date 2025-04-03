import setting # allows us to use the variables in settings such as directory paths or API keys
import discord 
from discord.ext import commands
import asyncio


"""
RESOURCES:
    1. Discord:https://www.youtube.com/watch?v=eLcAZIeqLu8&list=PLESMQx4LeD3N0-KKPPDaToZhBsom2E_Ju&index=3&ab_channel=RichardSchwabe
    2. Mongodb:https://www.youtube.com/watch?v=UpsZDGutpZc&ab_channel=TechWithTim

"""
#function to load all user from database


#function to compare all user from database with new users






#==================Discord Stuff==================#

# this is how the discord bot is set up and runs
def run():
    # discord required commands to make bot work
    # grabs all the intents permissions the bot uses
    intents = discord.Intents.default()     # then makes message_content true to read commands
    intents.message_content = True          # allows bot to read user messages
    intents.messages = True                 # good to have this True
    intents.guilds = True                   # good to have this True
    bot = commands.Bot(command_prefix='!', intents=intents) # prefix used for commands. so bot commands start with !

    # registering all users
    # first we need to load old users into an array
    # then we need to compare that array with the new set of user we want to add
 
    


    # this function runs when the bot connects
    @bot.event
    async def on_ready():
        print("We Are Running!")

        
        # going over all the files in cmds folder
        # then loads the commands from each file
        for cmd_file in setting.CMDS_DIR.glob("*.py"):
            if cmd_file.name != "__init__.py":                          # dont want init.py
                await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")  # :-3 is do not give last three character(.py)
        
        # get the channel to send messages to, and sends 'Hello'
        # to show that the bot is active
        starting = bot.get_channel(1137190101684850768)
        await starting.send("Hello!")                   # TODO: explain what bot does when it starts

        # prints all the loaded commands to make sure all the commands
        # were loaded correctly
        print("Loaded commands:")
        for command in bot.commands:
            print(f"- {command.name}")


        # TODO: when ready to deploy remove this code
        # this makes it so that if you are testing commands
        # the commands are only on the server the bot is in
        bot.tree.copy_global_to(guild=setting.GUILDS_ID)

        # this makes it so that the slash commands show up in the
        # user interface of discord
        # when ready to deploy remove'guild=setting.GUILDS_ID' because
        # TODO: that makes it so that the commands are synced only on the server
        # the bot is in
        await bot.tree.sync(guild=setting.GUILDS_ID)

    # starting bot when the token is passed
    bot.run(setting.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()