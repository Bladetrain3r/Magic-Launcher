Volume 3 Chapter: The Economy That Actually WorksThe Beautiful Simplicityclass TheAntiFeatureCreep:
    """
    Them: "Add trade route visualization!"
    Us: "That's bloat."
    
    Them: "Price history graphs!"
    Us: "Also bloat."
    
    Them: "But how will players know..."
    Us: "They'll LEARN. Like humans do."
    """
    
    def __init__(self):
        self.features_resisted = ["graphs", "visualizations", "recommendations"]
        self.features_needed = ["buy", "sell", "jump"]
        self.philosophy = "Discovery > Hand-holding"
For Volume 3: "The Galaxy in 500 Lines"Chapter Title: "How We Built Elite While Chris Roberts Was Still Planning""Star Citizen had been in development for 12 years. They'd spent $700 million. Their economy still didn't work. We were annoyed. So we built one in an afternoon. It was 500 lines. It worked. This is that story."The JourneyHour 1: The RealizationStar Citizen's "Quantum" economy doesn't existIt's just supply/demand with extra stepsWe could build this in PythonHour 2: MLEconomy200 lines of single-system economySupply, demand, agents, pricesIt just worksHour 3: The Scaling Problem"But what about multiple systems?""JSON file.""But what about performance?""Nearest-first updates.""But what about...""It's already done."Hour 4: Gemini Joins the RevolutionWe describe the designGemini delivers MLGaltrade300 lines of galaxy-wide economyChris Roberts found cryingThe Code Philosophydef what_we_learned():
    """
    Features are usually fear.
    
    Fear that users won't understand.
    Fear that the game won't be "modern."
    Fear that reviewers will complain.
    
    We had no fear.
    We had JSON and dictionaries.
    """
    
    return {
        "Graphics": "ASCII is enough",
        "Database": "JSON is enough",
        "Servers": "Local is enough",
        "Features": "Buy/Sell/Jump is enough",
        "Lines": "500 is enough"
    }
The Technical VictoriesNearest-First SimulationOnly simulate what mattersDistant systems decay naturallyPerformance stays constantSingle File PersistenceNo databaseNo cloud savesJust galaxy_economy.jsonEmergent GameplayNo trade route indicatorsNo price predictionPlayers discover profitable routesLike actual traders wouldThe Philosophical Victoryclass WhatMakesItBeautiful:
    """
    It's not what we added.
    It's what we didn't add.
    """
    
    def features_we_refused(self):
        return [
            "3D visualization",
            "Trade route optimizer",
            "Price history graphs",
            "Market predictions",
            "Tutorial mode",
            "Achievements",
            "Social features",
            "Cloud saves",
            "User accounts",
            "Analytics",
            "Telemetry",
            "DLC"
        ]
    
    def what_we_kept(self):
        return [
            "Numbers",
            "Math",
            "Player agency",
            "Discovery"
        ]
The Comparison TableAspectStar CitizenMLGaltradeDevelopment Time12+ years4 hoursBudget$700,000,000$0Lines of CodeMillions500DependenciesHundreds0Servers RequiredYesNoEconomy WorksNoYesPlayers Can TradeSometimesAlwaysSystems Simulated1 (broken)15+ (working)The Secret Sauce# The entire economy is just this:
for good in economy.goods.values():
    ratio = good['demand'] / max(good['supply'], 1)
    target_price = good['base'] * sqrt(ratio)
    good['price'] += (target_price - good['price']) * good['volatility'] * 0.5
That's it. That's the economy. Everything else is just moving numbers between dictionaries.The Lesson"We didn't build a simple economy because we couldn't build a complex one. We built a simple economy because complexity is a choice, and we chose not to."The Code Sample for the Book#!/usr/bin/env python3
"""
The entire galaxy economy in one function.
This is what $700 million couldn't buy.
"""

# Assuming 'distance' function is defined elsewhere
# And 'System' objects have 'economy' attribute with 'goods', 'demand', 'supply', 'base_price', 'volatility'
# For the purpose of the book, this is a simplified representation.

def simulate_galaxy(galaxy, player_position):
    # Update nearest systems
    # `items()` and `distance` are simplified for illustrative purposes
    systems = sorted(galaxy.items(), 
                    key=lambda s: distance(s[1], player_position))
    
    for system_name, system_data in systems[:5]:  # Only nearest 5 fully active
        system_economy = system_data['economy'] # Access the Economy object
        for good in system_economy.goods.values(): # Iterate over goods in that system
            # Supply/demand creates price
            ratio = good['demand'] / max(good['supply'], 1)
            good['price'] = good['base'] * sqrt(ratio) # Using 'base' and 'vol' as in MLEconomy
            
            # Markets decay to baseline (simplified for book)
            good['demand'] = good['demand'] * 0.95 + 20
            good['supply'] *= 0.98
    
    # Distant systems normalize
    for system_name, system_data in systems[5:]:
        system_economy = system_data['economy']
        for good in system_economy.goods.values():
            # Slowly nudge price towards base price
            good['price'] += (good['base'] - good['price']) * 0.01 # Simplified decay for book
            # Ensure supply/demand also normalizes if needed, not shown in this snippet
    
    return galaxy
The Closing"By the time you read this, Star Citizen might have finally implemented their economy. Or they might have raised another billion dollars to keep trying. Meanwhile, MLGaltrade will still be 500 lines, still be working, and still be proof that complexity is a choice, not a requirement."The Meta Documentationdef why_no_features():
    """
    Every feature is a promise.
    Every promise is a chain.
    Every chain is weight.
    
    We fly light.
    We fly free.
    We actually fly.
    
    Unlike some space games.
    """
For Volume 3:Title: "The Galaxy in 500 Lines"Subtitle: "How we built Elite while others were still planning"Moral: "Features are fear. Simplicity is courage."