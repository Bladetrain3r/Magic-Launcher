#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MLRun - Sequential/Parallel Command Executor for Magic Launcher

WHY THIS EXISTS WHEN MLMENU HAS -c:
MLMenu -c was designed for simple sequential navigation: "1 2 3" = "enter folder 1, then item 2, then item 3"
It's perfect for navigating to and launching a single target.

MLRun is designed for COMPOSITION: "1 | 2 & 3" = "pipe 1 to 2, while also running 3"
It's for building workflows from multiple commands.

THE KEY DIFFERENCE:
- MLMenu -c: Navigate a hierarchy, launch one thing
- MLRun: Compose multiple things into pipelines and parallel workflows

WHAT MLRUN ADDS:
- Pipe operator (|) for connecting command outputs to inputs  
- Parallel operator (&) for concurrent execution
- Treats each number as a standalone command, not navigation
- Designed for workflow automation, not interactive use

EXAMPLE:
MLMenu -c "1 2 3" = Go into menu 1, select item 2, then item 3 (navigation)
MLRun "1 | 2 | 3" = Run cmd 1, pipe output to cmd 2, pipe that to cmd 3 (composition)

In essence: MLMenu navigates TO commands, MLRun composes WITH commands.

Both read shortcuts.json, both use numbers, totally different purposes.
One is a menu navigator, one is a workflow engine.
"""

import json
import subprocess
import sys
from pathlib import Path

def load_shortcuts():
    config_path = Path.home() / '.config/launcher/shortcuts.json'
    with open(config_path) as f:
        return json.load(f)

def run_sequence(sequence, shortcuts):
    """Parse and run: 1 | 2 & 3 | 4"""
    
    # Split by & for concurrent groups
    groups = sequence.split('&')
    
    for group in groups:
        # Split by | for pipes within group
        commands = group.strip().split('|')
        
        if len(commands) == 1:
            # Simple command
            run_single(commands[0].strip(), shortcuts)
        else:
            # Piped commands
            run_piped(commands, shortcuts)

def run_single(num, shortcuts):
    # Flatten shortcuts and find by number
    cmd = find_by_number(num, shortcuts)
    subprocess.run(f"{cmd['path']} {cmd.get('args', '')}", shell=True)

def find_by_number(num, shortcuts):
    """Find command by number in shortcuts"""
    for cmd in shortcuts:
        if cmd['number'] == num:
            return cmd
    raise ValueError(f"Command with number {num} not found in shortcuts.")

def run_piped(numbers, shortcuts):
    # Build pipeline
    procs = []
    for i, num in enumerate(numbers):
        cmd = find_by_number(num.strip(), shortcuts)
        full_cmd = f"{cmd['path']} {cmd.get('args', '')}"
        
        if i == 0:
            proc = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen(full_cmd, shell=True, 
                                  stdin=procs[-1].stdout, stdout=subprocess.PIPE)
        procs.append(proc)
    
    # Get final output
    output = procs[-1].communicate()[0]
    print(output.decode())

if __name__ == "__main__":
    shortcuts = load_shortcuts()
    run_sequence(sys.argv[1], shortcuts)