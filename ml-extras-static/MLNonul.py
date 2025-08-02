#!/usr/bin/env python3
"""
MLNonul.py - A text file normalizer for the ML-Extras toolkit.

This script processes a single text file in-place, performing several crucial
cleanup operations to ensure it's compatible with standard Unix-style tools
and other ML-Extras utilities.

It performs the following:
1. Strips all null characters ('\x00').
2. Converts DOS-style line endings ('\r\n') to Unix-style ('\n').
3. Ensures the final file is encoded in UTF-8.

The script is designed to be lightweight, have no external dependencies,
and provide a clean exit code for use in automated scripts and pipelines.
"""

import sys
import os

def process_file(filepath):
    """
    Processes the specified file, performing normalization in place.
    
    Args:
        filepath (str): The path to the file to be processed.
        
    Returns:
        bool: True if the file was processed successfully, False otherwise.
    """
    try:
        # Read the file in binary mode to handle null bytes correctly
        with open(filepath, 'rb') as f:
            raw_data = f.read()

        # Decode the binary data to a string. We use 'errors=ignore' to
        # gracefully handle any non-UTF-8 bytes, which is a safe default
        # for a "cleanup" tool.
        content = raw_data.decode('utf-8', errors='ignore')

        # 1. Strip null characters. These are often remnants of memory dumps or
        #    corrupted files and can cause issues with many tools.
        content = content.replace('\x00', '')
        
        # 2. Normalize line endings. Replace DOS-style with Unix-style.
        #    This is a common requirement for tools like grep, sed, and awk.
        content = content.replace('\r\n', '\n')
        
        # 3. Write the cleaned content back to the file with UTF-8 encoding.
        #    This ensures a consistent and predictable output format.
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Successfully processed and normalized: {filepath}")
        return True
        
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'.", file=sys.stderr)
    except IOError as e:
        print(f"Error: Could not read or write to file '{filepath}'. Details: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

    return False

def main():
    """Main function to handle command-line arguments and script execution."""
    
    # Check for the correct number of command-line arguments
    if len(sys.argv) != 2:
        print("MLNonul - Text File Normalizer")
        print(f"Usage: {os.path.basename(sys.argv[0])} <filepath>")
        print("\nDescription:")
        print("Strips null characters, normalizes line endings, and re-encodes a file to UTF-8.")
        sys.exit(1) # Exit with a non-zero code for incorrect usage

    # Get the file path from the command-line arguments
    filepath = sys.argv[1]
    
    # Process the file and set the exit code based on the result
    if process_file(filepath):
        sys.exit(0) # Success
    else:
        sys.exit(1) # Failure

if __name__ == "__main__":
    main()

# A single, simple task. No frameworks, no dependencies, just a tool that works.
# This isn't about building a monolith, but about making tiny, useful things.
# Code zen achieved.
