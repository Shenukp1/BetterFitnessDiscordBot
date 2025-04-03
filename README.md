# Discord Workout Tracking Bot
Discord bot that helps user keep track and log their workouts directly from discord. Uses slash
commands for easy user interface, and MongoDB to store user workout related data.

## Functionality of the Bot
 1. Lets users create workout templates (e.g. "Push", "Leg Day", etc.)
 2. Add individual workouts under those templates (e.g. "Inclined Dumbbell Press", "Squats")
 3. Log your workout data (sets, reps, and weights)
 4. Autocomplete options when entering commands (makes it fast and easy to use)
 5. Show your past workout logs
 6. Download your logged data

## Python file Overview
### `main.py`
- Starts the bot and loads all commands in the /cmds folder
- Indicates the bot has started with a message("Hello") on a secified channel
- syncs slash commands so it shows up in the user interface

### `workout.py`
- Contains the logic for Discord commands
- Commands available:
  - /workout createow → Create overarching workout
  - /workout createiw → Add individual workouts under an OW
  - /workout logworkout → Log actual workout data
- Includes autocomplete features for user convenience

### `db.py`
- Connects to MongoDB using credentials stored securely
- Collections used:
  - overarching_workouts: for workout templates
  - workout_logs: for actual workout tracking

### `settings.py`
- Loads environment variables from a .env file(API keys, passwords, etc.)


## Setup Instructions

### Must Have:
- Python 3.10+
- MongoDB account
- .env file with these variables specified:
  DISCORD_API_TOKEN=your_discord_token_here
  DB_username=your_mongo_username
  DB_password=your_mongo_password
  MONGODB_PASSWORD=your_mongo_password
  GUILDS=your_server_id

    

 
