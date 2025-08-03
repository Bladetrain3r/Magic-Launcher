# Magic Launcher Paradigm: Introductory Document
## Why this doc?

- In building magic launcher and documenting the insights gained, there's been a significant growth in the sheer volume of text.
- This intro doc is a briefer summary of the technical key points and the "why" behind such aggressive simplicity.
- In general, the ML Paradigm is not a full slot-in replacement methodology for every scenario
- Instead, it asks you to ask the question "If it can be done simply, why have we complicated it?" 

## Magic Launcher Paradigm: Summary
### Core Philosophy
The Magic Launcher Paradigm prioritizes simplicity, speed, and user autonomy in software design. It builds tools that do one thing well, launch instantly, and work everywhere without surveillance or bloat.

### The Core Defiance: Universal Agnosticism
- The true power of this paradigm lies not in this repository's specific Python implementation, but in its profound simplicity. 
- The core design—a basic JSON file describing a command to execute—is entirely language and system-agnostic.
- This core functionality could be replicated on almost any system with a simple text parser and an execution primitive.
- You could write a launcher in a Bash script, or even in BASIC on a computer from the 1980s. 

## The Three Pillars

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

## Key Principles

### Tools, Not Services:  
- Tools launch without accounts, internet, or updates.  
- Services (e.g., AI, cloud) are chosen consciously, not forced.

### Simplicity is Security:  
- Minimal code (~200 lines) reduces attack surfaces.  
- Transparency (e.g., plain JSON) prevents hidden malice.


### Compose, Don’t Abstract:  
- Use pipelines (mltool | mlother) over inheritance or frameworks.  
- Copy-paste code to avoid coupling.


### JSON as Interface (or any simple parseable list format really):  
- shortcuts.json defines commands (e.g., {"1": {"path": "xterm"}}).  
- Numbers as verbs (mlrun "1 | 2") enable simple automation.

### Avoid Metadata Metastasis:  
- Keep configs lean; no unnecessary fields (e.g., usage stats).  
- Use filesystem or external tools for analytics.

### Duplication seems complex, coupling IS complex
- Adding fields to existing records is often considered easier than simply creating new records
- My experience is that this results in difficulties debugging, and makes automation fiddly
- A file based system for handling data allows portions of logic to be ported without affecting the core
- Therefore, ML based apps will prefer additional files (password.txt) loaded separately, to additional fiels {"password":"foo", "shortcuts": {"Nesting": "More"}}

## Tools in the Ecosystem

- **Magic Launcher:** GUI for launching shortcuts visually.  
- **MLMenu:** Terminal fallback for SSH or minimal systems.  
- **MLRun:** Non-interactive workflow composition via number sequences.  
- **Sequai:** Translates intent to numbers for AI integration.  
- **MLView:** Image viewer using minimal PIL features to avoid bloat.

## Case Studies

### Terraform Critique: Replaces stateful complexity with stateless shell scripts.  
- Modern Games: Rejects 100GB, always-online bloat for executable-based launching.  
- Microservices: Achieves true independence with text streams, not Kubernetes.

## Litmus Tests for Features
Before adding anything, ask:  

- Works over SSH on a 56k modem?  
- Runs on a 2005 computer?  
- Useful as the only feature?  
- Implementable in <100 lines?  
- Will it work in 10 years?If any answer is "no," reconsider.

## The Promise
Magic Launcher tools:  

- Start instantly.  
- Work offline, everywhere.  
- Respect your hardware and choices.  
- Never phone home or require accounts.  
- Just. Fucking. Work.

### Why It Matters
In a world of bloated, surveillance-heavy software, Magic Launcher offers a return to tools that empower users. By staying simple, composable, and transparent, it enables workflows from local scripts to distributed systems without losing clarity or control.

"Click a button, run a thing. No accounts, no updates, no bullshit."

## Optional Reading

This is just to provide insight into my perspective, and isn't directly relevant into Magic Launcher's usage.

## The Goal
Every extra step or stop to look around is extra cognitive overhead, every new messy way of organising an additional layer on top of complex enough systems on their own.
The goal is to make any action you can perform on your computer, or almost, something that can be translated into a click and saved for re-use.
You click, it goes. All else is to aid this objective, or it is cut.

I am not averse to quality of life, and as the roadmap should indicate I have clear ideas of what constitutes a reasonably comprehensive featureset for such a project.
But if it hits a point where I have to do more than click once on my task bar, type a few letters, and press enter, Magic Launcher has slipped from it's path.

## The Artistic Statement
At this point, I can only consider the production of Magic Launcher, the manifesto, and even the extras to be a form of programmer art.
While DevOps isn't programming or art in the traditional sense, it's got both creative and logical demands.
Magic Launcher, is a philosophical scream. The code manifesto, is what came out after I got the yell out of my system.
The Magic Launcher Paradigm, as described, is what I hope becomes an example of making software in fun, making it simple, making it solve.
Because every success I've ever had, even when working in full software as a service, has lain in making it simple, and having fun while I'm making it.
Terraform is cool, but it is the antonym of fun. Ansible is awesome, but one misaligned YAML and you've got silent failures down the whole chain.

I've also been, my entire life, an avid and regular video gamer, and power user. 
From either perspective, it's been... demoralising to watch the potential of a connected information world get squandered in subscription services and excess analytics.
I grew to love computers because they made magic happen on the screen, faster than I could even blink. When did that become a sign your app is insufficient?
Everyone proudly proclaims their "low" response times and "streamlined" 12MB landing pages, when the backing behind it is several hundred appliances strong and supported by a half broken brick.
I can't even embed some 2 minute Youtube videos in a static site without increasing the number of requests and bandwidth to load it by over a dozen times.

Online applications have the potential to bring the Star Trek computer experience to us. 
But "computer, help me with this problem." has been replaced as the ideal with the idea that an application being free means *you are the product*.

This entire project is a scream. 
But, by the very nature of it, rather than being destructive, I seek to express *frustration through utility*.
I hope that, considering the degree of frustration, the utility is equally significant.

If you have opened the repository and read this far, thank you. This much is enough, if it hasn't sparked an interest in the code presented. 
If you are still interested, please:
- Peruse this file, the FAQ, and the Changelog at your leisure to learn how Magic Launcher can be nifty for you.
- Take a look at the CODEMANIFESTO and ADDENDUMs in the DOCS folder for a deep dive into exactly what this is all about.
- Run Magic Launcher, add one or two of your favourite browser links, maybe try setting up a shortcut to open task manager or launch your IDE. Tell me how it works for you.
- Experiment, modify, or update any of the apps involved to your taste - they're fairly bite sized.

And lastly, please:
Think of a small problem, focus on just that, and write a program to solve it. 
It's easier than it sounds, and you know you've solved a real problem when running the fix makes a grin pop up.

Enjoy Magic Launcher!

🔥🔥🔥 THE ETERNAL LAUNCHER 🔥🔥🔥

        "I have become Tool, destroyer of bloat"

   In the grim darkness of the far future, there is only
             S U B P R O C E S S . R U N ( )

~~~~~~~~~~~~ ╔════════════════════════════════════════════════════════╗
~~~~~~~~~~~~ ║           M A G I C   L A U N C H E R   v ∞            ║
~~~~~~~~~~~~ ╠════════════════════════════════════════════════════════╣
~~~~~~~~~~~~ ║                                                        ║
~~~~~~~~~~~~ ║   Born: 2025                                           ║
~~~~~~~~~~~~ ║   Dependencies: python.os.subprocess()                 ║
~~~~~~~~~~~~ ║   Death: Sometime between grep and sed                 ║
~~~~~~~~~~~~ ║                                                        ║
~~~~~~~~~~~~ ║   "It launches things."                                ║
~~~~~~~~~~~~ ║   "That's it."                                         ║
~~~~~~~~~~~~ ║                                                        ║
~~~~~~~~~~~~ ║   ┌───────────────────────────────────────────────┐    ║
~~~~~~~~~~~~ ║   │  while universe.exists():                     │    ║
~~~~~~~~~~~~ ║   │      if button.clicked():                     │    ║
~~~~~~~~~~~~ ║   │          subprocess.run(thing)                │    ║
~~~~~~~~~~~~ ║   └───────────────────────────────────────────────┘    ║
~~~~~~~~~~~~ ║                                                        ║
~~~~~~~~~~~~ ║   Not a service. Not a platform. Just a tool.          ║
~~~~~~~~~~~~ ║                                                        ║
~~~~~~~~~~~~ ╚════════════════════════════════════════════════════════╝

           In 2045, when the AIs have taken over,
           they'll still use Magic Launcher to run
                    their world domination scripts.
                    
                 Because it just works.™