import discord
from discord.ext import commands
from discord import app_commands
from db import users_collection
from db import ow_collection
from db import log_collection
from datetime import datetime
import ast  #safe parsing
"""
In this file, the functionality of discord commands are made. such as the discord command 
to make a create an overaching workout(e.g. Push), and sub workouts within that overarching
workout(e.g. Incline Chest Press).

This file also creates functionality of logging a workout using discord commands.Once they are 
logged, they are saved on MongoDB(database)



In this file all the workout Inputs and Outputs are handled. 
    Inputs:
        1. creating a workout (e.g. Commands: createow )
        2. starting a workout (e.g. Commands: logworkout )
        3. downloading file to input into database
    
    Outputs:
        
NOTES:
    1. user_id = interaction.user.id  # Get the user's ID
    2. user_name = interaction.user.name  # Get the user's name (optional)
    2.  ephemeral=True - makes it so that you can only see the message. for example: 
        await interaction.response.send_message(f"{text_to_send}", ephemeral=True)

TODO
    1.TODO: let the user see there past x(gotta figure out how far back we
            we can save) workouts for there Overarching workout 
    2.TODO: downloading there previous x workouts before its deleted


HOW THE DB ORGANIZES EVERYTHING
    1. The creates their own Overarching workout(OW) template. Overarching Workouts can be named anything
        but for example an OW can be 'push'. 
    2. then within the OW 'push', there can be individual workout(IW) such as, 'inclined dumble press',
        'chest flies', so on..
    3 then within those IW, the user adds present rest timer, sets, reps

    4. Then the user can on discord do /workouts autocomplete_the_work_they_made autocomplete_the_IW enter_set_# enter_rep_# enter_weight_#

    5. then when the do 4. , this saves the infromation they inputted in a orangized manner in the database. so multiple occurance of "push" can be
        in the database

HOW DOWNLOADING AND UPLOADING WILL WORK
    1. 

"""








def create_overarching_workout(user_id, ow_name):

    """
    This function adds a new overarching workout(OW)(e.g. Push,Pull,Back...etc.)
    to the database.

    This function creates a template that serves as a blueprint for logging workouts. 
    However, it does not directly log a workout into the collection. Instead, it sets up 
    placeholders that are used later when the actual workout logging function is called.


    user_id: identifies the user to the OW that they want to create
    ow_name: name of the ow that they want to create



    """
    
    # checking if the overarching workout already exist within the database
    # if it does, gives a string for the discord bot to display to user
    # that it already exist under that user
    existing_workout = ow_collection.find({"user_id":user_id,"name":ow_name})
    if existing_workout:
        return f"Workout '{ow_name}' already exists."
    
    
    # If the workout doesnt exist, we are going to create that workout 
    # within the database and then link that workout to the discord
    # user through user_id and then give the overarching workout
    # a name based on what the user put in
    ow_data = {
        "user_id": user_id,
        "name": ow_name,
        "individual_workouts": []
    }
    # this is the 'link' to the database where ALL the overarching workouts 
    # are created
    ow_collection.insert_one(ow_data)
    return f"Workout '{ow_name}' has been created."




#this is to add an indivdiual workout to the OW
def add_individual_workout(user_id, ow_name, iw_name, rest_timer, sets, reps):

    """
    This function adds an individual workout(IW)(e.g. Inclined Chest Press) to 
    an existing OW(e.g. Push).

    This function creates a template that serves as a blueprint for logging workouts. 
    However, it does not directly log a workout into the collection. Instead, it sets up 
    placeholders that are used later when the actual workout logging function is called.

    The user can add as many individual workouts they want to an OW.

    user_id: identifies the user to the IW that they want to create
    ow_name: tell the database which OW the IW will be under
    iw_name: name of the individual workout(IW)
    rest_timer: the time they took to rest between sets
    sets: the number of sets they have for the IW
    reps: the number of reps they do per set


    
    """
    
    # checks if the individual workout exist already.
    # $elemMatch is used to find an exact match of the name only
    # as in, you can only create one individual workout with the same name
    # you cannot have multiple IW with the same name but 
    # different preset_rest_timer sets, reps
    existing_workout = ow_collection.find_one({
        "user_id": user_id,
        "name": ow_name,
        "individual_workouts": {
            "$elemMatch": {
                "name": iw_name
            }
        }
    })
    

    # if the workout exist, the discord command will recieve an string
    # to let the user know it already exists
    if existing_workout:
        return f"Workout '{iw_name}' already exists."
    

    # if it doesnt exist, we are going to create a IW
    # with the users specified rest_timer, sets, and reps
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




def log_workout(user_id, ow_name, iw_name, sets):

    """
    
    """
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




#need this function for autocomplete for overarching workouts for the user of the bot only
def get_overarching_workouts(user_id):
    workouts = ow_collection.find({"user_id": user_id}, {"_id": 0, "name": 1})
    return [workout["name"] for workout in workouts]




#need this function for auto complete for individual workouts based on selected OW
def get_individual_workouts(user_id, ow_name):
    ow = ow_collection.find_one({"user_id": user_id, "name": ow_name}, {"_id": 0, "individual_workouts": 1})
    if ow and "individual_workouts" in ow:
        return [iw["name"] for iw in ow["individual_workouts"]]
    return []


    #================DISCORD COMMANDS BELOW================#


#TODO:make it so i can only see the slash commands
class Workout(app_commands.Group):

    

    #================Handles Creating Workouts================#

    #Slash that allows user to create a overarching workouts(OW)
    @app_commands.command(name="createow", description="create your overarching workout(OW) - e.g. Push,Back,Pull...")
    @app_commands.describe(
    ow_name="Enter the overarching workout name",
    )
    async def createow(self, interaction: discord.Interaction, ow_name: str):
        """
        This function creates a new overarching workout(OW)(e.g. Push,Pull,Back...etc.) for users of the bot
            Errors to consider:
                
        
        """
        user_id = str(interaction.user.id)#this get the user that did the commands id
        response = create_overarching_workout(user_id, ow_name)

        await interaction.response.send_message(response)




    #Slash that allows user to create a individual workouts within OW
    @app_commands.command(name="createiw", description="create your Individual workout for OW - for Push(OW) e.g. Inclined dumbel press")
    @app_commands.describe(
    ow_name="Enter the Individual workout name",
    )
    async def createiw(self, interaction: discord.Interaction,ow_name: str, iw_name: str, rest_timer:str,sets:str,reps:str):

        user_id = str(interaction.user.id)#this get the user that did the commands id
        add_individual_workout(user_id, ow_name, iw_name, rest_timer, sets, reps)

        await interaction.response.send_message(f"You have created: {ow_name}")
    


    
    #this allows for autocompletion for OW in createiw
    @createiw.autocomplete("ow_name")#you put in the name of what var you want to autocomplete
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


    #this allows for autocompletion for OW logging
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
    
    #================Shows Workouts================#

    #showing IW for the past month 
    #Slash that allows user to Log OW
    @app_commands.command(name="showorkout", description="show your workout")
    @app_commands.describe(
    ow_name="Enter the overarching workout name",
    iw_name="Enter the individual workout name",
    sets="Enter sets in the format [(reps, weight), (reps, weight)]"
    )
    async def logworkout(self, interaction: discord.Interaction, ow_name: str, iw_name: str, sets: str):
        user_id = str(interaction.user.id)
        response = log_workout(user_id, ow_name, iw_name, sets)
        await interaction.response.send_message(response)




async def setup(bot):
    #name= name of the all the commands when you do /
    #description is text about the commands that show
    bot.tree.add_command(Workout(name="workout",description="Workout Commands"))