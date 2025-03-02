import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import requests
from PIL import Image, ImageTk
import io
from datetime import datetime

# --------------------- Pricing Dictionaries --------------------- #
ROOM_PRICES = {
    "1-Bed AC": 120,     
    "1-Bed Non-AC": 100, 
    "2-Bed AC": 180,     
    "2-Bed Non-AC": 150  
}

GAME_PRICES = {
    "Snooker": 20,   
    "Console": 15,   
    "Arcade": 10,    
    "Cricket": 25    
}

SPA_PRICES = {
    "Massage": 50,   
    "Facial": 30,    
    "Pedicure": 20   
}

POOL_PRICES = {
    "Pool Access": 10,  
}

# --------------------- Global DB Connection --------------------- #
connection = None

def connect_to_db():
    global connection
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="Your_username",
            password="Your_PAssword",
            database="hotel"
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database!")
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_next_room_number():
    """Return the next available room number from the customers table."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT IFNULL(MAX(room_number), 0) + 1 FROM customers")
        result = cursor.fetchone()
        return result[0] if result else 1
    except mysql.connector.Error as err:
        print(f"Error fetching next room number: {err}")
        return 1

# --------------------- Common Styling Functions --------------------- #
def create_title_box(parent, text):
    """Creates a title box with a light blue background."""
    frame = tk.Frame(parent, bg="#ADD8E6", padx=10, pady=5)
    label = tk.Label(frame, text=text, font=("Arial", 20, "bold"), bg="#ADD8E6", fg="black", justify="center")
    label.pack()
    return frame

def create_info_box(parent, text):
    """Creates an info/charges box with a brown background."""
    frame = tk.Frame(parent, bg="#A97C50", padx=10, pady=5)
    label = tk.Label(frame, text=text, font=("Arial", 12), bg="#A97C50", fg="white", justify="center")
    label.pack()
    return frame

def create_form_box(parent):
    """Creates and returns a white form box frame."""
    frame = tk.Frame(parent, bg="white", padx=10, pady=10)
    return frame

def bind_mousewheel(widget, canvas):
    """Bind mouse wheel scrolling to a canvas."""
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    widget.bind("<MouseWheel>", _on_mousewheel)

# --------------------- Save Functions (Defined Before Section Functions) --------------------- #
def save_game_details(game_select, room_number_entry, hours_entry, gaming_window):
    game_name = game_select.get()
    if not game_name:
        messagebox.showerror("Input Error", "Please select a game.")
        return
    room_number = room_number_entry.get()
    if not room_number:
        messagebox.showerror("Input Error", "Please enter the room number.")
        return
    try:
        num_hours = int(hours_entry.get())
        if num_hours <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of hours.")
        return
    price_per_hour = GAME_PRICES[game_name]
    total_price = num_hours * price_per_hour
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO games (game_name, total_price, room_number)
            VALUES (%s, %s, %s)
        """, (game_name, total_price, room_number))
        connection.commit()
        messagebox.showinfo("Success", f"Game: {game_name}\nHours: {num_hours}\nTotal Price: ${total_price} saved successfully!")
        gaming_window.destroy()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving game data: {err}")

def save_pool_details(room_number_entry, hours_entry, pool_window):
    room_number = room_number_entry.get()
    if not room_number:
        messagebox.showerror("Input Error", "Please enter the room number.")
        return
    try:
        num_hours = int(hours_entry.get())
        if num_hours <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of hours.")
        return
    price_per_hour = POOL_PRICES["Pool Access"]
    total_price = num_hours * price_per_hour
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO pool (total_price, room_number)
            VALUES (%s, %s)
        """, (total_price, room_number))
        connection.commit()
        messagebox.showinfo("Success", f"Pool Access: {num_hours} hours\nTotal Price: ${total_price} saved successfully!")
        pool_window.destroy()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving pool data: {err}")

def save_spa_details(service_select, room_number_entry, hours_entry, spa_window):
    spa_service = service_select.get()
    if not spa_service:
        messagebox.showerror("Input Error", "Please select a spa service.")
        return
    room_number = room_number_entry.get()
    if not room_number:
        messagebox.showerror("Input Error", "Please enter the room number.")
        return
    try:
        num_hours = int(hours_entry.get())
        if num_hours <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of hours.")
        return
    price_per_hour = SPA_PRICES[spa_service]
    total_price = num_hours * price_per_hour
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO spa (spa_service, total_price, room_number)
            VALUES (%s, %s, %s)
        """, (spa_service, total_price, room_number))
        connection.commit()
        messagebox.showinfo("Success", f"Spa Service: {spa_service}\nHours: {num_hours}\nTotal Price: ${total_price} saved successfully!")
        spa_window.destroy()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving spa data: {err}")

def generate_bill_details(room_number, parent):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT g.total_price AS game_price, p.total_price AS pool_price, s.total_price AS spa_price, r.total_room_price 
            FROM customers r 
            LEFT JOIN games g ON r.room_number = g.room_number
            LEFT JOIN pool p ON r.room_number = p.room_number
            LEFT JOIN spa s ON r.room_number = s.room_number
            WHERE r.room_number = %s
        """, (room_number,))
        results = cursor.fetchall()
        if not results:
            messagebox.showerror("No Data", "No data found for the given room number.")
            return

        total_game_price = sum([r[0] for r in results if r[0] is not None])
        total_pool_price = sum([r[1] for r in results if r[1] is not None])
        total_spa_price = sum([r[2] for r in results if r[2] is not None])
        total_room_price = results[0][3] if results[0][3] is not None else 0

        final_total = total_game_price + total_pool_price + total_spa_price + total_room_price
        tax = final_total * 0.1
        grand_total = final_total + tax

        bill_details = (
            f"Room Price: ${total_room_price}\n"
            f"Game Price: ${total_game_price}\n"
            f"Pool Price: ${total_pool_price}\n"
            f"Spa Price: ${total_spa_price}\n\n"
            f"Total: ${final_total}\n"
            f"Tax (10%): ${tax}\n"
            f"Grand Total: ${grand_total}"
        )
        details_box = create_info_box(parent, bill_details)
        details_box.pack(pady=10, anchor="center")

        paid_button = ttk.Button(parent, text="Paid", command=lambda: mark_as_paid(room_number))
        paid_button.pack(pady=10, anchor="center")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error generating final bill: {err}")

def mark_as_paid(room_number):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS previous_customers LIKE customers")
        cursor.execute("INSERT INTO previous_customers SELECT * FROM customers WHERE room_number = %s", (room_number,))
        cursor.execute("DELETE FROM customers WHERE room_number = %s", (room_number,))
        connection.commit()
        messagebox.showinfo("Success", "Payment recorded. Customer data moved to previous customers.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error processing payment: {err}")

def generate_final_bill(room_number_entry, billing_window):
    room_number = room_number_entry.get()
    if not room_number:
        messagebox.showerror("Input Error", "Please enter the room number.")
        return
    # Instead of an alert, we update the final bill window
    # Clear previous widgets in the window (if any)
    for widget in billing_window.winfo_children():
        widget.destroy()
    # Recreate the layout for the final bill
    final_frame = tk.Frame(billing_window, bg="white", padx=10, pady=10)
    final_frame.pack(fill="both", expand=True)
    title_box = create_title_box(final_frame, "Final Billing")
    title_box.pack(pady=10, anchor="center")
    form_box = create_form_box(final_frame)
    form_box.pack(pady=10, anchor="center")
    rn_label = tk.Label(form_box, text=f"Room Number: {room_number}", font=("Arial", 12), bg="white", justify="center")
    rn_label.pack(pady=5)
    generate_bill_details(room_number, final_frame)

# --------------------- Section Functions --------------------- #
def gaming_section():
    gaming_window = tk.Toplevel(root)
    gaming_window.title("Gaming Zone")
    gaming_window.geometry("600x400")

    canvas = tk.Canvas(gaming_window)
    scrollbar = ttk.Scrollbar(gaming_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    bind_mousewheel(scrollable_frame, canvas)

    title_box = create_title_box(scrollable_frame, "Gaming Zone")
    title_box.pack(pady=10, anchor="center")
    info_box = create_info_box(scrollable_frame, "Game Charges:\nSnooker: $20/hr\nConsole: $15/hr\nArcade: $10/hr\nCricket: $25/hr")
    info_box.pack(pady=5, anchor="center")
    form_box = create_form_box(scrollable_frame)
    form_box.pack(pady=10, anchor="center")

    rn_label = tk.Label(form_box, text="Enter Room Number:", font=("Arial", 12), bg="white", justify="center")
    rn_label.pack(pady=5)
    rn_entry = tk.Entry(form_box, justify="center")
    rn_entry.pack(pady=5)

    game_label = tk.Label(form_box, text="Select Game:", font=("Arial", 12), bg="white", justify="center")
    game_label.pack(pady=5)
    game_select = ttk.Combobox(form_box, values=list(GAME_PRICES.keys()), justify="center")
    game_select.pack(pady=5)

    hours_label = tk.Label(form_box, text="Enter Hours to Play:", font=("Arial", 12), bg="white", justify="center")
    hours_label.pack(pady=5)
    hours_entry = tk.Entry(form_box, justify="center")
    hours_entry.pack(pady=5)

    submit_button = ttk.Button(form_box, text="Submit",
                               command=lambda: save_game_details(game_select, rn_entry, hours_entry, gaming_window))
    submit_button.pack(pady=10)

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def pool_section():
    pool_window = tk.Toplevel(root)
    pool_window.title("Pool Zone")
    pool_window.geometry("600x400")

    canvas = tk.Canvas(pool_window)
    scrollbar = ttk.Scrollbar(pool_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    bind_mousewheel(scrollable_frame, canvas)

    title_box = create_title_box(scrollable_frame, "Pool Zone")
    title_box.pack(pady=10, anchor="center")
    info_box = create_info_box(scrollable_frame, "Pool Charges:\nPool Access: $10/hr")
    info_box.pack(pady=5, anchor="center")
    form_box = create_form_box(scrollable_frame)
    form_box.pack(pady=10, anchor="center")

    rn_label = tk.Label(form_box, text="Enter Room Number:", font=("Arial", 12), bg="white", justify="center")
    rn_label.pack(pady=5)
    rn_entry = tk.Entry(form_box, justify="center")
    rn_entry.pack(pady=5)

    hours_label = tk.Label(form_box, text="Enter Hours for Pool Access:", font=("Arial", 12), bg="white", justify="center")
    hours_label.pack(pady=5)
    hours_entry = tk.Entry(form_box, justify="center")
    hours_entry.pack(pady=5)

    submit_button = ttk.Button(form_box, text="Submit", command=lambda: save_pool_details(rn_entry, hours_entry, pool_window))
    submit_button.pack(pady=10)

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def spa_section():
    spa_window = tk.Toplevel(root)
    spa_window.title("Spa Zone")
    spa_window.geometry("600x400")

    canvas = tk.Canvas(spa_window)
    scrollbar = ttk.Scrollbar(spa_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    bind_mousewheel(scrollable_frame, canvas)

    title_box = create_title_box(scrollable_frame, "Spa Zone")
    title_box.pack(pady=10, anchor="center")
    info_box = create_info_box(scrollable_frame, "Spa Charges:\nMassage: $50/hr\nFacial: $30/hr\nPedicure: $20")
    info_box.pack(pady=5, anchor="center")
    form_box = create_form_box(scrollable_frame)
    form_box.pack(pady=10, anchor="center")

    rn_label = tk.Label(form_box, text="Enter Room Number:", font=("Arial", 12), bg="white", justify="center")
    rn_label.pack(pady=5)
    rn_entry = tk.Entry(form_box, justify="center")
    rn_entry.pack(pady=5)

    service_label = tk.Label(form_box, text="Select Spa Service:", font=("Arial", 12), bg="white", justify="center")
    service_label.pack(pady=5)
    service_select = ttk.Combobox(form_box, values=list(SPA_PRICES.keys()), justify="center")
    service_select.pack(pady=5)

    hours_label = tk.Label(form_box, text="Enter Hours for Spa Service:", font=("Arial", 12), bg="white", justify="center")
    hours_label.pack(pady=5)
    hours_entry = tk.Entry(form_box, justify="center")
    hours_entry.pack(pady=5)

    submit_button = ttk.Button(form_box, text="Submit", command=lambda: save_spa_details(service_select, rn_entry, hours_entry, spa_window))
    submit_button.pack(pady=10)

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def final_billing():
    billing_window = tk.Toplevel(root)
    billing_window.title("Final Billing")
    billing_window.geometry("600x700")

    canvas = tk.Canvas(billing_window)
    scrollbar = ttk.Scrollbar(billing_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    bind_mousewheel(scrollable_frame, canvas)

    title_box = create_title_box(scrollable_frame, "Final Billing")
    title_box.pack(pady=10, anchor="center")
    form_box = create_form_box(scrollable_frame)
    form_box.pack(pady=10, anchor="center")

    rn_label = tk.Label(form_box, text="Enter Room Number:", font=("Arial", 12), bg="white", justify="center")
    rn_label.pack(pady=5)
    rn_entry = tk.Entry(form_box, justify="center")
    rn_entry.pack(pady=5)

    generate_button = ttk.Button(form_box, text="Generate Final Bill", command=lambda: generate_bill_details(rn_entry.get(), scrollable_frame))
    generate_button.pack(pady=10)

    canvas.config(scrollregion=canvas.bbox("all"))

# --------------------- Reception Section --------------------- #
class Reception:
    def __init__(self, root):
        self.root = root
        self.root.title("Reception")
        self.root.geometry("600x700")

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.form_frame = self.get_form_frame()
        self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        self.form_frame.bind("<Configure>", self.on_frame_configure)
        bind_mousewheel(self.form_frame, self.canvas)

    def get_form_frame(self):
        frame = tk.Frame(self.canvas)

        title_box = create_title_box(frame, "Reception")
        title_box.pack(pady=10, anchor="center")

        info_box = create_info_box(frame, "Room Prices:\n1-Bed AC: $120\n1-Bed Non-AC: $100\n2-Bed AC: $180\n2-Bed Non-AC: $150")
        info_box.pack(pady=5, anchor="center")

        self.input_frame = create_form_box(frame)
        self.input_frame.pack(pady=10, anchor="center")

        self.room_type_label = tk.Label(self.input_frame, text="Select Room Type:", font=("Arial", 12), bg="white", justify="center")
        self.room_type_label.pack(pady=5)
        self.room_type = tk.StringVar(value="1-Bed AC")
        radio_frame = tk.Frame(self.input_frame, bg="white")
        radio_frame.pack(anchor="center")
        tk.Radiobutton(radio_frame, text="1-Bed AC", variable=self.room_type, value="1-Bed AC", bg="white", justify="center").pack(side="left", padx=5)
        tk.Radiobutton(radio_frame, text="1-Bed Non-AC", variable=self.room_type, value="1-Bed Non-AC", bg="white", justify="center").pack(side="left", padx=5)
        tk.Radiobutton(radio_frame, text="2-Bed AC", variable=self.room_type, value="2-Bed AC", bg="white", justify="center").pack(side="left", padx=5)
        tk.Radiobutton(radio_frame, text="2-Bed Non-AC", variable=self.room_type, value="2-Bed Non-AC", bg="white", justify="center").pack(side="left", padx=5)

        self.add_input_field("Guest Name:")
        self.add_input_field("Age:")
        self.add_input_field("Aadhar Card Number:")
        self.add_input_field("Number of People:")
        self.add_input_field("Check-In Date (YYYY-MM-DD):")
        self.add_input_field("Check-Out Date (YYYY-MM-DD):")

        btn_frame = tk.Frame(frame, bg="")
        btn_frame.pack(pady=10, anchor="center")
        style = ttk.Style()
        style.configure("Reception.TButton", font=("Arial", 12), padding=5)
        self.submit_button = ttk.Button(btn_frame, text="Submit", command=self.submit_booking, style="Reception.TButton", width=10)
        self.submit_button.pack(side="left", padx=10)
        self.back_button = ttk.Button(btn_frame, text="Back", command=self.go_back, style="Reception.TButton", width=10)
        self.back_button.pack(side="left", padx=10)

        return frame

    def add_input_field(self, label_text):
        label = tk.Label(self.input_frame, text=label_text, font=("Arial", 12), bg="white", justify="center")
        label.pack(pady=5)
        entry = ttk.Entry(self.input_frame, width=30, justify="center")
        entry.pack(pady=5)
        key = (label_text.replace(" ", "_")
                        .replace("(", "")
                        .replace(")", "")
                        .replace(":", "")
                        .replace("-", "_")
                        .lower())
        setattr(self, key + "_entry", entry)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def submit_booking(self):
        room_type = self.room_type.get()
        guest_name = self.guest_name_entry.get()
        age_str = self.age_entry.get()
        aadhar = self.aadhar_card_number_entry.get()
        people_str = self.number_of_people_entry.get()
        check_in_str = self.check_in_date_yyyy_mm_dd_entry.get()
        check_out_str = self.check_out_date_yyyy_mm_dd_entry.get()

        if not guest_name or not age_str or not aadhar or not people_str or not check_in_str or not check_out_str:
            messagebox.showerror("Input Error", "Please fill all fields.")
            return
        if room_type not in ROOM_PRICES:
            messagebox.showerror("Input Error", "Please select a valid room type.")
            return
        try:
            age = int(age_str)
            number_of_people = int(people_str)
        except ValueError:
            messagebox.showerror("Input Error", "Age and Number of People must be integers.")
            return
        try:
            check_in_date = datetime.strptime(check_in_str, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Dates must be in YYYY-MM-DD format.")
            return
        days_stay = (check_out_date - check_in_date).days
        if days_stay < 1:
            messagebox.showerror("Date Error", "Check-Out date must be after Check-In date.")
            return
        price_per_night = ROOM_PRICES[room_type]
        total_price = days_stay * price_per_night
        next_room_num = get_next_room_number()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO customers
                (name, age, aadhar, number_of_people, check_in, check_out, number_of_days,
                 room_type, room_number, total_room_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                guest_name, age, aadhar, number_of_people,
                check_in_date.strftime("%Y-%m-%d"),
                check_out_date.strftime("%Y-%m-%d"),
                days_stay,
                room_type,
                next_room_num,
                total_price
            ))
            connection.commit()
            messagebox.showinfo("Success", f"Room #{next_room_num} booked successfully for {guest_name}!\nTotal Price for {days_stay} night(s): ${total_price}")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error booking room: {err}")

    def go_back(self):
        self.root.destroy()

# --------------------- Main Menu --------------------- #
class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        self.root.geometry("600x400")

        bg_url = "https://plus.unsplash.com/premium_photo-1738503913441-492589911717?w=500&auto=format&fit=crop&q=60"
        response = requests.get(bg_url)
        img_data = response.content
        bg_image = Image.open(io.BytesIO(img_data))
        bg_image = bg_image.resize((600, 400), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.title_label = tk.Label(self.root, text="Welcome to Hotel NY", font=("Arial", 20, "bold"),
                                     bg="white", fg="black", bd=2, relief="raised", padx=10, pady=5, justify="center")
        self.title_label.pack(pady=20)

        style = ttk.Style()
        style.configure("Menu.TButton", font=("Arial", 12), padding=6)

        self.reception_button = ttk.Button(self.root, text="Reception", command=self.go_to_reception, style="Menu.TButton")
        self.reception_button.pack(pady=5)
        self.game_button = ttk.Button(self.root, text="Gaming", command=gaming_section, style="Menu.TButton")
        self.game_button.pack(pady=5)
        self.spa_button = ttk.Button(self.root, text="Spa", command=spa_section, style="Menu.TButton")
        self.spa_button.pack(pady=5)
        self.pool_button = ttk.Button(self.root, text="Pool", command=pool_section, style="Menu.TButton")
        self.pool_button.pack(pady=5)
        self.billing_button = ttk.Button(self.root, text="Total Bill", command=final_billing, style="Menu.TButton")
        self.billing_button.pack(pady=5)

    def go_to_reception(self):
        reception_window = tk.Toplevel(self.root)
        Reception(reception_window)

# --------------------- Main Execution --------------------- #
if __name__ == "__main__":
    connection = connect_to_db()
    if connection:
        root = tk.Tk()
        menu = MainMenu(root)
        root.mainloop()
    else:
        print("Error: Could not connect to the database.")
