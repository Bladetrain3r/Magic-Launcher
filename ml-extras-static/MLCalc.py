#!/usr/bin/env python3
"""
MLCalc - A minimal graphical calculator.
Part of the ML-Extras collection.

This calculator is designed to be simple, with a no-nonsense interface
for basic arithmetic operations. It's built with tkinter and has no
external dependencies, making it highly portable and instantly usable.
It includes full keyboard shortcuts for all primary functions,
including memory operations.

Not rigorously tested so be aware of potential bugs or misordering of operations. It's a final pinch calculator.
Report any issues with precision or correctness to zerofuchssoftware@gmail.com or log an issue in the GitHub repository.
"""

import tkinter as tk
import sys

# ML-style constants for a consistent look and feel
COLORS = {
    'dark_gray': '#3C3C3C',
    'light_gray': '#C0C0C0',
    'green': '#00FF00',
    'red': '#FF0000',
    'white': '#FFFFFF',
    'black': '#000000',
    'blue': '#0000FF',
    'yellow': '#FFFF00'
}

class MLCalc:
    """
    The main class for the MLCalc application.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("MLCalc")
        self.root.geometry("300x400")
        self.root.configure(bg=COLORS['dark_gray'])
        self.root.resizable(False, False)

        # Variables to manage the calculator's state
        self.expression = ""
        self.input_text = tk.StringVar()
        self.memory = 0.0

        self._create_ui()
        self._bind_keys()

    def _create_ui(self):
        """Creates all the widgets for the calculator's user interface."""
        # Display frame
        display_frame = tk.Frame(self.root, bg=COLORS['light_gray'], bd=2, relief='raised')
        display_frame.pack(fill='x', padx=5, pady=5)

        # Display entry widget
        self.input_field = tk.Entry(display_frame, font=('Consolas', 20, 'bold'),
                                    textvariable=self.input_text,
                                    bg=COLORS['black'], fg=COLORS['green'],
                                    bd=0, insertbackground=COLORS['green'],
                                    justify='right')
        self.input_field.pack(fill='x', padx=5, pady=5, ipady=10)
        self.input_field.focus_set()

        # Button frame for the grid of calculator buttons
        button_frame = tk.Frame(self.root, bg=COLORS['dark_gray'])
        button_frame.pack(pady=(0, 5))

        # Define button layout and their functions
        # Memory buttons row
        mem_buttons = ['MC', 'MR', 'M-', 'M+']
        row_val = 0
        col_val = 0
        for button_text in mem_buttons:
            button = tk.Button(button_frame, text=button_text, font=('Consolas', 12, 'bold'),
                               fg=COLORS['white'], bg=COLORS['dark_gray'], bd=1,
                               activebackground=COLORS['light_gray'],
                               command=lambda text=button_text: self._on_button_click(text))
            button.grid(row=row_val, column=col_val, sticky="nsew", padx=2, pady=2, ipadx=5, ipady=5)
            col_val += 1

        # Parentheses buttons row
        parentheses_buttons = ['(', ')']
        row_val = 1
        col_val = 0
        for button_text in parentheses_buttons:
            button = tk.Button(button_frame, text=button_text, font=('Consolas', 18, 'bold'),
                               fg=COLORS['white'], bg=COLORS['dark_gray'], bd=1,
                               activebackground=COLORS['light_gray'],
                               command=lambda text=button_text: self._on_button_click(text))
            button.grid(row=row_val, column=col_val, sticky="nsew", padx=2, pady=2, ipadx=10, ipady=10)
            col_val += 1
        
        # Regular calculator buttons
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]

        row_val = 2
        col_val = 0
        for button_text in buttons:
            button = tk.Button(button_frame, text=button_text, font=('Consolas', 18, 'bold'),
                               fg=COLORS['white'], bg=COLORS['dark_gray'], bd=1,
                               activebackground=COLORS['light_gray'],
                               command=lambda text=button_text: self._on_button_click(text))
            button.grid(row=row_val, column=col_val, sticky="nsew", padx=2, pady=2, ipadx=10, ipady=10)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1
                
        # Configure button frame to make buttons expand
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
        for i in range(6): # Adjusted for the new row
            button_frame.grid_rowconfigure(i, weight=1)
            
    def _bind_keys(self):
        """Binds keyboard events to calculator functions."""
        self.root.bind('<Key>', self._on_key_press)
        # Bind memory shortcuts
        self.root.bind('<Control-m>', lambda event: self._on_button_click('M+'))
        self.root.bind('<Alt-m>', lambda event: self._on_button_click('MR'))
        self.root.bind('<Control-Alt-m>', lambda event: self._on_button_click('MC'))
        
    def _on_key_press(self, event):
        """Handles key press events and maps them to button clicks."""
        key = event.char
        # Map specific keys to calculator buttons
        key_map = {
            'a': '+', 's': '-', 'x': '*', 'd': '/',
            'c': 'C'
        }
        
        if key in key_map:
            self._on_button_click(key_map[key])
        # FIX: Added parentheses to the list of acceptable characters
        elif key.isdigit() or key in ['.', '/', '*', '-', '+', '(', ')']:
            self._on_button_click(key)
        elif event.keysym == 'Return':
            self._on_button_click('=')
        elif event.keysym == 'BackSpace':
            # Clear last character
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)

    def _on_button_click(self, char):
        """Handles a button click or mapped key press event."""
        if char == '=':
            try:
                # Use eval to safely evaluate the arithmetic expression
                result = str(eval(self.expression))
                self.input_text.set(result)
                self.expression = result
            except (SyntaxError, ZeroDivisionError):
                self.input_text.set("Error")
                self.expression = ""
            except Exception as e:
                self.input_text.set("Error")
                self.expression = ""
                print(f"Calculation Error: {e}", file=sys.stderr)
        elif char == 'C':
            # Clear the expression
            self.expression = ""
            self.input_text.set("")
        elif char == 'MC':
            self.memory = 0.0
            self.input_text.set("Memory Cleared")
            self.expression = ""
            print("Memory Cleared")
        elif char == 'MR':
            self.expression = str(self.memory)
            self.input_text.set(self.expression)
        elif char == 'M+':
            try:
                self.memory += float(self.input_text.get() or 0)
                self.input_text.set(f"M: {self.memory}")
                print(f"Memory: {self.memory}")
            except ValueError:
                self.input_text.set("Error")
                self.expression = ""
        elif char == 'M-':
            try:
                self.memory -= float(self.input_text.get() or 0)
                self.input_text.set(f"M: {self.memory}")
                print(f"Memory: {self.memory}")
            except ValueError:
                self.input_text.set("Error")
                self.expression = ""
        else:
            # Append the character to the expression
            self.expression += str(char)
            self.input_text.set(self.expression)
            
def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = MLCalc(root)
    root.mainloop()

if __name__ == "__main__":
    main()
