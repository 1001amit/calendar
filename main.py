import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar")
        self.root.geometry("600x400")
        self.current_date = datetime.now()
        self.events_file = "events.json"
        self.events = self.load_events()
        self.create_widgets()

    def create_widgets(self):
        # Apply a default theme
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('TLabel', font=('Helvetica', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Helvetica', 16), padding=10)
        self.style.configure('Current.TButton', foreground='red', background='lightgrey')
        self.style.configure('Weekend.TButton', foreground='blue', background='lightgrey')

        # Header
        self.header = ttk.Label(self.root, text="", style="Header.TLabel", anchor="center")
        self.header.pack(pady=10)

        # Theme selection
        self.theme_label = ttk.Label(self.root, text="Select Theme:", style="TLabel")
        self.theme_label.pack(pady=5)
        self.theme_combobox = ttk.Combobox(self.root, values=self.style.theme_names())
        self.theme_combobox.set(self.style.theme_use())
        self.theme_combobox.pack(pady=5)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)

        # Calendar frame
        self.calendar_frame = ttk.Frame(self.root)
        self.calendar_frame.pack()

        # Sidebar frame
        self.sidebar_frame = ttk.Frame(self.root)
        self.sidebar_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.event_list = tk.Listbox(self.sidebar_frame, width=30, font=('Helvetica', 10))
        self.event_list.pack()

        # Buttons frame
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

            # Highlight current date
            if (self.current_date.year, self.current_date.month, day) == (datetime.now().year, datetime.now().month, datetime.now().day):
                date_button.config(style="Current.TButton")

            # Highlight weekends
            if col == 0 or col == 6:
                date_button.config(style="Weekend.TButton")

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
        event_text = self.events.get(date, "")
        event_popup = tk.Toplevel(self.root)
        event_popup.title(f"Events on {date}")

        tk.Label(event_popup, text=f"Events on {date}", font=('Helvetica', 12)).pack(pady=5)
        event_entry = tk.Entry(event_popup, width=50, font=('Helvetica', 10))
        event_entry.pack(pady=5)
        event_entry.insert(0, event_text)

        def save_event():
            self.events[date] = event_entry.get()
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
            self.event_list.insert(tk.END, f"{date}: {event}")

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        self.style.theme_use(selected_theme)
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
        
