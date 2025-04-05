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

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint maximized on secondary monitor"""
    global paint_app
    logger.info("Tool called: open_paint()")
    try:
        logger.info("Starting Microsoft Paint application")
        paint_app = Application().start('mspaint.exe')
        time.sleep(0.2)
        
        # Get the Paint window
        logger.info("Getting Paint window")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        logger.info(f"Primary monitor width: {primary_width}")
        
        # First move to secondary monitor without specifying size
        logger.info("Moving Paint window to secondary monitor")
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            primary_width + 1, 0,  # Position it on secondary monitor
            0, 0,  # Let Windows handle the size
            win32con.SWP_NOSIZE  # Don't change the size
        )
        
        # Now maximize the window
        logger.info("Maximizing Paint window")
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(0.2)
        
        logger.info("Paint opened successfully on secondary monitor and maximized")
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully on secondary monitor and maximized"
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
        
        # Get the Paint window
        logger.info("Getting Paint window")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width to adjust coordinates
        primary_width = GetSystemMetrics(0)
        logger.info(f"Primary monitor width: {primary_width}")
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            logger.info("Setting focus to Paint window")
            paint_window.set_focus()
            time.sleep(0.2)
        
        # Click on the Rectangle tool
        logger.info("Clicking on Rectangle tool")
        paint_window.click_input(coords=(530, 82))
        time.sleep(0.2)
        
        # Get the canvas area
        logger.info("Getting canvas area")
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Draw rectangle
        logger.info(f"Drawing rectangle from ({x1+2560}, {y1}) to ({x2+2560}, {y2})")
        canvas.press_mouse_input(coords=(x1+2560, y1))
        canvas.move_mouse_input(coords=(x2+2560, y2))
        canvas.release_mouse_input(coords=(x2+2560, y2))
        
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
        
        # Get the Paint window
        logger.info("Getting Paint window")
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            logger.info("Setting focus to Paint window")
            paint_window.set_focus()
            time.sleep(0.5)
        
        # Click on the Text tool
        logger.info("Clicking on Text tool")
        paint_window.click_input(coords=(528, 92))
        time.sleep(0.5)
        
        # Get the canvas area
        logger.info("Getting canvas area")
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Select text tool using keyboard shortcuts
        logger.info("Selecting text tool using keyboard shortcuts")
        paint_window.type_keys('t')
        time.sleep(0.5)
        paint_window.type_keys('x')
        time.sleep(0.5)
        
        # Click where to start typing
        logger.info("Clicking where to start typing")
        canvas.click_input(coords=(810, 533))
        time.sleep(0.5)
        
        # Type the text
        logger.info(f"Typing text: '{text}'")
        paint_window.type_keys(text)
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