#!/usr/bin/env/python3
"""
Simple Snake game for terminal - included with Magic Launcher
Controls: WASD or Arrow Keys, Q to quit
"""

import curses
import random
import time
from collections import deque

class SnakeGame:
    def __init__(self):
        self.score = 0
        self.game_over = False
        
    def run(self, stdscr):
        # Setup
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(100)  # Game speed (ms)
        
        # Colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Score
        
        # Game dimensions
        height, width = stdscr.getmaxyx()
        game_height = height - 4  # Leave room for score/border
        game_width = width - 2
        
        # Initial snake
        start_y = game_height // 2
        start_x = game_width // 4
        snake = deque([(start_y, start_x), (start_y, start_x-1), (start_y, start_x-2)])
        direction = (0, 1)  # Moving right
        
        # First food
        food = self.place_food(snake, game_height, game_width)
        
        while not self.game_over:
            # Draw border
            stdscr.clear()
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(0, 0, "═" * width)
            stdscr.addstr(game_height + 1, 0, "═" * width)
            for y in range(1, game_height + 1):
                stdscr.addstr(y, 0, "║")
                stdscr.addstr(y, width - 1, "║")
            
            # Draw score
            stdscr.addstr(game_height + 2, 2, f"Score: {self.score}")
            stdscr.addstr(game_height + 2, width - 20, "Q: Quit, WASD: Move")
            stdscr.attroff(curses.color_pair(3))
            
            # Get input
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('w') or key == curses.KEY_UP:
                if direction != (1, 0):  # Can't go back on yourself
                    direction = (-1, 0)
            elif key == ord('s') or key == curses.KEY_DOWN:
                if direction != (-1, 0):
                    direction = (1, 0)
            elif key == ord('a') or key == curses.KEY_LEFT:
                if direction != (0, 1):
                    direction = (0, -1)
            elif key == ord('d') or key == curses.KEY_RIGHT:
                if direction != (0, -1):
                    direction = (0, 1)
            
            # Move snake
            head = snake[0]
            new_head = (head[0] + direction[0], head[1] + direction[1])
            
            # Check collisions
            if (new_head[0] <= 0 or new_head[0] >= game_height + 1 or
                new_head[1] <= 0 or new_head[1] >= width - 1 or
                new_head in snake):
                self.game_over = True
                break
            
            snake.appendleft(new_head)
            
            # Check food
            if new_head == food:
                self.score += 10
                food = self.place_food(snake, game_height, game_width)
                # Snake grows (don't remove tail)
            else:
                snake.pop()  # Remove tail
            
            # Draw snake
            stdscr.attron(curses.color_pair(1))
            for segment in snake:
                stdscr.addstr(segment[0], segment[1], "█")
            stdscr.attroff(curses.color_pair(1))
            
            # Draw food
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(food[0], food[1], "●")
            stdscr.attroff(curses.color_pair(2))
            
            stdscr.refresh()
        
        # Game over screen
        stdscr.clear()
        msg = "GAME OVER!"
        score_msg = f"Final Score: {self.score}"
        cont_msg = "Press any key to exit..."
        
        height, width = stdscr.getmaxyx()
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(height//2 - 2, (width - len(msg))//2, msg)
        stdscr.attroff(curses.color_pair(2))
        
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height//2, (width - len(score_msg))//2, score_msg)
        stdscr.addstr(height//2 + 2, (width - len(cont_msg))//2, cont_msg)
        stdscr.attroff(curses.color_pair(3))
        
        stdscr.nodelay(False)
        stdscr.getch()
    
    def place_food(self, snake, height, width):
        while True:
            y = random.randint(1, height)
            x = random.randint(1, width - 2)
            if (y, x) not in snake:
                return (y, x)


def main():
    try:
        game = SnakeGame()
        curses.wrapper(game.run)
    except KeyboardInterrupt:
        pass
    
    print(f"\nThanks for playing! Final score: {game.score}")
    print("Magic Launcher - Simple tools for simple times")


if __name__ == "__main__":
    main()