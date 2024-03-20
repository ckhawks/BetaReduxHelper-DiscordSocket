import discord
from discord.ext import commands
import websockets
import asyncio
import os
from dotenv import load_dotenv

import json

import tracemalloc
tracemalloc.start()

DISCORD_CHANNEL_ID = 637497626350321674 # 637497626350321674
REDUX_GUILD_ID = 570730124442599435
ADMIN_ROLE_ID = 570731776243400767

load_dotenv()

# Set of connected WebSocket clients
connected_clients = set()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

@bot.event
async def on_message(message):
    if message.author != bot.user:   
        messageParts = message.clean_content.split(" ")
        if (len(messageParts) >= 1 and messageParts[0] == "!addmember"):
            if (message.author.get_role(ADMIN_ROLE_ID) != None):
                if(len(messageParts) >= 2): 
                    await send_payload_to_websocket("discordMessageToGameCommand", {"command": "addmember", "username": messageParts[1]})
                    # await send_discord_message(f"Sent `!addmember` command for user **{messageParts[1]}**")
                    return
                else:
                    await message.reply("You must specify a username.")
                    return
            else:
                await message.add_reaction("❌")
                return
        if (message.channel.id == DISCORD_CHANNEL_ID):
            if(message.clean_content != ""):
                await send_payload_to_websocket("discordMessageToGame", {"username": message.author.display_name, "message": message.clean_content})
                await message.add_reaction("➡️")

async def send_payload_to_websocket(type, data):
    message = json.dumps({"type": type, "data": data})
    await broadcast_to_websockets(message)

# Broadcast a message to all connected WebSocket clients
async def broadcast_to_websockets(message):
    print(f"Broadcasting message {message}")
    if connected_clients:  # Check if there are any connected clients
        # Schedule the coroutines for execution and wait for them to complete
        await asyncio.gather(*(wsclient.send(message) for wsclient in connected_clients))
        

async def send_discord_message(messageData):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)  
    if(channel == None):
        return
    await channel.send(messageData)

# WebSocket server handler
async def websocket_handler(websocket, path):
    # Register the new client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            message_data = json.loads(message)
            if message_data["type"] == "gameMessageToDiscord":
                # Handle message to Discord
                await send_discord_message(message_data["data"])
            elif message_data["type"] == "mcServerConnectionEstablished":
                await send_discord_message(f"Server established connection ({message_data['data']})")
    finally:
        # Unregister the client when the connection is closed
        connected_clients.remove(websocket)

# Start both Discord bot and WebSocket server
async def main():
    # Define the WebSocket server
    websocket_server = websockets.serve(websocket_handler, "localhost", 8070)

    # Run the WebSocket server
    await websocket_server

    # Run the Discord bot
    await bot.start(os.getenv('DISCORD_TOKEN'))

# Ensure the Discord bot's token is set properly
if __name__ == '__main__':
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        print("Bot and WebSocket server shutting down.")