import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from datetime import datetime, timedelta
import json
import os

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar")
        self.root.geometry("800x600")
        self.current_date = datetime.now()
        self.events_file = "events.json"
        self.events = self.load_events()
        self.create_widgets()

    def create_widgets(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('TLabel', font=('Helvetica', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Helvetica', 16), padding=10)
        self.style.configure('Current.TButton', foreground='red', background='lightgrey')
        self.style.configure('Weekend.TButton', foreground='blue', background='lightgrey')

        self.header = ttk.Label(self.root, text="", style="Header.TLabel", anchor="center")
        self.header.pack(pady=10)

        self.theme_label = ttk.Label(self.root, text="Select Theme:", style="TLabel")
        self.theme_label.pack(pady=5)
        self.theme_combobox = ttk.Combobox(self.root, values=self.style.theme_names())
        self.theme_combobox.set(self.style.theme_use())
        self.theme_combobox.pack(pady=5)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)

        self.mode_label = ttk.Label(self.root, text="Select Mode:", style="TLabel")
        self.mode_label.pack(pady=5)
        self.mode_combobox = ttk.Combobox(self.root, values=["Light", "Dark"])
        self.mode_combobox.set("Light")
        self.mode_combobox.pack(pady=5)
        self.mode_combobox.bind("<<ComboboxSelected>>", self.change_mode)

        self.calendar_frame = ttk.Frame(self.root)
        self.calendar_frame.pack()

        self.sidebar_frame = ttk.Frame(self.root)
        self.sidebar_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.event_list = tk.Listbox(self.sidebar_frame, width=50, font=('Helvetica', 10))
        self.event_list.pack()

        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(pady=10)

        self.prev_button = ttk.Button(self.buttons_frame, text="<<", command=self.show_prev_month)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = ttk.Button(self.buttons_frame, text=">>", command=self.show_next_month)
        self.next_button.grid(row=0, column=1, padx=5)

        self.update_event_list()
        self.draw_calendar()

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header.config(text=self.current_date.strftime("%B %Y"))

        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for idx, day in enumerate(days_of_week):
            ttk.Label(self.calendar_frame, text=day, style="TLabel").grid(row=0, column=idx)

        first_day_of_month = self.current_date.replace(day=1)
        start_day = first_day_of_month.weekday()
        if start_day == 6:
            start_day = -1

        days_in_month = (first_day_of_month.replace(month=self.current_date.month % 12 + 1, day=1) - timedelta(days=1)).day
        for day in range(1, days_in_month + 1):
            row = (day + start_day) // 7 + 1
            col = (day + start_day) % 7
            date_button = ttk.Button(self.calendar_frame, text=str(day), command=lambda d=day: self.show_event_popup(d))
            date_button.grid(row=row, column=col, padx=5, pady=5)

            if (self.current_date.year, self.current_date.month, day) == (datetime.now().year, datetime.now().month, datetime.now().day):
                date_button.config(style="Current.TButton")

            if col == 0 or col == 6:
                date_button.config(style="Weekend.TButton")

            event_date = self.current_date.replace(day=day).strftime("%Y-%m-%d")
            if event_date in self.events:
                color = self.events[event_date].get('color', '')
                if color:
                    date_button.config(style="", background=color)

    def show_prev_month(self):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.current_date = self.current_date.replace(day=1)
        self.draw_calendar()
        self.update_event_list()

    def show_next_month(self):
        self.current_date = self.current_date.replace(day=1) + timedelta(days=32)
        self.current_date = self.current_date.replace(day=1)
        self.draw_calendar()
        self.update_event_list()

    def show_event_popup(self, day):
        date = self.current_date.replace(day=day).strftime("%Y-%m-%d")
        event_text = self.events.get(date, {}).get('text', '')
        event_color = self.events.get(date, {}).get('color', '#ffffff')
        event_popup = tk.Toplevel(self.root)
        event_popup.title(f"Events on {date}")

        tk.Label(event_popup, text=f"Events on {date}", font=('Helvetica', 12)).pack(pady=5)
        event_entry = tk.Entry(event_popup, width=50, font=('Helvetica', 10))
        event_entry.pack(pady=5)
        event_entry.insert(0, event_text)

        color_label = tk.Label(event_popup, text="Event Color:", font=('Helvetica', 10))
        color_label.pack(pady=5)
        color_button = tk.Button(event_popup, text="Select Color", bg=event_color, command=lambda: self.pick_color(event_popup, color_button))
        color_button.pack(pady=5)

        def save_event():
            self.events[date] = {
                "text": event_entry.get(),
                "color": color_button.cget('bg')
            }
            self.save_events()
            self.update_event_list()
            event_popup.destroy()

        def delete_event():
            if date in self.events:
                del self.events[date]
                self.save_events()
                self.update_event_list()
                event_popup.destroy()

        save_button = ttk.Button(event_popup, text="Save", command=save_event)
        save_button.pack(pady=5)

        delete_button = ttk.Button(event_popup, text="Delete", command=delete_event)
        delete_button.pack(pady=5)

    def update_event_list(self):
        self.event_list.delete(0, tk.END)
        month_events = {date: event for date, event in self.events.items() if self.current_date.strftime("%Y-%m") in date}
        for date, event in sorted(month_events.items()):
            self.event_list.insert(tk.END, f"{date}: {event['text']}")

    def pick_color(self, popup, button):
        color_code = colorchooser.askcolor(title="Choose color")
        if color_code:
            button.config(bg=color_code[1])

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        self.style.theme_use(selected_theme)
        self.draw_calendar()
        self.update_event_list()

    def change_mode(self, event):
        selected_mode = self.mode_combobox.get()
        if selected_mode == "Dark":
            self.root.tk_setPalette(background="#2e2e2e", foreground="#ffffff")
            self.style.configure('TLabel', background="#2e2e2e", foreground="#ffffff")
            self.style.configure('TButton', background="#555555", foreground="#ffffff")
            self.style.configure('Header.TLabel', background="#2e2e2e", foreground="#ffffff")
        else:
            self.root.tk_setPalette(background="#ffffff", foreground="#000000")
            self.style.configure('TLabel', background="#ffffff", foreground="#000000")
            self.style.configure('TButton', background="#f0f0f0", foreground="#000000")
            self.style.configure('Header.TLabel', background="#ffffff", foreground="#000000")
        self.draw_calendar()
        self.update_event_list()

    def load_events(self):
        if os.path.exists(self.events_file):
            with open(self.events_file, "r") as file:
                return json.load(file)
        return {}

    def save_events(self):
        with open(self.events_file, "w") as file:
            json.dump(self.events, file)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
