from re import A
import sys
import json
import rich
from rich import traceback
from InquirerPy import prompt
from InquirerPy.base.control import Choice
traceback.install()


def select_account_interactive(file_path):

    with open(file_path, 'r') as f:
        account_lists = json.load(f)

    # Environment selection
    env_result = prompt([{
        "type": "list",
        "name": "env",
        "message": "Select environment:",
        "choices": ["pro", "pre", "dev"]
    }])    
    env = env_result['env']
    
    # Create name-to-id mapping
    name_to_id = {name: account_id for account_id, name in account_lists[env].items()}
    
    # Create choices with just account names
    account_choices = [
        Choice(account_name, account_name)
        for account_name in account_lists[env].values()
    ]
    
    account_result = prompt([{
        "type": "list",
        "name": "account", 
        "message": f"Select account for {env}:",
        "choices": account_choices
    }])
    
    selected_account_name = account_result['account']
    selected_account_id = name_to_id[selected_account_name]
    
    return env, selected_account_id, selected_account_name


def main():
    env, account_id, account_name = select_account_interactive()
    print(f"Environment: {env}, Account: {account_id}, Account Name: {account_name} ({account_id})")

if __name__ == "__main__":
    main()