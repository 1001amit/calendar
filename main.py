import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar")
        self.current_date = datetime.now()
        self.create_widgets()

    def create_widgets(self):
        self.header = ttk.Label(self.root, text="", anchor="center")
        self.header.pack(pady=10)

        self.calendar_frame = ttk.Frame(self.root)
        self.calendar_frame.pack()

        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(pady=10)

        self.prev_button = ttk.Button(self.buttons_frame, text="<<", command=self.show_prev_month)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = ttk.Button(self.buttons_frame, text=">>", command=self.show_next_month)
        self.next_button.grid(row=0, column=1, padx=5)

        self.draw_calendar()

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.header.config(text=self.current_date.strftime("%B %Y"))

        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for idx, day in enumerate(days_of_week):
            ttk.Label(self.calendar_frame, text=day).grid(row=0, column=idx)

        first_day_of_month = self.current_date.replace(day=1)
        start_day = first_day_of_month.weekday()
        if start_day == 6:
            start_day = -1

        days_in_month = (first_day_of_month.replace(month=self.current_date.month % 12 + 1, day=1) - timedelta(days=1)).day
        for day in range(1, days_in_month + 1):
            row = (day + start_day) // 7 + 1
            col = (day + start_day) % 7
            ttk.Button(self.calendar_frame, text=str(day)).grid(row=row, column=col, padx=5, pady=5)

    def show_prev_month(self):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.current_date = self.current_date.replace(day=1)
        self.draw_calendar()

    def show_next_month(self):
        self.current_date = self.current_date.replace(day=1) + timedelta(days=32)
        self.current_date = self.current_date.replace(day=1)
        self.draw_calendar()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
      
