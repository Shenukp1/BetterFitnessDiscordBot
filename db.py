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


# Encode them to be URL-safe
encoded_username = urllib.parse.quote_plus(setting.DB_USERNAME)
encoded_password = urllib.parse.quote_plus(setting.DB_PASSWORD)

# Construct the correct MongoDB connection string
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@discordbot.met5y.mongodb.net/?retryWrites=true&w=majority&appName=Discordbot"

# Creating a client instance
client = MongoClient(MONGO_URI)

# The database we want to use
db = client["bot"]

#Selecting the Users collection
users_collection = db["Users"]
workouts_collection = db["Users"]

ow_collection = db["overarching_workouts"]
log_collection = db["workout_logs"]
#can add more collections as needed