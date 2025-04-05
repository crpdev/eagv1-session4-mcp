import win32gui
import win32con
import win32api
import time
from pywinauto.application import Application
from win32api import GetSystemMetrics, mouse_event, SetCursorPos
import pyautogui
import os

# Global variable to store the Paint application
paint_app = None
paint_window_handle = None

def activate_window(hwnd):
    """Activate a window and bring it to the foreground"""
    try:
        # Try multiple methods to activate the window
        # Method 1: SetForegroundWindow
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        
        # Method 2: ShowWindow with SW_RESTORE if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)
        
        # Method 3: Bring to top
        win32gui.BringWindowToTop(hwnd)
        time.sleep(0.5)
        
        # Method 4: Set position to topmost temporarily
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        time.sleep(0.5)
        
        # Method 5: Set position back to normal
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        time.sleep(0.5)
        
        # Verify the window is now in the foreground
        return win32gui.GetForegroundWindow() == hwnd
    except Exception as e:
        print(f"Error activating window: {str(e)}")
        return False

def is_window_minimized(hwnd):
    """Check if a window is minimized"""
    return win32gui.IsIconic(hwnd)

def is_window_fullscreen(hwnd):
    """Check if a window is in fullscreen mode"""
    # Get the window style
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    # Check if the window has WS_MAXIMIZE style
    return bool(style & win32con.WS_MAXIMIZE)

def restore_window(hwnd):
    """Restore a minimized window"""
    if is_window_minimized(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(1)
        return True
    return False

def exit_fullscreen(hwnd):
    """Exit fullscreen mode"""
    if is_window_fullscreen(hwnd):
        # Send Alt+Enter to exit fullscreen
        win32api.keybd_event(0x12, 0, 0, 0)  # Alt key down
        win32api.keybd_event(0x0D, 0, 0, 0)  # Enter key down
        time.sleep(0.1)
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)  # Enter key up
        win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt key up
        time.sleep(1)
        return True
    return False

def ensure_paint_window_active():
    """Ensure Paint window is active and maximized"""
    global paint_app
    if not paint_app:
        return False
    
    try:
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Check if window is minimized and restore it
        if is_window_minimized(paint_window.handle):
            print("Paint window is minimized, restoring it...")
            restore_window(paint_window.handle)
        
        # Check if window is in fullscreen mode and exit it
        if is_window_fullscreen(paint_window.handle):
            print("Paint window is in fullscreen mode, exiting fullscreen...")
            exit_fullscreen(paint_window.handle)
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        
        # Move to secondary monitor and maximize
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOPMOST,  # Make it topmost to prevent minimizing
            primary_width + 100, 0,  # Position it on secondary monitor
            1920, 1080,  # Set a large size
            win32con.SWP_SHOWWINDOW
        )
        time.sleep(1)
        
        # Ensure window is active and maximized
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(1)
        
        # Multiple attempts to set focus
        for _ in range(5):  # Increased attempts
            win32gui.SetForegroundWindow(paint_window.handle)
            paint_window.set_focus()
            time.sleep(0.5)
        
        # Verify window is active
        active_window = win32gui.GetForegroundWindow()
        if active_window != paint_window.handle:
            print("Warning: Paint window is not active")
            return False
            
        return True
    except Exception as e:
        print(f"Error ensuring Paint window is active: {str(e)}")
        return False

def open_paint():
    """Open Microsoft Paint and return the window handle"""
    global paint_app, paint_window_handle
    try:
        # Close any existing Paint instances
        os.system("taskkill /f /im mspaint.exe")
        time.sleep(1)
        
        # Start Paint
        paint_app = Application().start('mspaint.exe')
        time.sleep(2)  # Wait for Paint to fully load
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        paint_window_handle = paint_window.handle
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        
        # Move to secondary monitor with a specific size (not maximized)
        win32gui.SetWindowPos(
            paint_window_handle,
            win32con.HWND_TOP,
            primary_width + 100, 0,  # Position it on secondary monitor
            1024, 768,  # Set a specific size (not maximized)
            win32con.SWP_SHOWWINDOW
        )
        time.sleep(1)
        
        # Activate the window
        if not activate_window(paint_window_handle):
            print("Warning: Failed to activate Paint window")
        
        time.sleep(1)
        
        return paint_window
    except Exception as e:
        print(f"Error opening Paint: {str(e)}")
        return None

def draw_rectangle(x1, y1, x2, y2):
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app, paint_window_handle
    try:
        if not paint_app or not paint_window_handle:
            print("Paint is not open. Please call open_paint first.")
            return False
        
        # Activate the window
        if not activate_window(paint_window_handle):
            print("Warning: Failed to activate Paint window")
            return False
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        canvas_rect = canvas.rectangle()
        
        # Print canvas dimensions for debugging
        print(f"Canvas dimensions: {canvas_rect.width()}x{canvas_rect.height()}")
        print(f"Canvas position: ({canvas_rect.left}, {canvas_rect.top})")
        
        # Calculate canvas offset
        canvas_x = canvas_rect.left
        canvas_y = canvas_rect.top
        
        # Click the Rectangle tool button (coordinates for the Rectangle tool in Paint)
        # Use absolute coordinates for the toolbar
        toolbar_x = paint_window.rectangle().left + 250
        toolbar_y = paint_window.rectangle().top + 80
        win32api.SetCursorPos((toolbar_x, toolbar_y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Click the outline thickness button and select thickest line
        thickness_x = paint_window.rectangle().left + 350
        thickness_y = paint_window.rectangle().top + 80
        win32api.SetCursorPos((thickness_x, thickness_y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Select the thickest line
        thickest_x = paint_window.rectangle().left + 350
        thickest_y = paint_window.rectangle().top + 200
        win32api.SetCursorPos((thickest_x, thickest_y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Calculate absolute coordinates for the canvas
        abs_x1 = canvas_x + x1
        abs_y1 = canvas_y + y1
        abs_x2 = canvas_x + x2
        abs_y2 = canvas_y + y2
        
        # Print coordinates for debugging
        print(f"Drawing rectangle from ({abs_x1}, {abs_y1}) to ({abs_x2}, {abs_y2})")
        
        # Press and hold at the starting point
        win32api.SetCursorPos((abs_x1, abs_y1))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Move to the end point while holding
        win32api.SetCursorPos((abs_x2, abs_y2))
        time.sleep(0.5)
        
        # Release at the end point
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"Error drawing rectangle: {str(e)}")
        return False

def add_text_in_paint(text):
    """Add text in Paint"""
    global paint_app, paint_window_handle
    try:
        if not paint_app or not paint_window_handle:
            print("Paint is not open. Please call open_paint first.")
            return False
        
        # Activate the window
        if not activate_window(paint_window_handle):
            print("Warning: Failed to activate Paint window")
            return False
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        canvas_rect = canvas.rectangle()
        
        # Calculate canvas center
        center_x = canvas_rect.width() // 2
        center_y = canvas_rect.height() // 2
        
        # Click the Text tool button
        text_tool_x = paint_window.rectangle().left + 400
        text_tool_y = paint_window.rectangle().top + 80
        win32api.SetCursorPos((text_tool_x, text_tool_y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Click the font size button and select large size
        font_size_x = paint_window.rectangle().left + 450
        font_size_y = paint_window.rectangle().top + 80
        win32api.SetCursorPos((font_size_x, font_size_y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Select large font size
        large_font_x = paint_window.rectangle().left + 450
        large_font_y = paint_window.rectangle().top + 200
        win32api.SetCursorPos((large_font_x, large_font_y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Calculate absolute coordinates for the canvas center
        abs_center_x = canvas_rect.left + center_x
        abs_center_y = canvas_rect.top + center_y
        
        # Click at the center point
        win32api.SetCursorPos((abs_center_x, abs_center_y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Type the text
        for char in text:
            win32api.keybd_event(ord(char), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
        
        time.sleep(0.5)
        
        # Click outside to finish text input
        win32api.SetCursorPos((canvas_rect.left + 50, canvas_rect.top + 50))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"Error adding text: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Open Paint
    paint_window = open_paint()
    if paint_window:
        print("Paint opened successfully")
        
        # Draw a rectangle
        if draw_rectangle(100, 100, 500, 300):
            print("Rectangle drawn successfully")
            
            # Add text
            if add_text_in_paint("Hello, World!"):
                print("Text added successfully")
            else:
                print("Failed to add text")
        else:
            print("Failed to draw rectangle")
    else:
        print("Failed to open Paint") 