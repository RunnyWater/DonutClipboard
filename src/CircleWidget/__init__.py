import tkinter as tk
import math
import threading
import keyboard
import pystray
from PIL import Image

class CircularMenu(tk.Tk):
    def __init__(self, data: dict = None):
        super().__init__()
        self.data = data or {
            1: "Option 1",
            2: "Option 2",
            3: "Option 3",
            4: "Option 4",
            5: "Option 5",
            6: "Option 6",
            7: "Option 7",
            8: "Option 8"
        }

        self.attributes('-topmost', True)
        self.overrideredirect(True)  # Set the window to override-redirect mode 
        self.geometry("600x600")
        self.configure(bg='#FFFF00')  # Set background color to match the buttons' background
        self.wm_attributes('-transparentcolor', '#FFFF00')
        self.bind("<Button-1>", self.start_move)
        self.bind("<Control-Key-c>", self.exit)
        self.bind("<B1-Motion>", self.do_move)
        self.bind("<Escape>", self.iconify_window)   
        self.bind("<FocusOut>", self.iconify_window)
        self.canvas = tk.Canvas(self, width=600, height=600, bg='#FFFF00', highlightthickness=0)
        self.canvas.pack()
        self.create_donut_buttons()      
        self.create_keybind_list()
        self.is_visible = True  # Keep track of window visibility

        # Start a separate thread to listen for global hotkeys
        self.hotkey_thread = threading.Thread(target=self.setup_global_hotkey)
        self.hotkey_thread.daemon = True
        self.hotkey_thread.start()

        # Initialize system tray icon
        self.setup_system_tray_icon()

    def exit(self, event=None):
        try:
            self.tray_icon.stop()  # Stop the tray icon

        except Exception as e:
            print(f"Error stopping threads: {e}")
        finally:
            self.destroy()  # Destroy the Tkinter window

    def setup_global_hotkey(self):
        keyboard.add_hotkey('tab+space', self.toggle_visibility)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.geometry(f"+{self.winfo_x() + deltax}+{self.winfo_y() + deltay}")

    def create_donut_buttons(self):
        # Number of buttons (sections of the donut)
        num_sections = 8
        # Radius of the donut
        outer_radius = 250
        inner_radius = 150  # Adjust inner radius to control thickness of the donut
        border_width = 10  # Width of the border
        
        # Center of the donut (adjust if needed)
        center_x = 300
        center_y = 300

        # Calculate the angle for each section
        angle_increment = 360 / num_sections

        for i in range(num_sections):
            start_angle = i * angle_increment
            end_angle = (i + 1) * angle_increment

            # Convert angles to radians
            start_angle_rad = math.radians(start_angle)
            end_angle_rad = math.radians(end_angle)

            # Calculate coordinates for outer arc points (outer arc)
            outer_x1 = center_x + (outer_radius + border_width) * math.cos(start_angle_rad)
            outer_y1 = center_y - (outer_radius + border_width) * math.sin(start_angle_rad)
            outer_x2 = center_x + (outer_radius + border_width) * math.cos(end_angle_rad)
            outer_y2 = center_y - (outer_radius + border_width) * math.sin(end_angle_rad)

            # Calculate coordinates for inner arc points (outer arc)
            inner_x1 = center_x + (inner_radius - border_width) * math.cos(start_angle_rad)
            inner_y1 = center_y - (inner_radius - border_width) * math.sin(start_angle_rad)
            inner_x2 = center_x + (inner_radius - border_width) * math.cos(end_angle_rad)
            inner_y2 = center_y - (inner_radius - border_width) * math.sin(end_angle_rad)

            # Create pie-shaped button
            sector_coords = [center_x, center_y, outer_x1, outer_y1, outer_x2, outer_y2, inner_x2, inner_y2, inner_x1, inner_y1]
            tag = f"section_{i+1}"
            self.canvas.create_polygon(*sector_coords, fill='blue', outline='#FFFF00', width=border_width, tags=tag)
            
            # Calculate center for text
            text_radius = (outer_radius + inner_radius) / 2 * .92  # Adjust multiplier to move closer or further from center
            text_angle = math.radians(start_angle + angle_increment / 2)
            text_x = center_x + text_radius * math.cos(text_angle)
            text_y = center_y - text_radius * math.sin(text_angle)
            
            # Create text label
            self.canvas.create_text(text_x, text_y, text=self.get_text(i+1), fill='#FFFFFF', font=('Arial', 15), tags=tag)

            # Bind button click to action
            self.canvas.tag_bind(tag, '<Button-1>', lambda event, i=i+1: self.button_action(i))


    def get_text(self, section_number):
        try:
            return self.data[section_number][:10]
        except KeyError:
            return "Press to bind"

    def create_keybind_list(self):
        keybind_frame = tk.Frame(self, bg='black')
        keybind_frame.place(relx=0.5, rely=0.55, anchor='s')
        
        keybind_label = tk.Label(keybind_frame, text="Keybinds:", bg='black', fg='white')
        keybind_label.pack()
        
        # List of keybinds (example)
        keybinds = ["Ctrl+C - exit fully the application", "Ctrl+Shift+H - toggle visibility"]
        
        for keybind in keybinds:
            keybind_item = tk.Label(keybind_frame, text=keybind, bg='black', fg='white')
            keybind_item.pack()

    def button_action(self, button_number):
        print(f"Section {button_number} pressed")

    def iconify_window(self, event=None):
        self.update_idletasks()  # Ensure the window updates before minimizing
        self.withdraw()  # Minimize the window
        self.is_visible = False

    def show_window(self):
        self.deiconify()  # Restore the window
        self.is_visible = True

    def toggle_visibility(self, event=None):
        if self.is_visible:
            self.iconify_window()
        else:
            self.show_window()

    def setup_system_tray_icon(self):
        icon_path = "icon_white.ico"
        icon_image = Image.open(icon_path)
        self.tray_icon = pystray.Icon('CircularMenu',icon=icon_image,title="CircularMenu",
                            menu=pystray.Menu(
                                pystray.MenuItem(text="Left-Click-Action", action=lambda:self.toggle_visibility(), default=True, visible=False ),
                                pystray.MenuItem("Open/Close Menu", lambda: self.toggle_visibility()), 
                                pystray.MenuItem("Exit", lambda: self.exit())
        ))
        self.tray_thread = threading.Thread(target=self.tray_icon.run)
        self.tray_thread.daemon = True
        self.tray_thread.start()