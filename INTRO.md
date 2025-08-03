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