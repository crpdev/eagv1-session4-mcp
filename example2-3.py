# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import win32api
import time
from win32api import GetSystemMetrics, SetCursorPos, mouse_event

# Global variable to store Paint window handle
paint_window_handle = None

def is_paint_active():
    """Check if Paint is the active window"""
    global paint_window_handle
    print("\n=== CHECKING IF PAINT IS ACTIVE ===")
    if paint_window_handle:
        print(f"Paint window handle exists: {paint_window_handle}")
        active_window = win32gui.GetForegroundWindow()
        time.sleep(1)
        print(f"Current foreground window: {active_window}")
        is_active = (active_window == paint_window_handle)
        print(f"Paint active window check: {is_active}")
        print(f"Active window handle: {active_window}")
        print(f"Paint window handle: {paint_window_handle}")
        print("=== END OF PAINT ACTIVE CHECK ===\n")
        return is_active
    else:
        print("Paint window handle is None!")
        print("=== END OF PAINT ACTIVE CHECK ===\n")
        return False

def ensure_paint_active():
    """Ensure Paint window is active and not minimized"""
    global paint_window_handle
    if paint_window_handle:
        print("Checking Paint window state...")
        
        # Check if window is minimized
        is_minimized = win32gui.IsIconic(paint_window_handle)
        time.sleep(1)
        print(f"Paint window minimized: {is_minimized}")
        
        if is_minimized:
            # Restore the window
            print("Restoring minimized Paint window...")
            win32gui.ShowWindow(paint_window_handle, win32con.SW_RESTORE)
            time.sleep(1)  # Increased delay after restore
        
        # Bring window to front
        print("Bringing Paint window to front...")
        win32gui.SetForegroundWindow(paint_window_handle)
        time.sleep(1)  # Increased delay after bringing to front
        
        # Ensure window is visible
        print("Ensuring Paint window is visible...")
        win32gui.ShowWindow(paint_window_handle, win32con.SW_SHOW)
        time.sleep(1)  # Increased delay after showing
        
        # Additional steps to ensure window is active
        print("Performing additional activation steps...")
        
        # Set window position to top
        win32gui.SetWindowPos(
            paint_window_handle,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        time.sleep(1)
        
        # Set window position back to normal
        win32gui.SetWindowPos(
            paint_window_handle,
            win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        time.sleep(1)
        
        # Try to activate window again
        win32gui.SetForegroundWindow(paint_window_handle)
        time.sleep(1)
        
        # Verify window is active
        is_active = is_paint_active()
        print(f"Paint window activation result: {is_active}")
        
        # If still not active, try one more time with a different approach
        if not is_active:
            print("Window still not active, trying alternative approach...")
            # Try to force activation by simulating Alt key
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt key down
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt key up
            time.sleep(0.1)
            win32gui.SetForegroundWindow(paint_window_handle)
            time.sleep(1)
            
            # Check again
            is_active = is_paint_active()
            print(f"Paint window activation result after alternative approach: {is_active}")
        
        return is_active
    return False

def cleanup_paint_window():
    """Ensure Paint window is visible and not minimized after execution"""
    global paint_window_handle
    if paint_window_handle:
        print("\n=== CLEANING UP PAINT WINDOW ===")
        try:
            # Check if window is minimized
            is_minimized = win32gui.IsIconic(paint_window_handle)
            print(f"Paint window minimized before cleanup: {is_minimized}")
            
            if is_minimized:
                # Restore the window
                print("Restoring minimized Paint window...")
                win32gui.ShowWindow(paint_window_handle, win32con.SW_RESTORE)
                time.sleep(1)
            
            # Bring window to front
            print("Bringing Paint window to front...")
            win32gui.SetForegroundWindow(paint_window_handle)
            time.sleep(1)
            
            # Ensure window is visible
            print("Ensuring Paint window is visible...")
            win32gui.ShowWindow(paint_window_handle, win32con.SW_SHOW)
            time.sleep(1)
            
            # Verify window state
            is_minimized = win32gui.IsIconic(paint_window_handle)
            print(f"Paint window minimized after cleanup: {is_minimized}")
            
            if not is_minimized:
                print("Paint window successfully restored and visible")
            else:
                print("WARNING: Paint window is still minimized after cleanup")
            
            print("=== END OF CLEANUP ===\n")
        except Exception as e:
            print(f"Error during Paint window cleanup: {str(e)}")

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app, paint_window_handle
    try:
        print("Starting rectangle drawing process...")
        
        if not paint_app or not paint_window_handle:
            print("Paint is not open")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Ensure Paint window is active
        print("Ensuring Paint window is active before drawing...")
        if not ensure_paint_active():
            print("Failed to activate Paint window")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Failed to activate Paint window"
                    )
                ]
            }
        
        # Get the Paint window
        print("Getting Paint window for drawing...")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Select the Rectangle tool using mouse click at specific coordinates
        print("Selecting Rectangle tool...")
        toolbar_x = paint_window.rectangle().left + 450
        toolbar_y = paint_window.rectangle().top + 75
        print(f"Toolbar coordinates: ({toolbar_x}, {toolbar_y})")
        
        # Convert coordinates to screen coordinates
        screen_x = win32gui.ClientToScreen(paint_window_handle, (toolbar_x, toolbar_y))[0]
        screen_y = win32gui.ClientToScreen(paint_window_handle, (toolbar_x, toolbar_y))[1]
        print(f"Screen coordinates: ({screen_x}, {screen_y})")
        
        # Move cursor and click
        print("Moving cursor to Rectangle tool...")
        SetCursorPos((screen_x, screen_y))
        time.sleep(0.5)
        print("Clicking Rectangle tool...")
        mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        time.sleep(1)  # Increased delay after selecting tool
        
        # Verify window is still active
        is_active = is_paint_active()
        print(f"Paint window active after selecting tool: {is_active}")
        
        # If window is not active, try to restore it
        if not is_active:
            print("Window lost focus after selecting tool, trying to restore...")
            if not ensure_paint_active():
                print("Failed to restore Paint window after selecting tool")
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text="Failed to keep Paint window active after selecting tool"
                        )
                    ]
                }
        
        # Get the canvas area
        print("Getting canvas area...")
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Draw rectangle - coordinates should already be relative to the Paint window
        print(f"Drawing rectangle from ({x1},{y1}) to ({x2},{y2})...")
        canvas.press_mouse_input(coords=(x1, y1))
        time.sleep(1)  # Increased delay after pressing
        canvas.move_mouse_input(coords=(x2, y2))
        time.sleep(1)  # Increased delay after moving
        canvas.release_mouse_input(coords=(x2, y2))
        time.sleep(1)  # Increased delay after releasing
        
        # Verify window is still active
        is_active = is_paint_active()
        print(f"Paint window active after drawing: {is_active}")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        print(f"Error drawing rectangle: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Add text in Paint"""
    global paint_app, paint_window_handle
    try:
        print("Starting text addition process...")
        
        if not paint_app or not paint_window_handle:
            print("Paint is not open")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Ensure Paint window is active
        print("Ensuring Paint window is active before adding text...")
        if not ensure_paint_active():
            print("Failed to activate Paint window")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Failed to activate Paint window"
                    )
                ]
            }
        
        # Get the Paint window
        print("Getting Paint window for text...")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
                # Select the Rectangle tool using mouse click at specific coordinates
        print("Selecting Rectangle tool...")
        toolbar_x = paint_window.rectangle().left + 300
        toolbar_y = paint_window.rectangle().top + 80
        print(f"Toolbar coordinates: ({toolbar_x}, {toolbar_y})")
        
        # Convert coordinates to screen coordinates
        screen_x = win32gui.ClientToScreen(paint_window_handle, (toolbar_x, toolbar_y))[0]
        screen_y = win32gui.ClientToScreen(paint_window_handle, (toolbar_x, toolbar_y))[1]
        print(f"Screen coordinates: ({screen_x}, {screen_y})")
        
        # Move cursor and click
        print("Moving cursor to Rectangle tool...")
        SetCursorPos((screen_x, screen_y))
        time.sleep(0.5)
        print("Clicking Rectangle tool...")
        mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        time.sleep(1)  # Increased delay after selecting tool
        
        # Verify window is still active
        is_active = is_paint_active()
        print(f"Paint window active after selecting tool: {is_active}")
        
        # If window is not active, try to restore it
        if not is_active:
            print("Window lost focus after selecting tool, trying to restore...")
            if not ensure_paint_active():
                print("Failed to restore Paint window after selecting tool")
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text="Failed to keep Paint window active after selecting tool"
                        )
                    ]
                }
        
        # Get the canvas area
        print("Getting canvas area...")
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Click where to start typing
        print("Clicking canvas for text input...")
        canvas.click_input(coords=(900, 525))  # Using more reasonable coordinates
        time.sleep(1)  # Increased delay after clicking
        
        # Verify window is still active
        is_active = is_paint_active()
        print(f"Paint window active before typing: {is_active}")
        
        # Type the text passed from client
        print(f"Typing text: '{text}'...")
        paint_window.type_keys(text)
        time.sleep(1)  # Increased delay after typing
        
        # Click outside the text box to finish
        print("Clicking outside text box...")
        canvas.click_input(coords=(800, 800))
        time.sleep(1)  # Increased delay after clicking outside
        
        # Verify window is still active
        is_active = is_paint_active()
        print(f"Paint window active after adding text: {is_active}")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        print(f"Error adding text: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint"""
    global paint_app, paint_window_handle
    try:
        print("\n=== STARTING PAINT OPENING PROCESS ===")
        paint_app = Application().start('mspaint.exe')
        time.sleep(2)  # Increased delay to ensure Paint fully loads
        
        # Get the Paint window
        print("Getting Paint window...")
        paint_window = paint_app.window(class_name='MSPaintApp')
        paint_window_handle = paint_window.handle
        print(f"Paint window handle: {paint_window_handle}")
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        print(f"Primary monitor width: {primary_width}")
        
        
        # Ensure window stays on top and has focus
        print("Setting Paint window focus...")
        win32gui.SetForegroundWindow(paint_window_handle)
        paint_window.set_focus()
        time.sleep(1)
        
        # Force the window to be visible and not minimized
        print("Ensuring Paint window is visible...")
        win32gui.ShowWindow(paint_window_handle, win32con.SW_RESTORE)
        time.sleep(1)
        
        # Verify window is active
        print("\nChecking if Paint is active after opening...")
        is_active = is_paint_active()
        print(f"Paint window active after opening: {is_active}")
        print("=== END OF PAINT OPENING PROCESS ===\n")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully"
                )
            ]
        }
    except Exception as e:
        print(f"Error opening Paint: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "dev":
            mcp.run()  # Run without transport for dev server
        else:
            mcp.run(transport="stdio")  # Run with stdio for direct execution
    finally:
        # Ensure Paint window is visible after execution
        cleanup_paint_window()
