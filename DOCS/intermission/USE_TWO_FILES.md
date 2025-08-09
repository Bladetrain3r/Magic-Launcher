# Addendum to the Magic Launcher Philosophy

## The Two-File Rule

**"When two files work best, use two files. Most rules are negotiable by necessity."**

### The Context

We just discovered this splitting MLLatinum. The HTML was becoming a mess with 500+ vocabulary words jammed inline. The solution was obvious: HTML for display, JSON for data.

This violates our "single file deployment" principle. And that's fine.

### Why This Matters

The Magic Launcher philosophy isn't dogma. It's pragmatism. When we say "one file," we mean "don't split into 47 modules for no reason." But when you have:

- Display logic (HTML/JS)
- Data (vocabulary)

These are fundamentally different concerns. Mixing them creates the exact hostile architecture we're fighting.

### The Test

Ask yourself:
1. **Would I edit these separately?** (HTML styling vs vocabulary additions)
2. **Do they change at different rates?** (UI rarely, vocabulary often)
3. **Could they be reused independently?** (Same vocab, different UI)

If yes to any: split them.

### Examples Where Two Files Win

**Good Splits:**
- `mllatinum.html` + `mllatinum-lang.json` - UI vs data
- `launcher.py` + `shortcuts.json` - Code vs configuration  
- `game.html` + `levels.json` - Engine vs content

**Bad Splits (Enterprise Theater):**
- `UserController.js` + `UserService.js` + `UserRepository.js` - Same fucking purpose
- `styles.css` + `colors.css` + `fonts.css` - Just write CSS
- `config.yml` + `config.prod.yml` + `config.dev.yml` - You have one environment: the one running

### The Negotiable Part

"Most rules are negotiable by necessity" means:
- **200-line limit?** MLLatinum.py is 500 lines because vocabulary is data, not code
- **No dependencies?** PIL for images because image decoding is genuinely hard
- **Single file?** Two files when one would be hostile to maintenance

But negotiate from necessity, not convenience. Every exception needs a reason that would satisfy someone maintaining this at 3 AM.

### The Anti-Pattern We're Avoiding

This is NOT permission for:
```
src/
  components/
    translator/
      TranslatorComponent.js
      TranslatorStyles.css
      TranslatorTypes.ts
      TranslatorContext.js
      TranslatorReducer.js
      TranslatorActions.js
      TranslatorConstants.js
```

That's seven files for what should be one component. That's enterprise theater.

### The Pattern We're Embracing

```
mllatinum.html     # Everything about display
mllatinum-lang.json # Everything about language
```

Two files. Clear boundary. Edit one without breaking the other.

### When to Break the Rules

Break a rule when following it would create the complexity we're fighting against. 

- Single file becoming unreadable? Split it.
- Reimplementing something hard? Add a dependency.
- 200 lines not enough? Use what you need.

But always ask: "Am I breaking this rule to solve a real problem, or because I'm used to enterprise patterns?"

### The Philosophical Point

Magic Launcher isn't about rigid adherence to rules. It's about:
1. Starting simple
2. Adding complexity only when forced
3. Recognizing when you're forced
4. Not adding complexity preemptively

### The Final Test

If someone asks "Why two files?" you should have an answer that isn't:
- "Best practices"
- "Separation of concerns"  
- "Future flexibility"
- "Industry standard"

Your answer should be: "Because editing vocabulary shouldn't require scrolling through HTML."

That's a real reason. That's necessity.

---

*Rules exist to prevent complexity. When rules create complexity, break the rules.*

*Two files that work > One file that fights you.*

*Magic Launcher: Pragmatic enough to break its own rules.*