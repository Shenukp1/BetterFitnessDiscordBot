import discord
from discord.ext import commands
from discord import app_commands
from db import users_collection
from db import ow_collection
from db import log_collection
from datetime import datetime
import ast  #safe parsing
"""
In this file, I want to collect all the workouts a user does. I will allow them
to catogorize their workouts such that they will have a overarching name(e.g. Push, Shoulder, Back,...etc), and then
the individual names(e.g. Inclined Chest Press, Shoulder Press,...etc) of the workout. 
    1.User can create an overarching workout.
    2.User must add to that overarching workout, individual works with predetermined
      sets, reps, and rest they want to meet. this is basically creating a template to input
      easily.
        2.2 Input -> Individual Workout Name:  Sets:  Reps:  RestTime:
        

what will always stay constant is set and time of rest after the user enter the individual workout.
for each set the user will record the reps, weight. (additional Idea) before the next set, a time for
the rest will start.

there will be a feature where once they made multiple individual workouts within the overaching workout(OW),they can start it. once they start OW, they will go through all the individual
workouts within the OW and input the reps, and weight before the next set. before every set, a timer will go off, 
which is the rest timer, and after it finishes, the user will be prompted to tell the reps and weight for the next set. 

the user can edit these workouts aswell.


NOTES:
    1. user_id = interaction.user.id  # Get the user's ID
    2. user_name = interaction.user.name  # Get the user's name (optional)

HOW THE DB ORGANIZES EVERYTHING
    
    1. The creates their own Overarching workout(OW) template. Overarching Workouts can be named anything
        but for example an OW can be 'push'. 
    2. then within the OW 'push', there can be individual workout(IW) such as, 'inclined dumble press',
        'chest flies', so on..
    3 then within those IW, the user adds present rest timer, sets, reps

    4. Then the user can on discord do /workouts autocomplete_the_work_they_made autocomplete_the_IW enter_set_# enter_rep_# enter_weight_#

    5. then when the do 4. , this saves the infromation they inputted in a orangized manner in the database. so multiple occurance of "push" can be
        in the database
"""







#this is to create the overaching workout
def create_overarching_workout(user_id, ow_name):
    ow_data = {
        "user_id": user_id,
        "name": ow_name,
        "individual_workouts": []
    }
    result = ow_collection.insert_one(ow_data)
    return result.inserted_id

#this is to add an indivdiual workout to the OW
def add_individual_workout(user_id, ow_name, iw_name, rest_timer, sets, reps):
    ow_collection.update_one(
        {"user_id": user_id, "name": ow_name},
        {"$push": {
            "individual_workouts": {
                "name": iw_name,
                "preset_rest_timer": rest_timer,
                "sets": sets,
                "reps": reps
            }
        }}
    )



#this allows a user to log there workout
def log_workout(user_id, ow_name, iw_name, sets):
    try:
        sets_list = ast.literal_eval(sets)  # Safe parsing of string input

        if not isinstance(sets_list, list) or not all(isinstance(i, tuple) and len(i) == 2 for i in sets_list):
            return "Invalid format! Use [(reps, weight), (reps, weight)]"

        log_entry = {
            "user_id": str(user_id),
            "overarching_workout": ow_name,
            "individual_workout": iw_name,
            "sets": [{"set_number": i+1, "reps": reps, "weight": weight} for i, (reps, weight) in enumerate(sets_list)],
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
        log_collection.insert_one(log_entry)
        return f"Workout {iw_name} logged successfully!"
    except (SyntaxError, ValueError):
        return "Invalid format! Use [(reps, weight), (reps, weight)]"




#need this function for autocomplete for overarching workouts
def get_overarching_workouts(user_id):
    workouts = ow_collection.find({"user_id": user_id}, {"_id": 0, "name": 1})
    return [workout["name"] for workout in workouts]




#need this function for auto complete for individual workouts based on selected OW
def get_individual_workouts(user_id, ow_name):
    ow = ow_collection.find_one({"user_id": user_id, "name": ow_name}, {"_id": 0, "individual_workouts": 1})
    if ow and "individual_workouts" in ow:
        return [iw["name"] for iw in ow["individual_workouts"]]
    return []



#TODO:make it so i can only see the slash commands
class Workout(app_commands.Group):


    

    #Creating an overarching workout category
    @app_commands.command()
    async def say(self, interaction: discord.Interaction, text_to_send:str, reps:str):
        #ephemeral = True means only you can see the message
        await interaction.response.send_message(f"{text_to_send}", ephemeral=True)
    #================Handles Creating Workouts================#

    #Slash that allows user to create a overarching workouts(OW)
    @app_commands.command(name="createow", description="create your overarching workout(OW) - e.g. Push,Back,Pull...")
    @app_commands.describe(
    ow_name="Enter the overarching workout name",
    )
    async def createow(self, interaction: discord.Interaction, ow_name: str):

        user_id = str(interaction.user.id)#this get the user that did the commands id
        create_overarching_workout(user_id, ow_name)

        await interaction.response.send_message(f"You have created: {ow_name}")




    #Slash that allows user to create a individual workouts within OW
    @app_commands.command(name="createiw", description="create your Individual workout for OW - for Push(OW) e.g. Inclined dumbel press")
    @app_commands.describe(
    ow_name="Enter the Individual workout name",
    )
    async def createiw(self, interaction: discord.Interaction,ow_name: str, iw_name: str, rest_timer:str,sets:str,reps:str):

        user_id = str(interaction.user.id)#this get the user that did the commands id
        add_individual_workout(user_id, ow_name, iw_name, rest_timer, sets, reps)

        await interaction.response.send_message(f"You have created: {ow_name}")
    
    #this allows for autocompletion for OW
    @createiw.autocomplete("ow_name")
    async def ow_autocomplete(self,interaction: discord.Interaction, current: str):
        user_id = str(interaction.user.id)
        workouts = get_overarching_workouts(user_id)
        return [
            app_commands.Choice(name=workout, value=workout)
            for workout in workouts if current.lower() in workout.lower()
        ]


    #================Handles Logging Workouts================#    

    #Slash that allows user to Log OW
    @app_commands.command(name="logworkout", description="Log your workout with multiple sets")
    @app_commands.describe(
    ow_name="Enter the overarching workout name",
    iw_name="Enter the individual workout name",
    sets="Enter sets in the format [(reps, weight), (reps, weight)]"
    )
    async def logworkout(self, interaction: discord.Interaction, ow_name: str, iw_name: str, sets: str):
        user_id = str(interaction.user.id)
        response = log_workout(user_id, ow_name, iw_name, sets)
        await interaction.response.send_message(response)


    #this allows for autocompletion for OW
    @logworkout.autocomplete("ow_name")
    async def ow_autocomplete(self,interaction: discord.Interaction, current: str):
        user_id = str(interaction.user.id)
        workouts = get_overarching_workouts(user_id)
        return [
            app_commands.Choice(name=workout, value=workout)
            for workout in workouts if current.lower() in workout.lower()
        ]

    #autocompletion is done based on the selected OW
    @logworkout.autocomplete("iw_name")
    async def iw_autocomplete(self,interaction: discord.Interaction, current: str):
        user_id = str(interaction.user.id)

        #Extract the previously selected OW from interaction.namespace
        selected_ow = interaction.namespace.ow_name  

        if not selected_ow:
            return []

        workouts = get_individual_workouts(user_id, selected_ow)
        return [
            app_commands.Choice(name=workout, value=workout)
            for workout in workouts if current.lower() in workout.lower()
        ]





async def setup(bot):
    #name= name of the all the commands when you do /
    #description is text about the commands that show
    bot.tree.add_command(Workout(name="workout",description="Workout Commands"))