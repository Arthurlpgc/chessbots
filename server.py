import os, time
from chessdotcom import get_player_stats 
import discord

TOKEN = 'Nzk1MzAyNDYxMDM1NjQyODkw.X_HZIg.9bQPhiF43SFwHY5ix9R28jcG_wM'
chess_mute_channel_id = 795307391104188446
guild_id = 589214102631481419
players = []
client = discord.Client()

async def refresh_players():
    if len(players) == 0:
        return
    guild = await client.fetch_guild(guild_id)
    channel = await client.fetch_channel(chess_mute_channel_id)
    for member_id in channel.voice_states:
        state = channel.voice_states[member_id]
        if (not state.self_mute):
            member = await guild.fetch_member(member_id)
            should_mute=(member.name not in players)
            await member.edit(mute=should_mute)
            if should_mute:
                print('Muted',member.name)
            else:
                print('Unmuted',member.name)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await refresh_players()

@client.event
async def on_voice_state_update(member, _old_state, new_state):
    channel = new_state.channel
    if channel != None and channel.id != chess_mute_channel_id:
        return
    if (not new_state.self_mute) and (not new_state.mute):
        if member.name not in players:
            await member.edit(mute=True)
            print('Muted',member.name)

@client.event
async def on_message(message):
    global players
    if message.content.startswith('!chessmatch'):
        players = [x.name for x in message.mentions]
        player_replies = [f'<@{x.id}>' for x in message.mentions]
        await message.channel.send('Players playing: '+ ' '.join(player_replies))
        await refresh_players()
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
            reply += f'  {chess_type}: {rating}\n'
        await message.channel.send(reply)

client.run(TOKEN)