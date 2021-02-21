import json
from pymongo import MongoClient

client = MongoClient('mongo', 27017, username="root", password="example")
db = client.bot_db
user_links_collection = db.user_links_collection
channel_user_links_collection = db.channel_user_links_collection


def link_account(tele_user, chess_user):
    tele_user = str(tele_user)
    linked_account = {"chess_user": chess_user, "tele_user": tele_user}
    user_links_collection.replace_one(
        {"tele_user": tele_user}, linked_account, True)


def get_linked_account(tele_user):
    tele_user = str(tele_user)
    user = user_links_collection.find_one({"tele_user": tele_user})
    if user is None:
        return None
    return user["chess_user"]


def add_to_group(tele_channel, chess_user):
    channel = channel_user_links_collection.find_one(
        {"tele_channel": tele_channel})
    if channel is None:
        channel = {"tele_channel": tele_channel, "users": []}
    if chess_user not in channel["users"]:
        channel["users"].append(chess_user)
        channel_user_links_collection.replace_one(
            {"tele_channel": tele_channel}, channel, True)

def remove_from_group(tele_channel, chess_user):
    channel = channel_user_links_collection.find_one(
        {"tele_channel": tele_channel})
    if channel is None:
        channel = {"tele_channel": tele_channel, "users": []}
    if chess_user in channel["users"]:
        channel["users"] = list(filter(lambda user: user != chess_user, channel["users"]))
        channel_user_links_collection.replace_one(
            {"tele_channel": tele_channel}, channel, True)



def get_all_linked_accounts(tele_channel):
    channel = channel_user_links_collection.find_one(
        {"tele_channel": tele_channel})
    if channel is None:
        return []
    return channel["users"]
