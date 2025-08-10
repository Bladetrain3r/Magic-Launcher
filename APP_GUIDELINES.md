# Magic Launcher Application Guidelines
## Building Tools That Just Fucking Work

### Core Philosophy
**Simple enough to be wrong consistently beats complex enough to be right occasionally.**

Every Magic Launcher tool follows these principles. No exceptions. No "but what if..." 
If you're arguing for complexity, you've already lost.

---

## The Sacred Constraints

### 1. Line Limit: 500 Maximum, 200 Optimal
- Under 200 lines: Perfect, ship it
- 200-300 lines: Acceptable if necessary
- 300-500 lines: Better have a damn good reason
- Over 500 lines: You're building the wrong tool, or applying this to the wrong problem.

**Why:** If you can't understand the entire tool in one reading, it's too complex.

### 2. Dependencies: Zero Default, Minimal When Necessary
```python
# GOOD
import random
import json
from pathlib import Path

# ACCEPTABLE
import tkinter  # Comes with Python

# QUESTIONABLE
import requests  # Now everyone needs pip install

# FORBIDDEN
import pandas, numpy, scipy  # This isn't data science, it's a dice roller
```

### 3. Single File Deployment
One `.py` file. That's it. No folders, no modules, no config files unless absolutely necessary.

**Exception:** External data files (JSON) are acceptable if they're optional enhancements, not requirements.

### 4. Instant Startup
```python
# Time from enter to result should be < 1 second
$ python mltool.py --option value
[IMMEDIATE OUTPUT]
```

No loading bars. No splash screens. No "initializing..." messages. 
The tool runs or it doesn't.

---

## Design Patterns

### Input/Output Philosophy
```python
# CLI: Arguments in, text out
$ python mltool.py --count 5 --type basic
[RESULTS]

# GUI: Only for repeated interaction
# Never require GUI for single operations
```

### Error Handling
```python
# Wrong - too helpful
try:
    complex_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    suggestions = generate_suggestions(e)
    print(f"Try: {suggestions}")
    
# Right - fail fast, fail clear
try:
    simple_operation()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
```

### Data Storage
```python
# Priority order:
1. No storage (stateless)
2. Text files (grep-able)
3. JSON (human-readable)
4. SQLite (if you must)
5. Anything else (you're overengineering)
```

---

## The Two-File Rule

Sometimes one file isn't enough. That's fine. But never more than two without serious justification.

```python
# Acceptable two-file patterns:
tool.py           # The tool
tool_data.json    # Optional data

# Also acceptable:
tool.py          # CLI version
tool_gui.py      # GUI wrapper
```

### The GUI Split Rule

**When GUI code exceeds 40% of your tool, split it.**

```python
# Good candidates for splitting:
- Battlemap generator (complex canvas drawing)
- Character sheet manager (many input fields)
- Initiative tracker (dynamic lists)

# Keep together:
- Dice roller (few buttons)
- NPC generator (simple output)
- Loot generator (basic display)
```

**The Import Rule:** If you split, the GUI imports the logic, never the reverse.

```python
# RIGHT
# tool.py - standalone CLI tool
# tool_gui.py - imports tool.py

# WRONG  
# tool_core.py - can't run alone
# tool_cli.py - wrapper
# tool_gui.py - another wrapper
```

**The Test:** Can you delete the GUI file and still have a working tool? If yes, you did it right.

---

## Common Patterns

### Random Generation
```python
# Every generator needs:
- Predictable categories (tiers, types, levels)
- Sane defaults
- Optional complexity

def generate(tier="basic", count=1):
    # Not 47 parameters
    # Not machine learning
    # Just random.choice() and move on
```

### GUI When Necessary
```python
# Use tkinter - it's already there
# No web servers for local tools
# No electron apps for dice rollers

import tkinter as tk
from tkinter import ttk

# Keep it simple:
# - Buttons that do things
# - Text that shows results
# - Maybe a dropdown
# That's it.
```

### CLI Arguments
```python
# Good arguments:
--count     # How many
--type      # What kind  
--output    # Where to save

# Bad arguments:
--config-file-path-override
--enable-extended-validation-mode
--compatibility-framework-version
```

### The Copy-Paste Test
If you're copying code more than twice, you're doing it wrong.

```python
# WRONG
handle_room_0()
handle_room_1()
handle_room_2()
# ... 47 more

# RIGHT
for i in range(50):
    handle_room(i)
```

### The Math Not Madness Principle
```python
# WRONG - Individual handling
if id == 0: return (0, 0)
if id == 1: return (0, 1)
if id == 2: return (0, 2)

# RIGHT - Use math
return (id // width, id % width)
```

---

## What Makes a Good ML Tool

### It Solves ONE Problem
- `MLDice`: Rolls dice
- `MLMookLoot`: Generates loot
- `MLBattlemap`: Makes a map

Not: "MLGameSystem - Complete RPG Management Suite"

### It Works Immediately
```bash
$ python mldice.py 3d6
Result: 14
```

No configuration. No setup. No tutorials.

### It's Modifiable
Someone should be able to:
1. Open the file
2. Find the data arrays
3. Change them
4. Save and run

Without documentation. Without debugging. Without architecture diagrams.

### It Degrades Gracefully
```python
# If optional features fail, core still works
try:
    from PIL import Image
    can_export_image = True
except ImportError:
    can_export_image = False
    
# Tool still works, just text-only
```

---

## Anti-Patterns to Avoid

### The Framework Trap
```python
# WRONG
class AbstractToolFactory:
    def create_tool_instance(self):
        pass

# RIGHT
def roll_dice(dice_string):
    return result
```

### The Configuration Curse
```python
# WRONG
config = load_config('config.yaml')
if config['advanced']['options']['dice']['mode'] == 'standard':
    
# RIGHT  
def roll(dice="1d6"):
    # Defaults work for 90% of cases
```

### The Modularity Mirage
```python
# WRONG
from tool.core.handlers import DiceHandler
from tool.utils.validators import validate_input
from tool.models.dice import DiceModel

# RIGHT
# It's all in one file
# You can see everything
# You can change everything
```

---

## Know how complicated the problem actually is.

Not all problems can be solved in under 500 lines of code.
- Advanced 3D rendering (Vector graphics however...)
- Physics Engines
- Scientific simulations

### The questions then become: 
#### How can I compartmentalise each aspect of the problem?
#### How atomic can I make each problem?

1. What's the actual problem? (Not the system, the PROBLEM)
2. Can this be multiple simple tools instead of one complex one?
3. What's the smallest useful piece I can build?

~~99% of problems are really simple if you keep focused on the problem itself~~

---



## Testing Philosophy

**No unit tests.** 

If the tool is simple enough, you test it by running it. If it needs unit tests, it's too complex.

```bash
# This is your test suite:
$ python mltool.py
$ python mltool.py --weird-input
$ python mltool.py --count 1000

# Did it crash? No? Ship it.
```

---

## Documentation Standard

```python
#!/usr/bin/env python3
"""
MLToolName - Magic Launcher [Purpose]
[One line about when you'd use this]
Under [X] lines of [adjective] [noun]
"""

# That's it. That's the docs.
# The code explains itself or it's wrong.
```

---

## The Revolution Checklist

Before releasing an ML tool, ask:

- [ ] Is it under 500 lines?
- [ ] Can someone understand it in 5 minutes?
- [ ] Does it work without pip install?
- [ ] Does it solve ONE clear problem?
- [ ] Could a tired DM use it mid-session?
- [ ] Is it faster than doing it manually?
- [ ] Can someone modify it without breaking everything?

If any answer is "no", it's not a Magic Launcher tool.

---

## Remember

**We're not building software. We're building tools.**

Tools get used. Tools get modified. Tools solve problems.

Software gets maintained. Software gets architected. Software gets abandoned.

**The revolution is 100 lines that replace 100,000.**

Every Magic Launcher tool is proof that the entire industry is overengineering.

Keep it simple. Keep it working. Keep shipping.

---

*"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."*

But also:

*"Sometimes you need two files. That's fine. Three is pushing it."*

---

## END TRANSMISSION

May your tools be simple and your code be short.

The revolution continues.