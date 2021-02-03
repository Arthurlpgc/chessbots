import json


def link_account(tele_user, chess_user):
    linked_accounts = json.loads(open('db/linked_accounts.json', 'r').read())
    linked_accounts[tele_user] = chess_user
    open('db/linked_accounts.json', 'w').write(json.dumps(linked_accounts))
    
def get_linked_account(tele_user):
    linked_accounts = json.loads(open('db/linked_accounts.json', 'r').read())
    if tele_user not in linked_accounts:
        return None
    return linked_accounts[tele_user]