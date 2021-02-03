import os, time, json
from chessdotcom import get_player_stats 
import discord

TOKEN = json.loads(open('secret.json', 'r').read())["discord_token"]
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.content.startswith('!chessrating '):
        player = message.content.split(' ')[1]
        stats = get_player_stats(player).json
        reply = f'Ratings for {player}:\n'
        for chess_type in stats:
            if type(stats[chess_type]) is not dict:
                continue 
            if 'last' not in stats[chess_type]:
                continue
            if 'rating' not in stats[chess_type]['last']:
                continue
            rating = stats[chess_type]['last']['rating']
            rd = None
            if 'rd' in stats[chess_type]['last']:
                rd = stats[chess_type]['last']['rd']
            reply += f'  {chess_type}: {rating} RD({rd})\n'
        await message.channel.send(reply)

client.run(TOKEN)