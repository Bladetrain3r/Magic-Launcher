#!/usr/bin/env python3
"""
MLAgent - Natural language to MLMenu commands
Part of ML-Extras

ONE JOB: Ask LLM to translate request to menu numbers
"""

import json
import sys
import os
from pathlib import Path

def check_shortcuts():
    """Make sure shortcuts.json exists"""
    path = Path.home() / '.config' / 'launcher' / 'shortcuts.json'
    if not path.exists():
        print(f"Error: No shortcuts.json at {path}")
        sys.exit(1)
    return path

def shortcuts_to_menu(shortcuts_path):
    """Convert shortcuts.json to numbered menu"""
    with open(shortcuts_path) as f:
        data = json.load(f)
    
    menu = []
    def add_items(items, depth=0):
        for i, (name, item) in enumerate(items.items(), 1):
            indent = "  " * depth
            if item.get('type') == 'folder':
                menu.append(f"{indent}{i}. {name}/")
                if 'items' in item:
                    add_items(item['items'], depth + 1)
            else:
                menu.append(f"{indent}{i}. {name}")
    
    add_items(data)
    return "\n".join(menu)

def ask_llm(prompt, menu_text, api_url="http://localhost:1234/v1/chat/completions"):
    """Ask LLM for number sequence"""
    import requests
    
    system = f"""Convert requests to menu navigation numbers.

Menu:
{menu_text}

Output ONLY numbers separated by spaces.
For "then": use new line
For "at same time": use &

Examples:
"run test" -> "3"
"run test then deploy" -> "3\n2"  
"build and test at same time" -> "1 & 3"
"""

    try:
        resp = requests.post(api_url, json={
            "model": "local",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        })
        
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"LLM Error: {e}")
    
    return None

def main():
    if len(sys.argv) < 2:
        print("MLAgent - Natural language to menu numbers")
        print("Usage: mlagent 'what you want to do'")
        print("Example: mlagent 'build then deploy'")
        sys.exit(1)
    
    prompt = ' '.join(sys.argv[1:])
    
    # Setup
    shortcuts = check_shortcuts()
    menu = shortcuts_to_menu(shortcuts)
    
    # Ask LLM
    print(f"Request: {prompt}")
    result = ask_llm(prompt, menu)
    
    if not result:
        print("Failed to get answer")
        sys.exit(1)
    
    # Just output what LLM said
    print(f"\nCommands:\n{result}")
    
    # Optionally save to file
    print(f"\nTo run:")
    for line in result.split('\n'):
        if '&' in line:
            # Concurrent commands
            cmds = line.split('&')
            for cmd in cmds:
                print(f"mlmenu -c '{cmd.strip()}' &")
            print("wait")
        else:
            # Sequential
            print(f"mlmenu -c '{line.strip()}'")

if __name__ == "__main__":
    main()