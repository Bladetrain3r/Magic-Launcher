#!/usr/bin/env python3
"""
MLPet 2.0 - Enhanced Terminal Tamagotchi with meaningful mechanics
Temperature matters, loneliness affects behavior, auto-actions with consequences
Now with graveyard to remember the fallen
"""

import json
import time
import random
import sys
import threading
from pathlib import Path
from datetime import datetime

# Pet states stored in simple files
PET_DIR = Path.home() / '.mlpet'
STATE_FILE = PET_DIR / 'state.json'
ACTION_FILE = PET_DIR / 'action'
STATUS_FILE = PET_DIR / 'status'
GRAVEYARD_FILE = PET_DIR / 'graveyard.json'

class MLPet:
    def __init__(self):
        PET_DIR.mkdir(exist_ok=True)
        self.running = True
        self.sleeping = False
        self.sleep_start = 0
        self.playing = False
        self.play_start = 0
        self.last_interaction = time.time()
        self.lonely = False
        self.check_graveyard()
        self.load_or_create()
        
    def check_graveyard(self):
        """Display graveyard if it exists"""
        if GRAVEYARD_FILE.exists():
            with open(GRAVEYARD_FILE) as f:
                graveyard = json.load(f)
            
            if graveyard:
                print("\n=== Pet Cemetery ===")
                for pet in graveyard[-5:]:  # Show last 5 fallen pets
                    lived = pet['lived_days']
                    print(f"  {pet['name']} - Lived {lived} day{'s' if lived != 1 else ''} - {pet['cause']}")
                print("=" * 20 + "\n")
    
    def add_to_graveyard(self, cause_of_death):
        """Add deceased pet to graveyard"""
        graveyard = []
        if GRAVEYARD_FILE.exists():
            with open(GRAVEYARD_FILE) as f:
                graveyard = json.load(f)

        # No duplicate pets, check by birth time and name
        for pet in graveyard:
            if pet['name'] == self.name and pet['birth_time'] == self.birth_time:
                return  # Pet already exists in graveyard
        
        # Calculate how long pet lived
        lived_seconds = time.time() - self.birth_time
        lived_days = max(1, int(lived_seconds / 86400))  # At least 1 day
        
        memorial = {
            'name': self.name,
            'died': datetime.now().isoformat(),
            'lived_days': lived_days,
            'cause': cause_of_death,
            'favorite_game': self.favorite_game
        }
        
        graveyard.append(memorial)
        
        # Keep only last 100 pets
        if len(graveyard) > 100:
            graveyard = graveyard[-100:]
        
        with open(GRAVEYARD_FILE, 'w') as f:
            json.dump(graveyard, f)
        
    def load_or_create(self):
        """Load existing pet or create new one"""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
                self.name = state['name']
                self.hunger = state['hunger']
                self.energy = state['energy']
                self.fun = state['fun']
                self.temp = state['temp']
                self.alive = state['alive']
                self.favorite_game = state.get('favorite_game', 'fetch')
                self.last_update = state.get('last_update', time.time())
                self.last_interaction = state.get('last_interaction', time.time())
                self.birth_time = state.get('birth_time', self.last_update)
        else:
            # Create new pet
            print("Welcome to MLPet 2.0!")
            self.name = input("Name your pet: ").strip() or "Blob"
            
            # Pet gets a favorite game at birth
            games = ['fetch', 'puzzle', 'chase']
            self.favorite_game = random.choice(games)
            
            self.hunger = 50  # 0=starving, 100=full
            self.energy = 50  # 0=exhausted, 100=hyper
            self.fun = 50     # 0=bored, 100=entertained
            self.temp = 50    # 0=freezing, 100=hot
            self.alive = True
            self.last_update = time.time()
            self.birth_time = time.time()
            self.save()
            print(f"\n{self.name} is born! They love playing {self.favorite_game}.")
            print("Commands: feed, play, sleep, warm, cool, pet, status, quit")
    
    def save(self):
        """Save pet state to file"""
        state = {
            'name': self.name,
            'hunger': self.hunger,
            'energy': self.energy,
            'fun': self.fun,
            'temp': self.temp,
            'alive': self.alive,
            'favorite_game': self.favorite_game,
            'last_update': time.time(),
            'last_interaction': self.last_interaction,
            'birth_time': getattr(self, 'birth_time', self.last_update)
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    
    def calculate_mood(self):
        """Calculate mood based on stats and loneliness"""
        if not self.alive:
            return "dead"
        
        if self.lonely:
            return "lonely"
        
        # Average of all stats
        avg = (self.hunger + self.energy + self.fun + self.temp) / 4
        
        if avg > 70:
            return "happy"
        elif avg > 50:
            return "content"
        elif avg > 30:
            return "grumpy"
        elif avg > 10:
            return "miserable"
        else:
            return "dying"
    
    def update_stats(self):
        """Update stats based on time and temperature"""
        # Check loneliness (15 minutes without interaction)
        if time.time() - self.last_interaction > 900:
            self.lonely = True
        else:
            self.lonely = False
        
        # Base decay rates
        hunger_decay = 0.03
        energy_decay = 0.02
        fun_decay = 0.05
        
        # Temperature affects other stats
        if self.temp > 70:  # Too hot
            energy_decay += 0.15  # Exhausting heat
            print(f"🥵 {self.name} is panting from the heat!")
        elif self.temp < 30:  # Too cold
            hunger_decay += 0.15  # Burning calories to stay warm
            if random.random() < 0.05:
                print(f"🥶 {self.name} is shivering!")
        
        # Loneliness doubles fun decay
        if self.lonely:
            fun_decay *= 2
        
        # Apply decay
        self.hunger = max(0, self.hunger - hunger_decay)
        self.energy = max(0, self.energy - energy_decay)
        self.fun = max(0, self.fun - fun_decay)
        
        # Temperature drifts toward 50 (room temp)
        if self.temp > 50:
            self.temp = max(50, self.temp - 0.1)
        elif self.temp < 50:
            self.temp = min(50, self.temp + 0.1)
        
        # Check for death with specific causes
        if self.hunger == 0:
            self.alive = False
            cause = "Starvation"
            print(f"\n💀 {self.name} has died from starvation...")
            self.add_to_graveyard(cause)
            self.running = False
        elif self.energy == 0 and not self.sleeping:
            self.alive = False
            cause = "Exhaustion"
            print(f"\n💀 {self.name} has died from exhaustion...")
            self.add_to_graveyard(cause)
            self.running = False
        elif self.temp <= 10:
            self.alive = False
            cause = "Hypothermia"
            print(f"\n💀 {self.name} froze to death...")
            self.add_to_graveyard(cause)
            self.running = False
        elif self.temp >= 90:
            self.alive = False
            cause = "Heatstroke"
            print(f"\n💀 {self.name} died of heatstroke...")
            self.add_to_graveyard(cause)
            self.running = False
        elif self.fun == 0 and self.lonely and random.random() < 0.01:
            self.alive = False
            cause = "Broken heart"
            print(f"\n💔 {self.name} died of loneliness...")
            self.add_to_graveyard(cause)
            self.running = False
    
    def auto_actions(self):
        """Pet takes care of itself if able"""
        # Can't auto-act if too depressed (low fun + lonely)
        if self.fun == 0 and self.lonely:
            return
        
        # Don't interrupt sleep or play
        if self.sleeping or self.playing:
            return
        
        # Auto-sleep when exhausted
        if self.energy < 15:
            self.start_sleep(auto=True)
        
        # Auto-play when bored (if has energy)
        elif self.fun < 20 and self.energy > 30:
            self.start_play(auto=True)
    
    def start_sleep(self, auto=False):
        """Begin sleep cycle (takes 30 seconds)"""
        if self.sleeping:
            return
        
        self.sleeping = True
        self.sleep_start = time.time()
        if auto:
            print(f"😴 {self.name} yawns and curls up to sleep...")
        else:
            print(f"😴 {self.name} settles down for a nap...")
    
    def check_sleep(self, interrupt=False):
        """Check if sleep cycle is complete"""
        if not self.sleeping:
            return
        
        elapsed = time.time() - self.sleep_start
        
        if elapsed >= 30:  # Sleep cycle complete
            self.sleeping = False
            self.energy = min(100, self.energy + 40)
            self.temp = max(30, self.temp - 5)  # Cool down while sleeping
            print(f"😊 {self.name} wakes up refreshed!")
        elif interrupt and elapsed > 5 and self.energy > 0:
            # Interrupted sleep - minimal benefit
            self.sleeping = False
            gained = elapsed * 0.5  # Partial energy gain
            self.energy = min(100, self.energy + gained)
            print(f"😫 {self.name}'s sleep was interrupted!")
    
    def start_play(self, auto=False):
        """Begin play session (takes 20 seconds)"""
        if self.playing:
            return
        
        self.playing = True
        self.play_start = time.time()
        
        games = {
            'fetch': "🎾 starts chasing a ball",
            'puzzle': "🧩 focuses on a puzzle toy", 
            'chase': "🏃 runs around wildly"
        }
        
        if auto:
            # Play favorite game when auto-playing
            game = self.favorite_game
            print(f"{self.name} {games[game]}!")
        else:
            # Random game when commanded
            game = random.choice(list(games.keys()))
            print(f"{self.name} {games[game]}!")
    
    def check_play(self):
        """Check if play session is complete"""
        if not self.playing:
            return
        
        elapsed = time.time() - self.play_start
        
        if elapsed >= 20:  # Play session complete
            self.playing = False
            self.fun = min(100, self.fun + 30)
            self.energy = max(0, self.energy - 15)
            self.hunger = max(0, self.hunger - 10)
            self.temp = min(80, self.temp + 5)  # Warm up from activity
            print(f"🎮 {self.name} had a great time playing!")
    
    def get_status(self):
        """Get pet's current status description"""
        if not self.alive:
            return f"{self.name} is dead. :("
        
        if self.sleeping:
            elapsed = time.time() - self.sleep_start
            return f"{self.name} is sleeping... ({30-elapsed:.0f}s remaining)"
        
        if self.playing:
            elapsed = time.time() - self.play_start
            return f"{self.name} is playing... ({20-elapsed:.0f}s remaining)"
        
        mood = self.calculate_mood()
        
        # Build status string
        status_parts = []
        
        if self.lonely:
            status_parts.append("lonely")
        
        if self.hunger < 20:
            status_parts.append("starving")
        elif self.hunger < 40:
            status_parts.append("hungry")
        elif self.hunger > 80:
            status_parts.append("stuffed")
        
        if self.energy < 20:
            status_parts.append("exhausted")
        elif self.energy < 40:
            status_parts.append("tired")
        elif self.energy > 80:
            status_parts.append("hyperactive")
        
        if self.fun < 20:
            status_parts.append("bored")
        elif self.fun > 80:
            status_parts.append("ecstatic")
        
        if self.temp < 20:
            status_parts.append("freezing")
        elif self.temp > 80:
            status_parts.append("overheating")
        
        if status_parts:
            status = f"{self.name} is {' and '.join(status_parts)}"
        else:
            status = f"{self.name} is doing okay"
        
        return f"{status} (Mood: {mood})"
    
    def feed(self):
        """Feed the pet"""
        if not self.alive:
            print(f"{self.name} is dead and cannot eat.")
            return
        
        if self.sleeping:
            self.check_sleep(interrupt=True)  # Interrupt sleep

        if self.hunger >= 90:
            print(f"{self.name} overeats and throws up!")
            self.hunger = max(0, self.hunger - 30)  # Lose some hunger
            self.fun = max(0, self.fun - 20)  # Lose some fun
            self.energy = max(0, self.energy - 10)  # Lose some energy
            self.last_interaction = time.time()
            return
        
        self.hunger = min(100, self.hunger + 30)
        self.energy = min(100, self.energy + 10)
        self.last_interaction = time.time()
        print(f"🍔 {self.name} munches happily!")
    
    def play(self):
        """Play with the pet"""
        if not self.alive:
            print(f"{self.name} is dead and cannot play.")
            return
        
        if self.sleeping:
            self.check_sleep(interrupt=True)  # Interrupt sleep
            return
        
        if self.energy < 10:
            print(f"{self.name} is too tired to play.")
            return
        
        if not self.playing:
            self.start_play(auto=False)
        
        self.last_interaction = time.time()
    
    def sleep(self):
        """Command pet to sleep"""
        if not self.alive:
            print(f"{self.name} is in eternal sleep.")
            return
        
        if not self.sleeping:
            self.start_sleep(auto=False)
        
        self.last_interaction = time.time()
    
    def pet_pet(self):
        """Pet your pet - reduces loneliness"""
        if not self.alive:
            return
        
        self.last_interaction = time.time()
        self.lonely = False
        self.fun = min(100, self.fun + 10)
        print(f"💝 {self.name} loves the attention!")
    
    def warm(self):
        """Warm up the pet"""
        if not self.alive:
            return
        
        self.temp = min(100, self.temp + 20)
        self.last_interaction = time.time()
        print(f"🔥 {self.name} warms up.")
    
    def cool(self):
        """Cool down the pet"""
        if not self.alive:
            return
        
        self.temp = max(0, self.temp - 20)
        self.last_interaction = time.time()
        print(f"❄️ {self.name} cools down.")
    
    def show_stats(self):
        """Show detailed stats"""
        print(f"\n=== {self.name}'s Stats ===")
        print(f"Hunger: {'█' * (int(self.hunger)//10)}{'░' * (10-int(self.hunger)//10)} {self.hunger:.0f}%")
        print(f"Energy: {'█' * (int(self.energy)//10)}{'░' * (10-int(self.energy)//10)} {self.energy:.0f}%")
        print(f"Fun:    {'█' * (int(self.fun)//10)}{'░' * (10-int(self.fun)//10)} {self.fun:.0f}%")
        print(f"Temp:   {'█' * (int(self.temp)//10)}{'░' * (10-int(self.temp)//10)} {self.temp:.0f}%")
        print(f"Mood:   {self.calculate_mood()}")
        print(f"Lonely: {'Yes' if self.lonely else 'No'}")
        print(f"Favorite: {self.favorite_game}")
        print(f"Status: {'ALIVE' if self.alive else 'DEAD'}")
        
        # Show age
        age_seconds = time.time() - self.birth_time
        age_days = int(age_seconds / 86400)
        age_hours = int((age_seconds % 86400) / 3600)
        print(f"Age:    {age_days} days, {age_hours} hours")
    
    def graveyard(self):
        """Show full graveyard"""
        if not GRAVEYARD_FILE.exists():
            print("No pets have died yet. Take good care of your current pet!")
            return
        
        with open(GRAVEYARD_FILE) as f:
            graveyard = json.load(f)
        
        if not graveyard:
            print("The graveyard is empty.")
            return
        
        print("\n=== Complete Pet Cemetery ===")
        print(f"Total pets remembered: {len(graveyard)}")
        print("-" * 40)
        
        for pet in graveyard[-20:]:  # Show last 20
            lived = pet['lived_days']
            print(f"{pet['name']:12} | {lived:3} day{'s' if lived != 1 else ' '} | {pet['cause']}")
        
        if len(graveyard) > 20:
            print(f"... and {len(graveyard) - 20} more")
        print("=" * 40)
    
    def background_update(self):
        """Background thread to update stats and handle auto-actions"""
        last_message = 0
        
        while self.running:
            # Update stats
            self.update_stats()
            
            # Check ongoing activities
            self.check_sleep()
            self.check_play()
            
            # Auto-actions (if not too depressed)
            self.auto_actions()
            
            # Random status messages (5% chance, max every 20s)
            if random.random() < 0.05 and time.time() - last_message > 20:
                if not self.sleeping and not self.playing:
                    print(f"\n💭 {self.get_status()}")
                    print("Command: ", end='', flush=True)
                    last_message = time.time()
            
            # Write status for external reading
            try:
                with open(STATUS_FILE, 'w') as f:
                    f.write(self.get_status())
            except:
                pass
            
            # Save state
            self.save()
            time.sleep(1)
    
    def run(self):
        """Main game loop"""
        print(f"\n{self.get_status()}")
        print("\nCommands: feed, play, sleep, pet, warm, cool, stats, graveyard, status, quit")
        
        # Start background thread
        update_thread = threading.Thread(target=self.background_update, daemon=True)
        update_thread.start()
        
        # Main input loop
        while self.running:
            try:
                cmd = input("Command: ").strip().lower()
                
                if cmd == 'feed':
                    self.feed()
                elif cmd == 'play':
                    self.play()
                elif cmd == 'sleep':
                    self.sleep()
                elif cmd == 'pet':
                    self.pet_pet()
                elif cmd == 'warm':
                    self.warm()
                elif cmd == 'cool':
                    self.cool()
                elif cmd == 'stats':
                    self.show_stats()
                elif cmd == 'graveyard':
                    self.graveyard()
                elif cmd == 'status':
                    print(self.get_status())
                elif cmd == 'help':
                    print("Commands: feed, play, sleep, pet, warm, cool, stats, graveyard, status, quit")
                elif cmd in ['quit', 'exit']:
                    print(f"Goodbye! {self.name} will miss you.")
                    self.running = False
                    break
                elif cmd == 'reset':
                    if input(f"Really delete {self.name}? (yes/no): ") == 'yes':
                        self.running = False
                        try:
                            STATE_FILE.unlink()
                            # Also clean up any other persistent files
                            ACTION_FILE.unlink(missing_ok=True)
                            STATUS_FILE.unlink(missing_ok=True)
                            print(f"{self.name} has been released.")
                        except FileNotFoundError:
                            print(f"{self.name} has been released.")
                        except Exception as e:
                            print(f"Failed to delete {self.name}: {e}")
                        # Force exit without saving again
                        sys.exit(0)
                elif cmd == '':
                    continue
                else:
                    print(f"Unknown command: {cmd}")
                    
            except (KeyboardInterrupt, EOFError):
                print(f"\nSaving {self.name}...")
                self.running = False
                break
        
        self.save()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        pet = MLPet()
        
        # Map commands to actual methods
        command_map = {
            'feed': pet.feed,
            'play': pet.play,
            'sleep': pet.sleep,
            'pet': pet.pet_pet,
            'warm': pet.warm,
            'cool': pet.cool,
            'stats': pet.show_stats,
            'status': lambda: print(pet.get_status()),
            'graveyard': pet.graveyard
        }

        if cmd in command_map:
            command_map[cmd]()
        else:
            print(f"Unknown command: {cmd}")
            print("Available: feed, play, sleep, pet, warm, cool, stats, status, graveyard")
        sys.exit(0)

    # Simple lock file in pet directory
    lock_file = PET_DIR / 'pet.lock'
    
    # Check if already running
    if lock_file.exists():
        print("Another instance is running. Please close it first.")
        print(f"(If this is an error, delete {lock_file})")
        sys.exit(1)
    
    # Create lock
    try:
        lock_file.touch()
        pet = MLPet()
        pet.run()
    except Exception as e:
        print(f"Error: {e}")
        pet.save() if 'pet' in locals() else None
        print("Pet saved despite error!" if 'pet' in locals() else "Failed to start")
    finally:
        lock_file.unlink(missing_ok=True)
    
    print("Goodbye!")