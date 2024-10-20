import os
import telebot
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the bot token from the environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Check if the token is loaded correctly
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided. Please check your .env file.")

# Print the token for debugging (optional)
print(f"BOT_TOKEN: {BOT_TOKEN}")

# Create a bot instance using the token
bot = telebot.TeleBot(BOT_TOKEN)

# Define a dictionary to track user states
user_states = {}

# Define message handlers
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing? Please upload a document.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # Get the file_id of the document
    file_id = message.document.file_id

    # Fetch file information
    file_info = bot.get_file(file_id)

    # Download the file from Telegram's servers
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the file locally with the original file name
    file_name = message.document.file_name
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Notify the user that the file has been saved
    bot.reply_to(message, f"Document '{file_name}' has been saved locally.")

    # Ask for options
    user_states[message.from_user.id] = {
        'file_name': file_name,
        'stage': 'options'
    }
    ask_options(message.from_user.id)

def ask_options(user_id):
    # Ask the user for options
    bot.send_message(user_id, "Please choose the options:\n"
                              "1. Number of copies (e.g., 1, 2, 3)\n"
                              "2. Color: black or white\n"
                              "3. Orientation: landscape or portrait\n"
                              "4. Quality: 50%, 75%, or 100%")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id]['stage'] == 'options')
def handle_options(message):
    # Get the user's response
    response = message.text

    # Split the response into individual options
    options = response.split(',')

    # Validate and store options
    try:
        num_copies = int(options[0].strip())
        color = options[1].strip().lower()
        orientation = options[2].strip().lower()
        quality = int(options[3].strip())

        # Validate the options
        if color not in ['black', 'white']:
            raise ValueError("Color must be 'black' or 'white'")
        if orientation not in ['landscape', 'portrait']:
            raise ValueError("Orientation must be 'landscape' or 'portrait'")
        if quality not in [50, 75, 100]:
            raise ValueError("Quality must be 50, 75, or 100")

        # Proceed with the specified options (you can add further processing here)
        bot.reply_to(message, f"Options received:\n"
                              f"Number of copies: {num_copies}\n"
                              f"Color: {color}\n"
                              f"Orientation: {orientation}\n"
                              f"Quality: {quality}%\n"
                              f"Processing your document...")
        
        # You can implement your processing logic here

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}. Please send your options in the format:\n"
                              "Number of copies, color (black or white), orientation (landscape or portrait), quality (50, 75, or 100)")

    # Clear user state after processing
    del user_states[message.from_user.id]

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# Start the bot
bot.infinity_polling()


