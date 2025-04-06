from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from pywinauto.application import Application
import win32gui
import win32con
import time
import logging
import os
from datetime import datetime
from win32api import GetSystemMetrics

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"paint_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize MCP server
logger.info("Initializing Paint MCP server")
mcp = FastMCP("PaintController")

# Global variable to store Paint application instance
paint_app = None

def ensure_paint_active():
    """Ensure the Paint window is active and visible"""
    global paint_app
    if not paint_app:
        logger.warning("Paint is not open. Please call open_paint first.")
        return False
    
    try:
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Check if the window is minimized and restore it if needed
        if win32gui.IsIconic(paint_window.handle):
            logger.info("Paint window is minimized, restoring it")
            win32gui.ShowWindow(paint_window.handle, win32con.SW_RESTORE)
            time.sleep(0.5)  # Wait for the window to be restored
        
        # Ensure the window is active and in the foreground
        logger.info("Ensuring Paint window is active and in the foreground")
        win32gui.SetForegroundWindow(paint_window.handle)
        time.sleep(0.5)  # Wait for the window to become active
        
        # Bring the window to the top
        logger.info("Bringing Paint window to the top")
        win32gui.BringWindowToTop(paint_window.handle)
        time.sleep(0.5)  # Wait for the window to be brought to the top
        
        return True
    except Exception as e:
        logger.error(f"Error ensuring Paint window is active: {str(e)}")
        return False

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint"""
    global paint_app
    logger.info("Tool called: open_paint()")
    try:
        logger.info("Starting Microsoft Paint application")
        paint_app = Application().start('mspaint.exe')
        time.sleep(1.5)  # Increased sleep time to ensure Paint is fully loaded
        
        # Get the Paint window
        logger.info("Getting Paint window")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        logger.info(f"Primary monitor width: {primary_width}")
        
        # Ensure the window is active and in the foreground
        logger.info("Ensuring Paint window is active and in the foreground")
        win32gui.SetForegroundWindow(paint_window.handle)
        time.sleep(0.5)  # Wait for the window to become active
        
        # Bring the window to the top
        logger.info("Bringing Paint window to the top")
        win32gui.BringWindowToTop(paint_window.handle)
        time.sleep(0.5)  # Wait for the window to be brought to the top
        
        # Set the window to be topmost temporarily to ensure it's visible
        logger.info("Setting Paint window to be topmost temporarily")
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        time.sleep(0.5)  # Wait for the window to be set as topmost
        
        # Set the window back to normal (not topmost)
        logger.info("Setting Paint window back to normal")
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        time.sleep(0.5)  # Wait for the window to be set back to normal
        
        logger.info("Paint opened successfully")
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully"
                )
            ]
        }
    except Exception as e:
        logger.error(f"Error opening Paint: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app
    logger.info(f"Tool called: draw_rectangle(x1={x1}, y1={y1}, x2={x2}, y2={y2})")
    try:
        if not paint_app:
            logger.warning("Paint is not open. Please call open_paint first.")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Ensure Paint window is active and visible
        if not ensure_paint_active():
            logger.warning("Failed to ensure Paint window is active")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Failed to ensure Paint window is active"
                    )
                ]
            }
        
        # Get the Paint window
        logger.info("Getting Paint window")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width to adjust coordinates
        primary_width = GetSystemMetrics(0)
        logger.info(f"Primary monitor width: {primary_width}")
        
        # Click on the Rectangle tool
        logger.info("Clicking on Rectangle tool")
        paint_window.click_input(coords=(440, 65))
        time.sleep(1)
        
        # Get the canvas area
        logger.info("Getting canvas area")
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Draw rectangle
        logger.info(f"Drawing rectangle from ({x1}, {y1}) to ({x2}, {y2})")
        canvas.press_mouse_input(coords=(x1, y1))
        canvas.move_mouse_input(coords=(x2, y2))
        canvas.release_mouse_input(coords=(x2, y2))
        
        logger.info("Rectangle drawn successfully")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        logger.error(f"Error drawing rectangle: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text(text: str) -> dict:
    """Add text in Paint"""
    global paint_app
    logger.info(f"Tool called: add_text(text='{text}')")
    try:
        if not paint_app:
            logger.warning("Paint is not open. Please call open_paint first.")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Ensure Paint window is active and visible
        if not ensure_paint_active():
            logger.warning("Failed to ensure Paint window is active")
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Failed to ensure Paint window is active"
                    )
                ]
            }
        
        # Get the Paint window
        logger.info("Getting Paint window")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Click on the Text tool
        logger.info("Clicking on Text tool")
        paint_window.click_input(coords=(290, 72))
        time.sleep(0.5)
        
        # Get the canvas area
        logger.info("Getting canvas area")
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Select text tool using keyboard shortcuts
        logger.info("Selecting text tool using keyboard shortcuts")
        paint_window.type_keys('t')
        time.sleep(0.5)
        paint_window.type_keys('x')
        
        # Click where to start typing
        logger.info("Clicking where to start typing")
        canvas.click_input(coords=(810, 533))
        time.sleep(0.5)
        
        # Type the text
        logger.info(f"Typing text: '{text}'")
        # Use a different approach to type text with spaces
        for char in text:
            if char == ' ':
                # For spaces, use the space key
                paint_window.type_keys('{SPACE}')
            else:
                # For other characters, type them directly
                paint_window.type_keys(char)
            time.sleep(0.1)  # Small delay between characters
        time.sleep(0.5)
        
        # Click to exit text mode
        logger.info("Clicking to exit text mode")
        canvas.click_input(coords=(1050, 800))
        
        logger.info("Text added successfully")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text '{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        logger.error(f"Error adding text: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error adding text: {str(e)}"
                )
            ]
        }

if __name__ == "__main__":
    logger.info("Starting Paint MCP server")
    mcp.run(transport="stdio")
    logger.info("Paint MCP server stopped") 