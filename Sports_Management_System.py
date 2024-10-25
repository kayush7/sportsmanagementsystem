import mysql.connector 
import customtkinter as ctk
import hashlib
from tkinter import messagebox, Listbox, Scrollbar

class SportsManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sports Management System")
        self.geometry("800x600")

        # Database connection
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='my5ql2420',
            database='sp1'  # Ensure this matches the database name
        )
        self.cursor = self.connection.cursor()

        self.create_tables()
        self.login_popup()

        # Dictionary for sport positions
        self.positions_dict = {
            "Football": ["Forward", "Midfielder", "Defender", "Goalkeeper"],
            "Basketball": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
            "Volleyball": ["Outside Hitter", "Setter", "Libero", "Middle Blocker", "Opposite Hitter"],
            "Cricket": ["Batsman", "Bowler", "All-rounder", "Wicketkeeper"],
            "Tennis": ["Singles Player", "Doubles Player"]
        }

    def create_tables(self):
        # Create tables if they don't exist
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                sport VARCHAR(255) NOT NULL,
                position VARCHAR(255) NOT NULL,
                age INT NOT NULL CHECK (age > 0)
            )
        """)
        
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS statistics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                player_id INT NOT NULL,
                sport VARCHAR(255) NOT NULL,
                matches_played INT NOT NULL CHECK (matches_played >= 0),
                goals_points_runs_scored INT DEFAULT 0 CHECK (goals_points_runs_scored >= 0),
                assists_wickets_aces_given INT DEFAULT 0 CHECK (assists_wickets_aces_given >= 0),
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
            )
        """)
        
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                player_id INT,
                reminder_date DATE NOT NULL,
                reminder_text VARCHAR(255) NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
            )
        """)

        # Create items table
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(255) NOT NULL,
                description VARCHAR(255),
                quantity INT NOT NULL CHECK (quantity >= 0),
                unit_price DECIMAL(10, 2) NOT NULL,
                supplier_name VARCHAR(255) NOT NULL,
                item_condition VARCHAR(255) NOT NULL
            )
        """)

    def login_popup(self):
        # Create login popup window
        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Login / Register")
        self.popup.geometry("300x200")

        self.username_entry = ctk.CTkEntry(self.popup, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.popup, placeholder_text="Password", show='*')
        self.password_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self.popup, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        self.register_button = ctk.CTkButton(self.popup, text="Register", command=self.register)
        self.register_button.pack(pady=5)

        self.popup.grab_set()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username = self.username_entry.get()
        password = self.hash_password(self.password_entry.get())

        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        self.cursor.execute(query, (username, password))
        user = self.cursor.fetchone()

        if user:
            self.popup.destroy()
            self.create_widgets()
        else:
            messagebox.showerror("Login failed", "Invalid username or password. Please try again.")

    def register(self):
        username = self.username_entry.get()
        password = self.hash_password(self.password_entry.get())

        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (username, password))
            self.connection.commit()
            messagebox.showinfo("Registration successful", "You can now log in.")
        except mysql.connector.Error as err:
            messagebox.showerror("Registration failed", f"Error: {str(err)}")

    def create_widgets(self):
    # Create main application tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill='both')

        self.player_management_tab = self.tab_view.add("Player Management")
        self.statistics_tab = self.tab_view.add("Player Statistics")
        self.item_management_tab = self.tab_view.add("Item Management")  
        self.view_players_tab = self.tab_view.add("View All Players")
        self.view_statistics_tab = self.tab_view.add("View Player Stats")
        self.reminders_tab = self.tab_view.add("Manage Reminders")
        self.view_reminders_tab = self.tab_view.add("View Reminders")
        self.view_items_tab = self.tab_view.add("View Items")  # New View Items Tab

        self.create_player_management_widgets()
        self.create_statistics_widgets()
        self.create_item_management_widgets()
        self.create_view_players_widgets()
        self.create_view_statistics_widgets()
        self.create_reminders_widgets()
        self.create_view_reminders_widgets()
        self.create_view_items_widgets()  # Initialize View Items Widgets


    def create_view_items_widgets(self):
        self.view_items_listbox = Listbox(self.view_items_tab, height=20, font=("Arial", 14))
        self.view_items_listbox.pack(pady=(10, 5), fill='both', expand=True)

        self.refresh_button = ctk.CTkButton(self.view_items_tab, text="Refresh Items List", command=self.view_all_items)
        self.refresh_button.pack(pady=(5, 5))

        self.view_all_items()

    def view_all_items(self):
        self.view_items_listbox.delete(0, 'end')
        self.cursor.execute("SELECT * FROM items")
        for row in self.cursor.fetchall():
            self.view_items_listbox.insert('end', f"ID: {row[0]}, Name: {row[1]}, Category: {row[2]}, Quantity: {row[4]}, Price: {row[5]}")


    def create_item_management_widgets(self):
        self.item_name_entry = ctk.CTkEntry(self.item_management_tab, placeholder_text="Item Name")
        self.item_name_entry.pack(pady=(10, 5))

        self.category_label = ctk.CTkLabel(self.item_management_tab, text="Select Category:")
        self.category_label.pack(pady=(10, 5))

        self.category_combobox = ctk.CTkComboBox(
            self.item_management_tab,
            values=["equipment", "uniform", "accessories"]
        )
        self.category_combobox.pack(pady=(0, 5))

        self.description_entry = ctk.CTkEntry(self.item_management_tab, placeholder_text="Description")
        self.description_entry.pack(pady=(10, 5))

        self.quantity_entry = ctk.CTkEntry(self.item_management_tab, placeholder_text="Quantity")
        self.quantity_entry.pack(pady=(10, 5))

        self.unit_price_entry = ctk.CTkEntry(self.item_management_tab, placeholder_text="Unit Price")
        self.unit_price_entry.pack(pady=(10, 5))

        self.supplier_name_entry = ctk.CTkEntry(self.item_management_tab, placeholder_text="Supplier Name")
        self.supplier_name_entry.pack(pady=(10, 5))

        self.item_condition_label = ctk.CTkLabel(self.item_management_tab, text="Select Condition:")
        self.item_condition_label.pack(pady=(10, 5))

        self.item_condition_combobox = ctk.CTkComboBox(
            self.item_management_tab,
            values=["new", "good", "worn out", "under repair"]
        )
        self.item_condition_combobox.pack(pady=(0, 5))

        self.add_item_button = ctk.CTkButton(self.item_management_tab, text="Add Item", command=self.add_item)
        self.add_item_button.pack(pady=(5, 5))

        self.update_item_button = ctk.CTkButton(self.item_management_tab, text="Update Item", command=self.update_item)
        self.update_item_button.pack(pady=(5, 5))

        self.delete_item_button = ctk.CTkButton(self.item_management_tab, text="Delete Item", command=self.delete_item)
        self.delete_item_button.pack(pady=(5, 5))

        self.item_id_label = ctk.CTkLabel(self.item_management_tab, text="Item ID (for update/delete):")
        self.item_id_label.pack(pady=(10, 5))

        self.item_id_entry = ctk.CTkEntry(self.item_management_tab, placeholder_text="Item ID")
        self.item_id_entry.pack(pady=(0, 10))

    def add_item(self):
        name = self.item_name_entry.get()
        category = self.category_combobox.get()
        description = self.description_entry.get()
        quantity = self.quantity_entry.get()
        unit_price = self.unit_price_entry.get()
        supplier_name = self.supplier_name_entry.get()
        item_condition = self.item_condition_combobox.get()

        if not all([name, category, description, quantity, unit_price, supplier_name, item_condition]):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            quantity = int(quantity)
            unit_price = float(unit_price)
            if quantity < 0 or unit_price < 0:
                raise ValueError("Quantity and Unit price must be non-negative.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        query = """
            INSERT INTO items (name, category, description, quantity, unit_price, supplier_name, item_condition)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (name, category, description, quantity, unit_price, supplier_name, item_condition))
        self.connection.commit()
        messagebox.showinfo("Success", "Item added successfully!")

    def update_item(self):
        item_id = self.item_id_entry.get()
        name = self.item_name_entry.get()
        category = self.category_combobox.get()
        description = self.description_entry.get()
        quantity = self.quantity_entry.get()
        unit_price = self.unit_price_entry.get()
        supplier_name = self.supplier_name_entry.get()
        item_condition = self.item_condition_combobox.get()

        if not all([item_id, name, category, description, quantity, unit_price, supplier_name, item_condition]):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            item_id = int(item_id)
            quantity = int(quantity)
            unit_price = float(unit_price)
            if quantity < 0 or unit_price < 0:
                raise ValueError("Quantity and Unit price must be non-negative.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        query = """
            UPDATE items 
            SET name=%s, category=%s, description=%s, quantity=%s, unit_price=%s, supplier_name=%s, item_condition=%s 
            WHERE id=%s
        """
        self.cursor.execute(query, (name, category, description, quantity, unit_price, supplier_name, item_condition, item_id))
        self.connection.commit()
        messagebox.showinfo("Success", "Item updated successfully!")

    def delete_item(self):
        item_id = self.item_id_entry.get()

        if not item_id:
            messagebox.showerror("Error", "Item ID must be filled!")
            return

        try:
            item_id = int(item_id)
        except ValueError:
            messagebox.showerror("Error", "Invalid Item ID.")
            return

        query = "DELETE FROM items WHERE id=%s"
        self.cursor.execute(query, (item_id,))
        self.connection.commit()
        messagebox.showinfo("Success", "Item deleted successfully!")

    def create_player_management_widgets(self):
        # Player Management Widgets
        self.name_entry = ctk.CTkEntry(self.player_management_tab, placeholder_text="Player Name")
        self.name_entry.pack(pady=(10, 5))

        self.sport_label = ctk.CTkLabel(self.player_management_tab, text="Select Sport:")
        self.sport_label.pack(pady=(10, 5))

        self.sport_combobox = ctk.CTkComboBox(
            self.player_management_tab,
            values=list(self.positions_dict.keys()),
            command=self.update_position_options
        )
        self.sport_combobox.pack(pady=(0, 5))

        self.position_label = ctk.CTkLabel(self.player_management_tab, text="Select Position:")
        self.position_label.pack(pady=(10, 5))

        self.position_combobox = ctk.CTkComboBox(self.player_management_tab, values=[])
        self.position_combobox.pack(pady=(0, 5))

        self.age_label = ctk.CTkLabel(self.player_management_tab, text="Age:")
        self.age_label.pack(pady=(10, 5))

        self.age_entry = ctk.CTkEntry(self.player_management_tab, placeholder_text="Age")
        self.age_entry.pack(pady=(0, 10))

        self.add_button = ctk.CTkButton(self.player_management_tab, text="Add Player", command=self.add_player)
        self.add_button.pack(pady=(5, 5))

        self.update_button = ctk.CTkButton(self.player_management_tab, text="Update Player", command=self.update_player)
        self.update_button.pack(pady=(5, 5))

        self.delete_button = ctk.CTkButton(self.player_management_tab, text="Delete Player", command=self.delete_player)
        self.delete_button.pack(pady=(5, 5))

        self.player_id_label = ctk.CTkLabel(self.player_management_tab, text="Player ID (for update/delete):")
        self.player_id_label.pack(pady=(10, 5))

        self.player_id_entry = ctk.CTkEntry(self.player_management_tab, placeholder_text="Player ID")
        self.player_id_entry.pack(pady=(0, 10))

    def add_player(self):
        name = self.name_entry.get()
        sport = self.sport_combobox.get()
        position = self.position_combobox.get()
        age = self.age_entry.get()

        if not name or not sport or not position or not age:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            age = int(age)
            if age <= 0:
                raise ValueError("Age must be a positive integer.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        query = "INSERT INTO players (name, sport, position, age) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (name, sport, position, age))
        self.connection.commit()
        messagebox.showinfo("Success", "Player added successfully!")

    def update_player(self):
        player_id = self.player_id_entry.get()
        name = self.name_entry.get()
        sport = self.sport_combobox.get()
        position = self.position_combobox.get()
        age = self.age_entry.get()

        if not player_id or not name or not sport or not position or not age:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            player_id = int(player_id)
            age = int(age)
            if age <= 0:
                raise ValueError("Age must be a positive integer.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        query = "UPDATE players SET name=%s, sport=%s, position=%s, age=%s WHERE id=%s"
        self.cursor.execute(query, (name, sport, position, age, player_id))
        self.connection.commit()
        messagebox.showinfo("Success", "Player updated successfully!")

    def delete_player(self):
        player_id = self.player_id_entry.get()

        if not player_id:
            messagebox.showerror("Error", "Player ID must be filled!")
            return

        try:
            player_id = int(player_id)
        except ValueError:
            messagebox.showerror("Error", "Invalid Player ID.")
            return

        query = "DELETE FROM players WHERE id=%s"
        self.cursor.execute(query, (player_id,))
        self.connection.commit()
        messagebox.showinfo("Success", "Player deleted successfully!")

    def update_position_options(self, sport):
        self.position_combobox.configure(values=self.positions_dict.get(sport, []))

    def create_statistics_widgets(self):
        # Statistics Widgets
        self.player_id_stat_entry = ctk.CTkEntry(self.statistics_tab, placeholder_text="Player ID")
        self.player_id_stat_entry.pack(pady=(10, 5))

        self.matches_played_entry = ctk.CTkEntry(self.statistics_tab, placeholder_text="Matches Played")
        self.matches_played_entry.pack(pady=(10, 5))

        self.goals_points_runs_entry = ctk.CTkEntry(self.statistics_tab, placeholder_text="Goals/Points/Runs")
        self.goals_points_runs_entry.pack(pady=(10, 5))

        self.assists_wickets_aces_entry = ctk.CTkEntry(self.statistics_tab, placeholder_text="Assists/Wickets/Aces")
        self.assists_wickets_aces_entry.pack(pady=(10, 5))

        self.add_stats_button = ctk.CTkButton(self.statistics_tab, text="Add Statistics", command=self.add_statistics)
        self.add_stats_button.pack(pady=(5, 5))

        # New fields for updating and deleting statistics
        self.stat_id_entry = ctk.CTkEntry(self.statistics_tab, placeholder_text="Statistic ID (for update/delete)")
        self.stat_id_entry.pack(pady=(10, 5))

        self.update_stats_button = ctk.CTkButton(self.statistics_tab, text="Update Statistics", command=self.update_statistics)
        self.update_stats_button.pack(pady=(5, 5))

        self.delete_stats_button = ctk.CTkButton(self.statistics_tab, text="Delete Statistics", command=self.delete_statistics)
        self.delete_stats_button.pack(pady=(5, 5))

    def add_statistics(self):
        player_id = self.player_id_stat_entry.get()
        matches_played = self.matches_played_entry.get()
        goals_points_runs = self.goals_points_runs_entry.get()
        assists_wickets_aces = self.assists_wickets_aces_entry.get()

        if not player_id or not matches_played or not goals_points_runs or not assists_wickets_aces:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            player_id = int(player_id)
            matches_played = int(matches_played)
            goals_points_runs = int(goals_points_runs)
            assists_wickets_aces = int(assists_wickets_aces)

            if matches_played < 0 or goals_points_runs < 0 or assists_wickets_aces < 0:
                raise ValueError("Statistics must be non-negative.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        query = "INSERT INTO statistics (player_id, sport, matches_played, goals_points_runs_scored, assists_wickets_aces_given) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(query, (player_id, self.sport_combobox.get(), matches_played, goals_points_runs, assists_wickets_aces))
        self.connection.commit()
        messagebox.showinfo("Success", "Statistics added successfully!")

    def update_statistics(self):
        stat_id = self.stat_id_entry.get()
        player_id = self.player_id_stat_entry.get()
        matches_played = self.matches_played_entry.get()
        goals_points_runs = self.goals_points_runs_entry.get()
        assists_wickets_aces = self.assists_wickets_aces_entry.get()

        if not stat_id or not player_id or not matches_played or not goals_points_runs or not assists_wickets_aces:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            stat_id = int(stat_id)
            player_id = int(player_id)
            matches_played = int(matches_played)
            goals_points_runs = int(goals_points_runs)
            assists_wickets_aces = int(assists_wickets_aces)

            if matches_played < 0 or goals_points_runs < 0 or assists_wickets_aces < 0:
                raise ValueError("Statistics must be non-negative.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        query = """
            UPDATE statistics 
            SET player_id=%s, matches_played=%s, goals_points_runs_scored=%s, assists_wickets_aces_given=%s 
            WHERE id=%s
        """
        self.cursor.execute(query, (player_id, matches_played, goals_points_runs, assists_wickets_aces, stat_id))
        self.connection.commit()
        messagebox.showinfo("Success", "Statistics updated successfully!")

    def delete_statistics(self):
        stat_id = self.stat_id_entry.get()

        if not stat_id:
            messagebox.showerror("Error", "Statistic ID must be filled!")
            return

        try:
            stat_id = int(stat_id)
        except ValueError:
            messagebox.showerror("Error", "Invalid Statistic ID.")
            return

        query = "DELETE FROM statistics WHERE id=%s"
        self.cursor.execute(query, (stat_id,))
        self.connection.commit()
        messagebox.showinfo("Success", "Statistics deleted successfully!")

    def create_view_players_widgets(self):
        self.view_players_listbox = Listbox(self.view_players_tab, height=15, font=("Arial", 14))
        self.view_players_listbox.pack(pady=(10, 5), fill='both', expand=True)

        self.refresh_button = ctk.CTkButton(self.view_players_tab, text="Refresh Player List", command=self.view_all_players)
        self.refresh_button.pack(pady=(5, 5))

        self.view_all_players()

    def view_all_players(self):
        self.view_players_listbox.delete(0, 'end')
        self.cursor.execute("SELECT * FROM players")
        for row in self.cursor.fetchall():
            self.view_players_listbox.insert('end', f"ID: {row[0]}, Name: {row[1]}, Sport: {row[2]}, Position: {row[3]}, Age: {row[4]}")

    def create_view_statistics_widgets(self):
        self.view_statistics_listbox = Listbox(self.view_statistics_tab, height=15, font=("Arial", 14))
        self.view_statistics_listbox.pack(pady=(10, 5), fill='both', expand=True)

        self.player_id_stat_view_entry = ctk.CTkEntry(self.view_statistics_tab, placeholder_text="Player ID")
        self.player_id_stat_view_entry.pack(pady=(10, 5))

        self.view_stats_button = ctk.CTkButton(self.view_statistics_tab, text="View Statistics", command=self.view_statistics)
        self.view_stats_button.pack(pady=(5, 5))

    def view_statistics(self):
        player_id = self.player_id_stat_view_entry.get()

        if not player_id:
            messagebox.showerror("Error", "Player ID must be filled!")
            return

        try:
            player_id = int(player_id)
        except ValueError:
            messagebox.showerror("Error", "Invalid Player ID.")
            return

        self.view_statistics_listbox.delete(0, 'end')
        query = "SELECT * FROM statistics WHERE player_id=%s"
        self.cursor.execute(query, (player_id,))
        for row in self.cursor.fetchall():
            self.view_statistics_listbox.insert('end', f"Stat ID: {row[0]}, Matches: {row[3]}, Goals/Points/Runs: {row[4]}, Assists/Wickets/Aces: {row[5]}")

    def create_reminders_widgets(self):
        self.reminder_text_entry = ctk.CTkEntry(self.reminders_tab, placeholder_text="Reminder Text")
        self.reminder_text_entry.pack(pady=(10, 5))

        self.reminder_date_entry = ctk.CTkEntry(self.reminders_tab, placeholder_text="YYYY-MM-DD")
        self.reminder_date_entry.pack(pady=(10, 5))

        self.add_reminder_button = ctk.CTkButton(self.reminders_tab, text="Add Reminder", command=self.add_reminder)
        self.add_reminder_button.pack(pady=(5, 5))

    def add_reminder(self):
        player_id = self.player_id_stat_entry.get()  # Assuming this ID is filled
        reminder_text = self.reminder_text_entry.get()
        reminder_date = self.reminder_date_entry.get()

        if not player_id or not reminder_text or not reminder_date:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        query = "INSERT INTO reminders (player_id, reminder_date, reminder_text) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (player_id, reminder_date, reminder_text))
        self.connection.commit()
        messagebox.showinfo("Success", "Reminder added successfully!")

    def create_view_reminders_widgets(self):
        self.view_reminders_listbox = Listbox(self.view_reminders_tab, height=15, font=("Arial", 14))
        self.view_reminders_listbox.pack(pady=(10, 5), fill='both', expand=True)

        self.refresh_reminders_button = ctk.CTkButton(self.view_reminders_tab, text="Refresh Reminders List", command=self.view_all_reminders)
        self.refresh_reminders_button.pack(pady=(5, 5))

        self.view_all_reminders()

    def view_all_reminders(self):
        player_id = self.player_id_stat_entry.get()  # Assuming this ID is filled

        if not player_id:
            messagebox.showerror("Error", "Player ID must be filled!")
            return

        self.view_reminders_listbox.delete(0, 'end')
        query = "SELECT * FROM reminders WHERE player_id=%s"
        self.cursor.execute(query, (player_id,))
        for row in self.cursor.fetchall():
            self.view_reminders_listbox.insert('end', f"Reminder ID: {row[0]}, Date: {row[2]}, Text: {row[3]}")

if __name__ == "__main__":
    app = SportsManagementApp()
    app.mainloop()
