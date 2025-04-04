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
    """
    This is a class that groups multiple slash commands under the same
    category(e.g. workouts). The user would use "/workout name_of_command"
    to use a command that are avaliable.

    Functionality to add:
        1. TODO: list all commands and what they do


    
    """

    #================Handles Creating Workouts================#

    # @app_commands.command is a way to add better user interface, such as a description
    # about what the command does.
    # @app_commands.describe tell the user what they need to enter
    @app_commands.command(name="createow", description="create your overarching workout(OW) - e.g. Push,Back,Pull...")
    @app_commands.describe(
    ow_name="Enter the overarching workout name - e.g. Push,Back,Pull...",
    )
    async def createow(self, interaction: discord.Interaction, ow_name: str):
        """
        This function is used to preform a slash command  to create a new 
        overarching workout(OW)(e.g. Push,Pull,Back...etc.) for users

        interaction: discord object used for slash commands
        ow_name: the overarching workout name given by the user
        

        The Command: /workout createow


            Errors to consider:
                
        
        """
        
        user_id = str(interaction.user.id)  # gets the ID of the user that used the command /workout createow
        response = create_overarching_workout(user_id, ow_name) # this then call the function to create the OW in the database

        await interaction.response.send_message(response) # returns a response to the user based on what the  create_overarching_workout returned




    @app_commands.command(name="createiw", description="create your Individual workout for OW - for Push(OW) e.g. Inclined dumbel press")
    @app_commands.describe(
    ow_name="Enter the Individual workout name",
    )
    async def createiw(self, interaction: discord.Interaction,ow_name: str, iw_name: str, rest_timer:str,sets:str,reps:str):
        """
        This function is used to preform a slash command  to create a new 
        individual workout(IW)(e.g. Inclined Dumbell Press, Cable Rows, Leg Press...etc.)
        Within the OW(e.g. Push,Pull..)that the user specified. This is to create a template
        to log the workouts later.

        interaction: discord object used for slash commands
        ow_name: the overarching workout name given by the user but also autocompleted
        iw_name: name of the individual workout(IW)
        rest_timer: the time they took to rest between sets
        sets: the number of sets they have for the IW
        reps: the number of reps they do per set

        The Command: /workout createiw

        
        """
        # grabs the user_id and the calls the function with the correct params
        user_id = str(interaction.user.id)
        response = add_individual_workout(user_id, ow_name, iw_name, rest_timer, sets, reps)

        await interaction.response.send_message(f"{response}")
    


    # @createiw.autocomplete allows for autocompletion of the specified param and function
    # as you can see it follows @functionName.autcomplete('varNameWithinFun').
    # in this case it would be any ow_name param
    @createiw.autocomplete("ow_name")# you put in the name of what var you want to autocomplete
    async def ow_autocomplete(self,interaction: discord.Interaction, current: str):
        """
        This function allows autocomplete when the user is typing for the string 
        ow_name in "/workout createiw"

        interaction: discord object used for slash commands
        current: give us what the user is typing
        
        """

        # based on the user_id we are going to call get_overarching_workouts func
        # that gets all the overarching workouts under the user in the database
        user_id = str(interaction.user.id)
        workouts = get_overarching_workouts(user_id)

        
        choices = [] # creating a list to hold the Choice objects
        # we are then going to check if what input the user is writing 
        # is within the OW they created.
        for workout in workouts:
            if current.lower() in workout.lower():# if pu(what the user wrote or is typing) in push(whats in the database)

                # Choice is a discord object. 
                # name: the dropdown text that is shown(e.g., Push)
                # value: this is the value that get pass to the command that is uses autocomplete
                # so ow_name will get passed that value(e.g., Push) that the user click on when the dropdown is shown
                choice = app_commands.Choice(name=workout, value=workout)
                choices.append(choice)  # this allows for the user to be displayed all the OW they created
        
        return choices



    #================Handles Logging Workouts================#    


    @app_commands.command(name="logworkout", description="Log your workout with multiple sets")
    @app_commands.describe(
    ow_name="Enter the overarching workout name",
    iw_name="Enter the individual workout name",
    sets="Enter sets in the format [(reps, weight), (reps, weight)]"
    )
    async def logworkout(self, interaction: discord.Interaction, ow_name: str, iw_name: str, sets: str):

        """
        This function logs the workout for the for the workouts templates that
        are already created.

        interaction: discord object used for slash commands
        ow_name: name of the overarching workout 


        Functionality to Consider:
            1. TODO: what if they want to enter there sets one at a time. but we want to make 
                     sure that it is added under the same OW, IW. might have to look at log workout




        
        """

        user_id = str(interaction.user.id)
        response = log_workout(user_id, ow_name, iw_name, sets)
        await interaction.response.send_message(response)


    
    @logworkout.autocomplete("ow_name")
    async def ow_autocomplete(self,interaction: discord.Interaction, current: str):

        """
        function that allows for autocompletion for OW logging
        
        """

        user_id = str(interaction.user.id)
        workouts = get_overarching_workouts(user_id)
        choices = []
        for workout in workouts:
            if current.lower() in workout.lower():
                choice = app_commands.Choice(name=workout, value=workout)
                choices.append(choice)

        return choices
        
        
    @logworkout.autocomplete("iw_name")
    async def iw_autocomplete(self,interaction: discord.Interaction, current: str):

        """
        function that allows autocompletion based on the selected OW in logworkout
        """

        user_id = str(interaction.user.id)
        
        selected_ow = interaction.namespace.ow_name  # this gets the the input that is put in for OW using interaction.namespace

        choices = []

        # this make it so that if there is no OW selected, then it will
        # show no dropdown option for IW
        if not selected_ow:
            return choices

        workouts = get_individual_workouts(user_id, selected_ow)
        choices = []
        for workout in workouts:
            if current.lower() in workout.lower():
                choice = app_commands.Choice(name=workout, value=workout)
                choices.append(choice)

        return choices
    
    #================Shows Workouts================#

    # TODO Implementation for show workouts required
   
    @app_commands.command(name="showorkout", description="shows your past 3 workouts for individual workouts")
    @app_commands.describe(
    ow_name="Enter the overarching workout name",
    iw_name="Enter the individual workout name",
    sets="Enter sets in the format [(reps, weight), (reps, weight)]"
    )
    async def logworkout(self, interaction: discord.Interaction, ow_name: str, iw_name: str, sets: str):
        user_id = str(interaction.user.id)
        response = get_log_workout(user_id, ow_name, iw_name, sets)# TODO: implement function
        await interaction.response.send_message(response)




async def setup(bot):
    """
    This function is responsible for regisetering all the workout commands under
    the workout class function. such that all the subcommands(e.g. createow, createiw,...)
    appear under "/workout subCommandsHere".
    
    """
    bot.tree.add_command(Workout(name="workout",description="Workout Commands"))