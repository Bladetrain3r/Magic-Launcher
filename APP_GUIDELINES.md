# Magic Launcher Application Guidelines
## Building Tools That Just Fucking Work

### Core Philosophy
**Simple enough to be wrong consistently beats complex enough to be right occasionally.**

Every Magic Launcher tool follows these principles. No exceptions. No "but what if..." 
If you're arguing for complexity, you've already lost.

---

## The Pillars

### Speed is Life, Bloat is Death  
- Sub-second startup, <50MB RAM.  
- Every feature must justify its performance cost.

### OS-Free Thinking  
- Same behavior across platforms (Raspberry Pi to gaming rig).  
- No OS-specific dependencies; use file-based configs.

### Focused Functionality  
- Solve one problem exceptionally.  
- Resist feature creep; explainable in one sentence.

## Technical Standards

### Minimum Requirements:  
- 640x480 display, 32MB RAM, Python 3.6+, minimal dependencies (stdlib preferred).

### Visual Design:  
- CGA/EGA-inspired colors, monospace fonts, fixed grids.  
- No animations, support 16-color terminals.

### Code Principles:  
- Simple, fast code (e.g., subprocess.run(path)) over clever abstractions.  
- Fail gracefully, log quietly, prioritize keyboard navigation.
```
File Structure:  app_name/
├── app.py        # Core logic
├── config.json   # Human-readable config
└── README.md     # One-page max
```

## Target Constraints

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

### Guide for Builders
- Design for deletion. 
- If a component can’t be removed without surgery, it’s the wrong component. 
- Favor small processes with clear seams, plain files over hidden state, and interfaces you can replace in an afternoon.
~~Easy to delete, easy to replace~~
- Measure ends, not means. 
- Pick one metric that tracks the outcome you actually care about (e.g., time-to-success for a user task), and treat all other numbers as diagnostics, not targets. 
- If a metric starts steering behavior away from purpose, drop it—even if it’s beautifully instrumented.
~~Easy measure, easy interpret~~
- Speak human, cut intermediaries. 
- Require that designs, docs, and PR descriptions pass the “smart friend outside the team” test. 
- Prefer mechanisms over metaphors, examples over jargon, and defaults that work without training. 
- Every interpreter you remove returns autonomy to the people doing the work.
~~The Law of Self Interest dictates the middleman places you second~~

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

### Recommended Further Reading
The DOCS folder has gotten quite lengthy and I admit significant portions are the WHY of things or musings on completely separate topics.
Key Documents I think will provide you the toolkit to create tools that bring you joy:

#### APP_GUIDELINES.md
This document was already a good start.

#### making_tools/command_expansion.md
How to use `$()` to compose tools. The forgotten Unix power that turns every CLI into a function.

#### making_tools/templates/
- `core.py` - Basic CLI template (17 lines of boilerplate)
- `core_plus_gui.py` - CLI with optional GUI 
- `template.html` - Web interface template
Start with these. Modify the `run()` function. Ship it.

#### Vol. 2 03 + 04
- "Glyphs are magic" explains a lot about why pipes and text streams can be powerful

#### Vol1. Silicon_Spring.html
[https://zerofuchs.co.za/manifesto/SILICONSPRING.html]
The aspiration. The mad dream. The philosophy behind the revolution. Read when you need motivation or context.
Or just hit up the webpage: 

#### making_tools/ (folder)
A folder specifically earmarked for documents covering practical implementation:
- Command expansion, pipes, and Unix composition patterns
- Cron scheduling and automation
- Different ways of composing MLTools to produce solutions
- Real-world examples and patterns
## END TRANSMISSION

May your tools be simple and your code be short.

The revolution continues.