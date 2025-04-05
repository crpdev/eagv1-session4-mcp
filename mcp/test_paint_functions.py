import sys
import os
import time

# Fix the import path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the fixed functions directly
from fixed_paint_functions import open_paint, draw_rectangle, add_text_in_paint

def main():
    print("Testing Paint functions...")
    
    # Open Paint
    print("Opening Paint...")
    if open_paint():
        print("Paint opened successfully")
        
        # Wait a moment to ensure Paint is fully loaded
        time.sleep(3)
        
        # Draw a large rectangle in the center of the screen
        print("Drawing rectangle...")
        # Using coordinates for a rectangle that should be visible in the canvas
        if draw_rectangle(200, 200, 600, 400):
            print("Rectangle drawn successfully")
            
            # Wait a moment before adding text
            time.sleep(2)
            
            # Add text
            print("Adding text...")
            if add_text_in_paint("Test Rectangle"):
                print("Text added successfully")
            else:
                print("Failed to add text")
        else:
            print("Failed to draw rectangle")
    else:
        print("Failed to open Paint")
    
    print("Test completed. Press Enter to exit...")
    input()

if __name__ == "__main__":
    main() 