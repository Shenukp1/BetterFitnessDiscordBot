from pymongo import MongoClient
import urllib.parse
import setting
"""
In this file, all mongodb code is done. the codes purpose is to give other files access to collection.






NOTES:

    What Do 1 and 0 Do?

        Ex. users_collection.find({}, {"_id": 0, "name": 1})

        1 (Include the field) → "name": 1 means only retrieve the name field.
        0 (Exclude the field) → "_id": 0 means do not retrieve the _id field (MongoDB includes it by default).

    Each discord person on the server needs to register with the bot, aka the database to use it. that username will be
    unique to them so they can only access there data -> I think i can use ctx.author.id

"""


# this makes it so no one can see passwords
encoded_username = urllib.parse.quote_plus(setting.DB_USERNAME)
encoded_password = urllib.parse.quote_plus(setting.DB_PASSWORD)

# Construct the correct MongoDB connection string to get access to the mongodb
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@discordbot.met5y.mongodb.net/?retryWrites=true&w=majority&appName=Discordbot"

# creating a client instance so we can access the databases
client = MongoClient(MONGO_URI)

# getting the database we want to use
db = client["bot"]

# TODO: remove because they might not be important
users_collection = db["Users"]
workouts_collection = db["Users"]

# the purpose of the overarching workouts database is to
# only allow the user to remember the workouts they have
# created and then to easily log workouts
ow_collection = db["overarching_workouts"]

# the purpose of this collection is to log the workouts
# as in keep track of the weights, sets, reps a user did for
# individual workouts(e.g. Inclined dumbell press) within the
# overarching workout(e.g. Push)
log_collection = db["workout_logs"]


# can add more collections as needed