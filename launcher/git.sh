#!/bin/bash
git status &> diff.out
python3 ../Pyttai/Pychat/main.py -c "/file diff.out Give me a commit message for this status."
