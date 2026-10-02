import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Change to your MySQL password (e.g., 'root123' or '')
    'database': 'salon_db'
}

# --- DATABASE SETUP & CONNECTOR ---
def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS salon_db;")
        cursor.execute("USE salon_db;")
        
        # Appointments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                phone VARCHAR(15) NOT NULL,
                service_type VARCHAR(50) NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT chk_phone CHECK (phone REGEXP '^[0-9+ -]+$')
            );
        """)

        # Users Table (for Authentication)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            );
        """)

        # Insert default admin account if table is empty
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123');")

        conn.commit()
        conn.close()
    except Error as e:
        messagebox.showerror("Database Config Error", f"Could not connect to MySQL:\n{e}\n\nPlease check your MySQL configuration.")

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
        return None

# --- AUTHENTICATION DATABASE OPERATIONS ---
def verify_login(username, password):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        return cursor.fetchone() is not None
    except Error as e:
        messagebox.showerror("Error", f"Authentication failed: {e}")
        return False
    finally:
        conn.close()

def register_user(username, password):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Error", f"Registration failed (Username may already exist): {e}")
        return False
    finally:
        conn.close()

# --- APPOINTMENTS CRUD OPERATIONS ---
def create_appointment(name, phone, service, date_str, time_str):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = """INSERT INTO appointments (customer_name, phone, service_type, appointment_date, appointment_time) 
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (name, phone, service, date_str, time_str))
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Error", f"Failed to insert record: {e}")
        return False
    finally:
        conn.close()

def fetch_all_appointments():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT appointment_id, customer_name, phone, service_type, appointment_date, appointment_time, status FROM appointments")
        return cursor.fetchall()
    except Error as e:
        messagebox.showerror("Error", f"Failed to fetch records: {e}")
        return []
    finally:
        conn.close()

def update_appointment(app_id, name, phone, service, date_str, time_str, status):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = """UPDATE appointments 
                   SET customer_name=%s, phone=%s, service_type=%s, appointment_date=%s, appointment_time=%s, status=%s 
                   WHERE appointment_id=%s"""
        cursor.execute(query, (name, phone, service, date_str, time_str, status, app_id))
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Error", f"Failed to update record: {e}")
        return False
    finally:
        conn.close()

def delete_appointment(app_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE appointment_id=%s", (app_id,))
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Error", f"Failed to delete record: {e}")
        return False
    finally:
        conn.close()

# --- AUTHENTICATION WINDOW (LOGIN PAGE) ---
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("System Access - Authentication")
        self.root.geometry("380x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f6f8")

        # Header Title
        header = tk.Frame(self.root, bg="#0d233a", height=60)
        header.pack(fill=tk.X)
        
        lbl_title = tk.Label(
            header, text="⚡ System Access", font=("Arial", 16, "bold"),
            fg="#00aaff", bg="#0d233a"
        )
        lbl_title.pack(pady=15)

        # Form Container
        form_frame = tk.Frame(self.root, bg="#f4f6f8", padx=25, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Username Input
        tk.Label(form_frame, text="Username:", font=("Arial", 10, "bold"), bg="#f4f6f8", anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.ent_username = tk.Entry(form_frame, font=("Arial", 11), relief=tk.SOLID, bd=1)
        self.ent_username.pack(fill=tk.X, ipady=4, pady=(0, 15))

        # Password Input
        tk.Label(form_frame, text="Password:", font=("Arial", 10, "bold"), bg="#f4f6f8", anchor="w").pack(fill=tk.X, pady=(0, 2))
        self.ent_password = tk.Entry(form_frame, font=("Arial", 11), show="*", relief=tk.SOLID, bd=1)
        self.ent_password.pack(fill=tk.X, ipady=4, pady=(0, 20))

        # Buttons
        btn_login = tk.Button(
            form_frame, text="Login", font=("Arial", 11, "bold"),
            bg="#27ae60", fg="white", activebackground="#219150",
            activeforeground="white", bd=0, cursor="hand2", command=self.handle_login
        )
        btn_login.pack(fill=tk.X, ipady=6, pady=(0, 10))

        btn_register = tk.Button(
            form_frame, text="Register New Account", font=("Arial", 11, "bold"),
            bg="#2980b9", fg="white", activebackground="#1f6391",
            activeforeground="white", bd=0, cursor="hand2", command=self.handle_register
        )
        btn_register.pack(fill=tk.X, ipady=6, pady=(0, 20))

        # Default Credentials Hint Label
        lbl_hint = tk.Label(
            form_frame, text="Default Admin: admin / admin123",
            font=("Arial", 9, "italic"), fg="#7f8c8d", bg="#f4f6f8"
        )
        lbl_hint.pack()

    def handle_login(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password.")
            return

        if verify_login(username, password):
            messagebox.showinfo("Success", "Login Successful!")
            self.root.destroy()  # Close login window
            open_main_app()      # Launch salon management window
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def handle_register(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password to register.")
            return

        if register_user(username, password):
            messagebox.showinfo("Success", "Account created! You can now log in.")
            self.ent_password.delete(0, tk.END)

# --- MAIN TKINTER SALON APP ---
class SalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Salon Appointment Management System")
        self.root.geometry("900x550")

        self.selected_id = None
        self.var_name = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_service = tk.StringVar()
        self.var_date = tk.StringVar()
        self.var_time = tk.StringVar()
        self.var_status = tk.StringVar(value="Scheduled")

        # Header
        title = tk.Label(self.root, text="Salon Appointment System", font=("Arial", 18, "bold"), bg="#4A90E2", fg="white", pady=10)
        title.pack(fill=tk.X)

        # Layout Container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel (Inputs)
        left_frame = tk.LabelFrame(main_frame, text="Appointment Details", font=("Arial", 11, "bold"), padx=10, pady=10)
        left_frame.place(x=10, y=10, width=320, height=450)

        tk.Label(left_frame, text="Customer Name:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(left_frame, textvariable=self.var_name, width=22).grid(row=0, column=1, pady=5)

        tk.Label(left_frame, text="Phone Number:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(left_frame, textvariable=self.var_phone, width=22).grid(row=1, column=1, pady=5)

        tk.Label(left_frame, text="Service:").grid(row=2, column=0, sticky="w", pady=5)
        services = ["Haircut", "Hair Coloring", "Facial", "Manicure/Pedicure", "Spa/Massage"]
        ttk.Combobox(left_frame, textvariable=self.var_service, values=services, width=20, state="readonly").grid(row=2, column=1, pady=5)

        tk.Label(left_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(left_frame, textvariable=self.var_date, width=22).grid(row=3, column=1, pady=5)

        tk.Label(left_frame, text="Time (HH:MM):").grid(row=4, column=0, sticky="w", pady=5)
        tk.Entry(left_frame, textvariable=self.var_time, width=22).grid(row=4, column=1, pady=5)

        tk.Label(left_frame, text="Status:").grid(row=5, column=0, sticky="w", pady=5)
        ttk.Combobox(left_frame, textvariable=self.var_status, values=["Scheduled", "Completed", "Cancelled"], width=20, state="readonly").grid(row=5, column=1, pady=5)

        # Buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="Book", command=self.add_record, bg="#2ecc71", fg="white", width=8).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="Update", command=self.update_record, bg="#3498db", fg="white", width=8).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame, text="Delete", command=self.delete_record, bg="#e74c3c", fg="white", width=8).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame, text="Clear", command=self.clear_fields, bg="#95a5a6", fg="white", width=8).grid(row=1, column=1, padx=2, pady=2)

        # Right Panel (Treeview Table)
        right_frame = tk.Frame(main_frame)
        right_frame.place(x=340, y=10, width=530, height=450)

        scroll_y = tk.Scrollbar(right_frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(right_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            right_frame, 
            columns=("ID", "Name", "Phone", "Service", "Date", "Time", "Status"),
            xscrollcommand=scroll_x.set, 
            yscrollcommand=scroll_y.set
        )

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        cols = [("ID", 30), ("Name", 100), ("Phone", 80), ("Service", 100), ("Date", 75), ("Time", 60), ("Status", 75)]
        for col_name, width in cols:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width)

        self.tree["show"] = "headings"
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<ButtonRelease-1>", self.get_selected_row)
        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in fetch_all_appointments():
            self.tree.insert("", tk.END, values=row)

    def add_record(self):
        if not self.var_name.get() or not self.var_phone.get() or not self.var_service.get():
            messagebox.showwarning("Validation Error", "Name, Phone, and Service are required.")
            return

        if create_appointment(self.var_name.get(), self.var_phone.get(), self.var_service.get(), self.var_date.get(), self.var_time.get()):
            messagebox.showinfo("Success", "Appointment booked successfully.")
            self.load_data()
            self.clear_fields()

    def get_selected_row(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            content = self.tree.item(selected_item)
            row = content["values"]
            if row:
                self.selected_id = row[0]
                self.var_name.set(row[1])
                self.var_phone.set(str(row[2]))
                self.var_service.set(row[3])
                self.var_date.set(row[4])
                self.var_time.set(row[5])
                self.var_status.set(row[6])

    def update_record(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select an appointment to update.")
            return

        if update_appointment(self.selected_id, self.var_name.get(), self.var_phone.get(), self.var_service.get(), self.var_date.get(), self.var_time.get(), self.var_status.get()):
            messagebox.showinfo("Success", "Appointment updated successfully.")
            self.load_data()
            self.clear_fields()

    def delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("Selection Error", "Please select an appointment to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this appointment?"):
            if delete_appointment(self.selected_id):
                messagebox.showinfo("Success", "Appointment deleted successfully.")
                self.load_data()
                self.clear_fields()

    def clear_fields(self):
        self.selected_id = None
        self.var_name.set("")
        self.var_phone.set("")
        self.var_service.set("")
        self.var_date.set("")
        self.var_time.set("")
        self.var_status.set("Scheduled")

# --- APPLICATION LAUNCH HANDLER ---
def open_main_app():
    main_win = tk.Tk()
    app = SalonApp(main_win)
    main_win.mainloop()

if __name__ == "__main__":
    init_db()  # Initialize database & tables
    
    # Launch authentication window
    login_win = tk.Tk()
    auth_app = LoginWindow(login_win)
    login_win.mainloop()