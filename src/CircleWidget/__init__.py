import tkinter as tk
import math
import threading
import keyboard
import pystray
from PIL import Image, ImageTk, ImageDraw
from .clipboard import *
import pyperclip

class CircularMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = get_clipboard_data()

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
        self.create_keybind_list()
        self.create_clipboard_label()
        self.create_input_fields_window()
        self.create_donut_buttons()      
        self.center_both_windows()
        self.input_window.withdraw()
        self.is_visible = True
        self.input_fields_visibility = False
        
        
        self.hotkey_thread = threading.Thread(target=self.setup_global_hotkey)
        self.hotkey_thread.daemon = True
        self.hotkey_thread.start()

        self.setup_system_tray_icon()


    def center_both_windows(self):
        self.update_idletasks()
        

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        self.geometry(f"+{screen_width//2 - window_width//2}+{screen_height//2 - window_height//2}")
       
        input_fields_width = self.input_window.winfo_width()
        input_fields_height = self.input_window.winfo_height()

        self.input_window.geometry(f"+{screen_width//2 - input_fields_width//2}+{screen_height//2 - input_fields_height//2}")


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
        print(event.x, event.y)
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.geometry(f"+{self.winfo_x() + deltax}+{self.winfo_y() + deltay}")

    def do_move_input_fields(self, event):
        deltax = event.x - self.input_window.x
        deltay = event.y - self.input_window.y
        self.input_window.geometry(f"+{self.input_window.winfo_x() + deltax}+{self.input_window.winfo_y() + deltay}")

    def create_input_fields_window(self):
        w = 500
        h = 400
        self.input_window = tk.Toplevel(self)
        self.input_window.geometry(f"{w}x{h}")
        self.input_window.overrideredirect(True)
        self.input_window.attributes('-topmost', True)

        if not os.path.exists("src/img/rounded_mask.png"):
            rounded_mask = Image.new("RGBA", (w, h), 0)
            draw = ImageDraw.Draw(rounded_mask)
            draw.rounded_rectangle((0, 0, w, h), radius=30, fill='#333333FF')
            rounded_mask.save("src/img/rounded_mask.png")
        
        self.input_window.wm_attributes('-transparentcolor', '#FFFF00') 
        mask_image = ImageTk.PhotoImage(Image.open("src/img/rounded_mask.png"))
        rounded_label = tk.Label(self.input_window, image=mask_image, bg='#FFFF00')
        rounded_label.place(x=0, y=0, relwidth=1, relheight=1)
        rounded_label.image = mask_image 

        frame = tk.Frame(self.input_window, bg='#333333')
        frame.place(x=20, y=20, width=w-40, height=h-60)

        self.entries = []
        def revert_button_color(button):
            button.config(bg='#333')

        def setup_placeholder(entry_widget, placeholder_text):
            entry_widget.insert(0, placeholder_text)
            entry_widget.config(fg='gray')
            
            def clear_placeholder(event):
                if entry_widget.get() == placeholder_text:
                    entry_widget.delete(0, 'end')
                    entry_widget.config(fg='black')
                    
            def restore_placeholder(event):
                if entry_widget.get() == '':
                    setup_placeholder(entry_widget, placeholder_text)
            
            entry_widget.bind('<FocusIn>', clear_placeholder)
            entry_widget.bind('<FocusOut>', restore_placeholder)

        for i in range(1, 9):
            button = tk.Button(frame, text=f"Bind key {i}", bg='#333', fg='#FFF', border=1)
            button.grid(row=(i-1)//2, column=(i-1)%2*2, padx=10, pady=10)
            
            def on_click(i):
                for btn in frame.winfo_children():
                    if isinstance(btn, tk.Button) and btn.cget('text') == f"Bind key {i}":
                        btn.config(bg='#444')
                        frame.after(3000, lambda: revert_button_color(btn))
                        break 
                
                self.set_new_bind_button(i)
            button.config(command=lambda i=i: on_click(i))
            
            entry = tk.Entry(frame)
            entry.grid(row=(i-1)//2, column=(i-1)%2*2+1, padx=10, pady=10)
            placeholder_text = self.get_text_by_section_number(i)
            setup_placeholder(entry, placeholder_text)
            self.entries.append(entry)



        esc_text = "Press Esc to hide this window"
        esc_label = tk.Label(self.input_window, text=esc_text, bg='#333', fg='#FFF')
        esc_label.place(relx=0.5, rely=0.95, anchor='s')


        self.input_window.bind("<Escape>", lambda event: self.input_window.withdraw())
        self.input_window.bind("<Button-1>", self.start_move_input_fields)
        self.input_window.bind("<B1-Motion>", self.do_move_input_fields)

    def set_new_bind_button(self, button_number):
        entry_text = self.entries[button_number-1].get()
        if entry_text == "":
            return
        set_new_bind(button_number, entry_text)
        self.reset_color()
        self.update_text_objects()


    def toggle_input_fields(self):
        if self.input_fields_visibility:
            self.input_window.withdraw()
            self.input_fields_visibility = False 
        else:
            self.input_window.deiconify()
            self.input_fields_visibility = True
            if self.is_visible:
                self.toggle_visibility()


    def create_donut_buttons(self):
        num_sections = 8
        outer_radius = 250
        inner_radius = 150 
        border_width = 10  
        
        center_x = 300
        center_y = 300

        angle_increment = 360 / num_sections

        self.buttons = []
        self.text_objects = []
        for i in range(num_sections):
            start_angle = i * angle_increment - 90
            end_angle = (i + 1) * angle_increment - 90

            start_angle_rad = math.radians(start_angle)
            end_angle_rad = math.radians(end_angle)

            outer_x1 = center_x + (outer_radius + border_width) * math.cos(start_angle_rad)
            outer_y1 = center_y + (outer_radius + border_width) * math.sin(start_angle_rad)
            outer_x2 = center_x + (outer_radius + border_width) * math.cos(end_angle_rad)
            outer_y2 = center_y + (outer_radius + border_width) * math.sin(end_angle_rad)

            inner_x1 = center_x + (inner_radius - border_width) * math.cos(start_angle_rad)
            inner_y1 = center_y + (inner_radius - border_width) * math.sin(start_angle_rad)
            inner_x2 = center_x + (inner_radius - border_width) * math.cos(end_angle_rad)
            inner_y2 = center_y + (inner_radius - border_width) * math.sin(end_angle_rad)

            sector_coords = [center_x, center_y, outer_x1, outer_y1, outer_x2, outer_y2, inner_x2, inner_y2, inner_x1, inner_y1]
            tag = f"section_{i+1}"
            self.canvas.create_polygon(*sector_coords, fill='blue', outline='#FFFF00', width=border_width/2, tags=tag)
            
            text_radius = (outer_radius + inner_radius) / 2 * .92
            text_angle = math.radians(start_angle + angle_increment / 2)
            text_x = center_x + text_radius * math.cos(text_angle)
            text_y = center_y + text_radius * math.sin(text_angle)
            
            text_object = self.canvas.create_text(text_x, text_y, text=self.get_text(i+1), fill='#FFFFFF', font=('Arial', 15), tags=tag)

            self.canvas.tag_bind(tag, '<Button-1>', lambda event, i=i+1: self.on_button_click(i))
            self.buttons.append(tag)
            self.text_objects.append(text_object)


    def update_text_objects(self):
        num_sections = 8
        outer_radius = 250
        inner_radius = 150 
        border_width = 10  
        
        center_x = 300
        center_y = 300

        for i, button_tag in enumerate(self.buttons):
            start_angle = i * 360 / num_sections - 90
            text_radius = (outer_radius + inner_radius) / 2 *.92
            text_angle = math.radians(start_angle + 360 / num_sections / 2)
            text_x = center_x + text_radius * math.cos(text_angle)
            text_y = center_y + text_radius * math.sin(text_angle)
            text_object = self.canvas.create_text(text_x, text_y, text=self.get_text(i+1), fill='#FFFFFF', font=('Arial', 15), tags=button_tag)
            self.text_objects[i] = text_object 


    def reset_color(self):
        for button_tag in self.buttons:
            self.canvas.itemconfigure(button_tag, fill='blue')


    def on_button_click(self, section_number):
        self.reset_color()
        new_color = 'red'
        self.canvas.itemconfigure(self.buttons[section_number-1], fill=new_color)
        self.update_text_objects()
        self.get_info_to_paperclip(section_number)
        self.create_clipboard_label()

    def get_info_to_paperclip(self, section_number):
        pyperclip.copy(self.data[section_number])

    def get_text(self, section_number):
        value = self.get_text_by_section_number(section_number)
        if len(value) > 10:
            value = value[:7] + '...'
        return value

    def get_text_by_section_number(self, section_number):
        self.data = get_clipboard_data()
        value = self.data[section_number]
        return value

    def create_clipboard_label(self):
        if hasattr(self, 'clipboard_label'):
            self.clipboard_label.destroy()

        clipboard_frame = tk.Frame(self, bg='black')
        clipboard_frame.place(relx=0.5, rely=0.5, anchor='s')
        
        clipboard_text = "Clipboard:"
        clipboard_label = tk.Label(clipboard_frame, text=clipboard_text, bg='black', fg='white', font=('Arial', 20))
        clipboard_label.pack()

        clipboard_content = pyperclip.paste()
        if len(clipboard_content) > 35:
            clipboard_content = clipboard_content[:35] + '...'
        self.clipboard_label = tk.Label(clipboard_frame, text=clipboard_content, bg='black', fg='#aaDDFF', font=('Arial', 10))
        self.clipboard_label.pack()
        self.current_clipboard_object = self.clipboard_label    

    def create_keybind_list(self):
        keybind_frame = tk.Frame(self, bg='black')
        keybind_frame.place(relx=0.5, rely=0.65, anchor='s')
        
        keybind_label = tk.Label(keybind_frame, text="Keybinds:", bg='black', fg='white')
        keybind_label.pack()
        
        keybinds = ["Esc - minimize the application", "Tab+Space - toggle visibility"]
        for keybind in keybinds:
            keybind_item = tk.Label(keybind_frame, text=keybind, bg='black', fg='white',  font=('Arial', 8))
            keybind_item.pack()

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
            if self.input_fields_visibility:
                self.toggle_input_fields()

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