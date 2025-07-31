# The Magic Launcher Paradigm

## Core Philosophy

The Magic Launcher Paradigm is a development philosophy that prioritizes simplicity, speed, and universal compatibility over feature completeness. It's about building tools that solve real problems without creating new ones.

### The Three Pillars

1. **Speed is Life, Bloat is Death**
   - If it doesn't start instantly, it's too heavy
   - If it needs more than 50MB RAM, reconsider the approach
   - Every feature must justify its performance cost

2. **OS-Free Thinking**
   - Works the same on a Raspberry Pi as on a gaming rig
   - No OS-specific dependencies or behaviors
   - File-based configuration over registry/system settings

3. **Focused Functionality**
   - Do one thing exceptionally well
   - Resist feature creep like your life depends on it
   - If you can't explain it in one sentence, it's too complex

## Technical Standards

### Minimum Requirements
- **Display**: 640x480 @ 16 colors (VGA minimum)
- **RAM**: 32MB available
- **CPU**: If it runs Python 3.6+, it's enough
- **Dependencies**: Standard library preferred, minimal external deps

### Visual Design
- **Color Palette**: CGA/EGA inspired but true color capable
  - Support 16-color terminals as baseline
  - Use true color when available, but never require it
- **Fonts**: Monospace preferred, system fonts acceptable
  - Courier, Consolas, or system default
  - Unicode support best-effort, not required
- **Layout**: Fixed grids over responsive design
  - Predictable is better than flexible
  - No animations or transitions

### Code Principles

```python
# YES: Simple, obvious, fast
def launch_app(path):
    subprocess.run(path)

# NO: Clever, abstract, slow  
class ApplicationLauncherFactory:
    def create_launcher(self, config):
        return self._build_launcher_with_plugins(config)
```

## The Manifesto

### We Believe:

1. **A tool should load faster than you can blink**
   - Cold start to usable in under 1 second
   - No splash screens, no loading bars

2. **Configuration is a file, not a journey**
   - One config file, human-readable
   - No wizards, no "first run experience"
   - Sensible defaults that just work

3. **The terminal is not the enemy**
   - CLI-first design with GUI as convenience
   - Text is universal, widgets are not
   - SSH-friendly by default

4. **Less is exponentially more**
   - Every feature doubles the bug surface
   - Every option confuses someone
   - Every dependency is a future breakage

5. **Retro aesthetics are timeless**
   - What worked in 1985 still works today
   - Pixel-perfect beats anti-aliased
   - Function defines form

## Implementation Guidelines

### File Structure
```
app_name/
├── app.py           # Single entry point
├── config.json      # Simple, obvious config
└── README.md        # One page max
```

### Error Handling
- Fail gracefully, log quietly
- Never crash on bad input
- Default to safe behavior

### User Interface
- Keyboard shortcuts for everything
- Mouse support as backup, not primary
- No context menus deeper than one level
- No tooltips required to understand functionality

## Examples of the Paradigm

### Good ML-Paradigm App:
- **Purpose**: Display text files
- **Features**: Open, display, zoom
- **Size**: 200 lines of code
- **Dependencies**: None beyond stdlib

### Bad ML-Paradigm App:
- **Purpose**: Display text files
- **Features**: Syntax highlighting, themes, plugins, cloud sync, AI suggestions
- **Size**: 50,000 lines of code  
- **Dependencies**: 47 npm packages

## The Litmus Tests

Before adding any feature, ask:

1. **Does it work over SSH on a 56k modem?**
2. **Can it run on a computer from 2005?**
3. **Would you use it if it was the only feature?**
4. **Can you implement it in under 100 lines?**
5. **Will it still work in 10 years?**

If any answer is "no", reconsider.

## For ML-Extras Specifically

Tools in ML-Extras should:
- Launch from Magic Launcher with single shortcut
- Share the visual aesthetic (green/gray/CGA)
- Require no installation beyond copying files
- Solve one problem completely
- Work without network access
- Store data in obvious places

## The Promise

By following the Magic Launcher Paradigm, we promise to deliver tools that:
- Start instantly
- Work everywhere  
- Never surprise you
- Respect your time
- Respect your hardware
- Just. Fucking. Work.

---

*"An OS-free desktop isn't about replacing your OS. It's about transcending it."*

*The Magic Launcher Paradigm - build it for fun, build it simply, build it to solve.*