import os
import time
import json
import discord
from chessdotcom import get_player_stats
from rating import get_ratings


TOKEN = json.loads(open('secret.json', 'r').read())["discord_token"]
client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.content.startswith('!chessrating '):
        player = message.content.split(' ')[1]
        ratings = get_ratings(player)
        reply = f'Ratings for {player}:\n'
        for chess_type in ratings:
            stat = ratings[chess_type]
            rating = stat['rating']
            rd = stat['rd']
            reply += f'  {chess_type}: {rating} RD({rd})\n'
        await message.channel.send(reply)

client.run(TOKEN)
