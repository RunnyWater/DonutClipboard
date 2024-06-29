import tkinter as tk
import math
import threading
import keyboard
import pystray
from PIL import Image, ImageTk, ImageDraw
from .clipboard import *

class CircularMenu(tk.Tk):
    def __init__(self, data: dict = None):
        super().__init__()
        self.data = data or get_clipboard_data()

        self.attributes('-topmost', True)
        self.overrideredirect(True)  
        self.geometry("600x600")
        self.configure(bg='#FFFF00') 
        self.wm_attributes('-transparentcolor', '#FFFF00')
        self.bind("<Button-1>", self.start_move)
        self.bind("<Control-Key-c>", self.exit)
        self.bind("<B1-Motion>", self.do_move)
        self.bind("<Escape>", self.iconify_window)   
        self.canvas = tk.Canvas(self, width=600, height=600, bg='#FFFF00', highlightthickness=0)
        self.canvas.pack()
        self.create_donut_buttons()      
        self.create_keybind_list()
        self.create_input_fields_window()
        self.input_window.withdraw()
        self.is_visible = True

        # Start a separate thread to listen for global hotkeys
        self.hotkey_thread = threading.Thread(target=self.setup_global_hotkey)
        self.hotkey_thread.daemon = True
        self.hotkey_thread.start()

        self.setup_system_tray_icon()

    def exit(self, event=None):
        try:
            self.tray_icon.stop()
        except Exception as e:
            print(f"Error stopping threads: {e}")
        finally:
            self.destroy() 

    def setup_global_hotkey(self):
        keyboard.add_hotkey('tab+space', self.toggle_visibility)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def start_move_input_fields(self, event):
        self.input_window.x = event.x
        self.input_window.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.geometry(f"+{self.winfo_x() + deltax}+{self.winfo_y() + deltay}")

    def do_move_input_fields(self, event):
        deltax = event.x - self.input_window.x
        deltay = event.y - self.input_window.y
        self.input_window.geometry(f"+{self.input_window.winfo_x() + deltax}+{self.input_window.winfo_y() + deltay}")

    def create_input_fields_window(self):
        w = 470
        h = 220
        self.input_window = tk.Toplevel(self)
        self.input_window.geometry(f"{w}x{h}")
        self.input_window.overrideredirect(True)
        self.input_window.attributes('-topmost', True)
        self.input_window.wm_attributes('-transparentcolor', 'black') 

        mask_image = ImageTk.PhotoImage(Image.open("src/img/rounded_mask.png"))
        rounded_label = tk.Label(self.input_window, image=mask_image, bg='#333')
        rounded_label.place(x=0, y=0, relwidth=1, relheight=1)
        rounded_label.image = mask_image 

        frame = tk.Frame(self.input_window, bg='#333')
        frame.place(x=20, y=20, width=w-50, height=h)

        for i in range(1, 9):
            label = tk.Label(frame, text=f"Input {i}:", bg='#333', fg='#FFF')
            label.grid(row=(i-1)//2, column=((i-1)%2)*2, padx=10, pady=10)
            entry = tk.Entry(frame)
            entry.grid(row=(i-1)//2, column=((i-1)%2)*2+1, padx=10, pady=10)

        esc_text = "Press Esc to hide this window"
        esc_label = tk.Label(self.input_window, text=esc_text, bg='#333', fg='#FFF')
        esc_label.place(relx=0.5, rely=0.95, anchor='s')


        self.input_window.bind("<Escape>", lambda event: self.input_window.withdraw())
        self.input_window.bind("<Button-1>", self.start_move_input_fields)
        self.input_window.bind("<B1-Motion>", self.do_move_input_fields)



    def toggle_input_fields(self):
        if hasattr(self, 'input_window') and self.input_window.winfo_exists():
            self.input_window.deiconify()  # Show the window if it's hidden
            self.input_window.lift()  # Bring to front
        else:
            self.create_input_fields_window()  # Create and show the window


    def create_donut_buttons(self):
        num_sections = 8
        outer_radius = 250
        inner_radius = 150 
        border_width = 10  
        
        center_x = 300
        center_y = 300

        # Calculate the angle for each section
        angle_increment = 360 / num_sections

        for i in range(num_sections):
            start_angle = i * angle_increment - 90  # Adjust to start at the top
            end_angle = (i + 1) * angle_increment - 90

            # Convert angles to radians
            start_angle_rad = math.radians(start_angle)
            end_angle_rad = math.radians(end_angle)

            # Calculate coordinates for outer arc points (outer arc)
            outer_x1 = center_x + (outer_radius + border_width) * math.cos(start_angle_rad)
            outer_y1 = center_y + (outer_radius + border_width) * math.sin(start_angle_rad)
            outer_x2 = center_x + (outer_radius + border_width) * math.cos(end_angle_rad)
            outer_y2 = center_y + (outer_radius + border_width) * math.sin(end_angle_rad)

            # Calculate coordinates for inner arc points (outer arc)
            inner_x1 = center_x + (inner_radius - border_width) * math.cos(start_angle_rad)
            inner_y1 = center_y + (inner_radius - border_width) * math.sin(start_angle_rad)
            inner_x2 = center_x + (inner_radius - border_width) * math.cos(end_angle_rad)
            inner_y2 = center_y + (inner_radius - border_width) * math.sin(end_angle_rad)

            # Create pie-shaped button
            sector_coords = [center_x, center_y, outer_x1, outer_y1, outer_x2, outer_y2, inner_x2, inner_y2, inner_x1, inner_y1]
            tag = f"section_{i+1}"
            self.canvas.create_polygon(*sector_coords, fill='blue', outline='#FFFF00', width=border_width/2, tags=tag)
            
            # Calculate center for text
            text_radius = (outer_radius + inner_radius) / 2 * .92  # Adjust multiplier to move closer or further from center
            text_angle = math.radians(start_angle + angle_increment / 2)
            text_x = center_x + text_radius * math.cos(text_angle)
            text_y = center_y + text_radius * math.sin(text_angle)
            
            # Create text label
            self.canvas.create_text(text_x, text_y, text=self.get_text(i+1), fill='#FFFFFF', font=('Arial', 20), tags=tag)

            # Bind button click to action
            self.canvas.tag_bind(tag, '<Button-1>', lambda event, i=i+1: self.button_action(i))



    def get_text(self, section_number):
        try:
            return section_number # remove
            return self.data[section_number][:7]+'...'
        except KeyError:
            return "Bind it..."

    def create_keybind_list(self):
        keybind_frame = tk.Frame(self, bg='black')
        keybind_frame.place(relx=0.5, rely=0.55, anchor='s')
        
        keybind_label = tk.Label(keybind_frame, text="Keybinds:", bg='black', fg='white')
        keybind_label.pack()
        
        keybinds = ["Esc - minimize the application", "Tab+Space - toggle visibility"]
        
        for keybind in keybinds:
            keybind_item = tk.Label(keybind_frame, text=keybind, bg='black', fg='white')
            keybind_item.pack()

    def button_action(self, button_number):
        print(f"Section {button_number} pressed")

    def iconify_window(self, event=None):
        self.update_idletasks()
        self.withdraw()  
        self.is_visible = False

    def show_window(self):
        self.deiconify() 
        self.is_visible = True

    def toggle_visibility(self, event=None):
        if self.is_visible:
            self.iconify_window()
        else:
            self.show_window()

    def setup_system_tray_icon(self):
        icon_path = "src/img/icon.ico"
        icon_image = Image.open(icon_path)
        self.tray_icon = pystray.Icon('CircularMenu',icon=icon_image,title="CircularMenu",
                            menu=pystray.Menu(
                                pystray.MenuItem(text="Left-Click-Action", action=lambda:self.toggle_visibility(), default=True, visible=False ),
                                pystray.MenuItem("Open/Close Menu", lambda: self.toggle_visibility()), 
                                pystray.MenuItem("Show Input Fields", lambda: self.toggle_input_fields()),
                                pystray.MenuItem("Exit", lambda: self.exit())
        ))
        self.tray_thread = threading.Thread(target=self.tray_icon.run)
        self.tray_thread.daemon = True
        self.tray_thread.start()