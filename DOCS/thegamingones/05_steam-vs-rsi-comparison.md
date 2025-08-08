# Steam vs RSI Launcher: A Study in Necessary Complexity

## Or: How to Use 600MB of RAM to Do Nothing

### Executive Summary

The RSI Launcher uses more memory than Steam while providing approximately 1% of the functionality. This document examines why this is indefensible from an engineering perspective.

---

## The Raw Numbers

### Memory Usage (Actual Screenshots)

| Application | Idle Memory | Active Memory | Features Provided |
|------------|-------------|---------------|-------------------|
| **Steam** | ~232MB | ~582MB | Hundreds |
| **RSI Launcher** | ~600MB | ~613MB | Four (generously) |

### Process Breakdown

#### RSI Launcher Processes
```
RSI Launcher.exe - 7,972 KB
RSI Launcher.exe - 145,984 KB  
RSI Launcher.exe - 5,880 KB
RSI Launcher.exe - 4,608 KB
RSI Launcher.exe - 280,404 KB
RSI Launcher.exe - 169,096 KB
----------------------------
TOTAL: 613.9 MB
```

#### Steam Processes (Logged In)
```
steam.exe - 50 MB (main)
steamservice.exe - 8 MB
steamwebhelper.exe - 50 MB
steamwebhelper.exe - 32 MB
steamwebhelper.exe - 3.5 MB
steamwebhelper.exe - 97 MB
steamwebhelper.exe - 6 MB
steamwebhelper.exe - 12 MB
steamwebhelper.exe - 322 MB
----------------------------
TOTAL: 580.5 MB
```

---

## Feature Comparison

### Steam Features (Justified Complexity)

#### Core Gaming Platform
- **Store**: Browse and purchase from 50,000+ games
- **Library**: Manage hundreds/thousands of owned games
- **Downloads**: Queue management, bandwidth limiting, scheduling
- **Updates**: Automatic updates with delta patching that actually works

#### Community Features
- **Friends System**: Chat, voice, presence, groups
- **Community Hub**: Forums, guides, artwork, screenshots
- **Workshop**: Largest modding platform on the internet
- **Reviews**: User review system with helpful/funny ratings
- **Activity Feeds**: See what friends are playing/buying

#### Technical Features
- **Cloud Saves**: Automatic sync across devices
- **Family Sharing**: Share library with family members
- **Remote Play**: Stream games to other devices
- **Big Picture Mode**: TV/controller interface
- **VR Support**: Complete VR ecosystem management
- **Proton/Linux**: Windows game compatibility layer

#### Developer Features
- **Steamworks SDK**: Multiplayer, achievements, stats
- **Beta Branches**: Test builds management
- **Steam Input**: Universal controller configuration

#### Business Features
- **Trading Cards/Market**: Digital economy
- **Points Shop**: Rewards system
- **Sales Events**: Seasonal sales with minigames
- **Curator System**: Recommendation networks

**Memory per feature: ~2-3MB** (conservative estimate)

### RSI Launcher Features (Unjustified Complexity)

#### Core Features
- **Launch Game**: Starts Star Citizen (sometimes)
- **Update Game**: Downloads patches (minimum 4GB even for 3KB fixes)
- **Login**: Authentication (works mostly)
- **Settings**: Disable the bloat you don't want

#### Bloat Features
- **News Feed**: Articles nobody reads
- **Background Video**: CPU-melting decoration
- **Animations**: Sliding panels that add nothing
- **Marketing Content**: 4 tabs of "reactive" media updated bimonthly
- **Telemetry**: Analytics that apparently don't improve anything

**Memory per feature: ~150MB** (if we're being generous about counting features)

---

## The Purpose Test

### Steam's Purpose Alignment
```python
steam_purposes = {
    "Game Library Management": "✓ Excellent",
    "Game Discovery": "✓ Industry leading",
    "Social Gaming": "✓ Comprehensive", 
    "Mod Support": "✓ Largest platform",
    "Developer Tools": "✓ Full suite",
    "Digital Storefront": "✓ Market leader"
}
# Every MB of RAM serves multiple purposes
```

### RSI Launcher's Purpose Alignment
```python
rsi_purposes = {
    "Launch Star Citizen": "✓ Eventually",
    "Update Star Citizen": "⚠ Wastefully",
    "Look Pretty": "✗ Subjective and unnecessary",
    "Marketing": "✗ Wrong tool for the job",
    "News Delivery": "✗ Nobody asked for this"
}
# Most RAM serves no gameplay purpose
```

---

## The Engineering Analysis

### Why Steam's Complexity is Justified

1. **Multi-Purpose Tool**: Steam isn't just a launcher, it's a platform
2. **Feature Utilization**: Most users use most features
3. **Network Effects**: Each feature enhances others (friends + library + workshop)
4. **Business Model**: Features directly support revenue (store + community = sales)
5. **Scale**: Serving 120 million active users justifies optimization investment

### Why RSI Launcher's Complexity is Not Justified

1. **Single Purpose Tool**: Only needs to launch ONE game
2. **Feature Ignorance**: Most features are disabled by users
3. **No Synergy**: News doesn't enhance launching, videos don't improve updates
4. **Resource Competition**: Launcher RAM/CPU competes with the actual game
5. **Scale**: One game doesn't justify Electron overhead

---

## The Alternative Design

### What RSI Launcher Should Be

```python
class IdealRSILauncher:
    """
    Total code: ~500 lines
    Memory usage: ~30MB
    Features: Everything necessary
    """
    
    def __init__(self):
        self.game_path = find_game()
        self.verify_files()
    
    def launch(self):
        """The only required feature"""
        if needs_update():
            download_delta_patches()  # Not 4GB minimums
        subprocess.run([self.game_path])
    
    def settings(self):
        """The only UI needed"""
        return {
            "Install Location": self.game_path,
            "Check for Updates": True,
            "Close After Launch": True
        }

# That's it. That's the entire launcher.
```

### Memory Usage If Done Right

| Component | Memory | Purpose |
|-----------|--------|---------|
| Python/C++ Core | 20MB | Basic runtime |
| Update Checker | 5MB | Delta comparison |
| Simple GUI | 5MB | Native widgets, not web |
| **TOTAL** | **30MB** | **100% functional** |

---

## The Philosophical Divide

### Steam (Necessary Complexity)
> "Every feature must earn its memory cost through user value"

- Features are added based on user behavior data
- Features are removed if unused
- Memory optimization is ongoing
- Serves millions simultaneously

### RSI Launcher (Unnecessary Complexity)
> "We added it because we could"

- Features added for marketing/appearance
- Features never removed despite non-use
- Memory optimization ignored
- Serves one game that needs those resources

---

## The Verdict

| Metric | Steam | RSI Launcher | Winner |
|--------|-------|--------------|--------|
| Memory Usage | 580MB | 613MB | Steam |
| Features | Hundreds | <10 | Steam |
| Efficiency | ~2MB/feature | ~150MB/feature | Steam |
| Purpose Alignment | 100% | 20% | Steam |
| Update Efficiency | Delta patches | 4GB minimum | Steam |
| User Experience | Functional | Frustrating | Steam |

---

## Conclusion

The RSI Launcher is a perfect example of modern software dysfunction:

1. **Uses web technology** (Electron) for a desktop application
2. **Prioritizes appearance** over functionality
3. **Ignores resource constraints** that affect the actual game
4. **Solves no user problems** while creating several
5. **Costs more than better alternatives** in every metric

Steam proves that complexity CAN be justified when it serves user needs. The RSI Launcher proves that most complexity is just poor engineering decisions compounded by worse product decisions.

### The Final Comparison

```python
# Steam: Complex because it does complex things
steam = MultipurposePlatform(
    features=hundreds,
    users=millions,
    memory=580MB,
    justification="Each feature used by millions"
)

# RSI: Complex because nobody said no
rsi = SinglePurposeLauncher(
    features=4,
    users=thousands,
    memory=613MB,
    justification="Some people like RGB"
)
```

### The Magic Launcher Alternative

```bash
#!/bin/bash
# The entire RSI Launcher in 3 lines
check_for_updates && download_updates
cd /path/to/star/citizen
./StarCitizen.exe

# Memory usage: 0MB
# Features: 100% of what's needed
# User satisfaction: Higher than current
```

---

*"The RSI Launcher: Proof that you can use 600MB of RAM to accomplish what subprocess.run() does in zero."*

**Final Score: Steam 580MB for everything vs RSI 613MB for nothing**