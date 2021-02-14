import json
from pymongo import MongoClient

client = MongoClient('mongo', 27017, username="root", password="example")
db = client.bot_db
user_links_collection = db.user_links_collection


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


def get_all_linked_accounts():
    linked_accounts = user_links_collection.find()
    return [user["chess_user"] for user in linked_accounts]
