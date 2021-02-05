import json

def get_all_linked_accounts():
    linked_accounts = json.loads(open('db/linked_accounts.json', 'r').read())
    return linked_accounts

def link_account(tele_user, chess_user):
    linked_accounts = get_all_linked_accounts()
    linked_accounts[tele_user] = chess_user
    open('db/linked_accounts.json', 'w').write(json.dumps(linked_accounts))
    
def get_linked_account(tele_user):
    linked_accounts = get_all_linked_accounts()
    if tele_user not in linked_accounts:
        return None
    return linked_accounts[tele_user]
