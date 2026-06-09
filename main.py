import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import string
import os
from cryptography.fernet import Fernet

# ===============================
# Permanent Encryption Key
# ===============================
if not os.path.exists("secret.key"):
    with open("secret.key", "wb") as key_file:
        key_file.write(Fernet.generate_key())

with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

# ===============================
# Database Connection
# ===============================
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    password TEXT
)
""")
conn.commit()

# ===============================
# Save Password
# ===============================


def save_password():
    website = website_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if website == "" or username == "" or password == "":
        messagebox.showwarning("Warning", "Please fill all fields")
        return

    encrypted_password = cipher.encrypt(password.encode()).decode()

    cursor.execute(
        "INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
        (website, username, encrypted_password)
    )
    conn.commit()

    messagebox.showinfo("Success", "Password Saved Successfully")

    website_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

# ===============================
# Generate Strong Password
# ===============================


def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(12))

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

# ===============================
# View Passwords
# ===============================


def view_passwords():
    records = cursor.execute(
        "SELECT website, username, password FROM passwords"
    ).fetchall()

    data = ""

    for row in records:
        decrypted_password = cipher.decrypt(row[2].encode()).decode()

        data += f"Website: {row[0]}\n"
        data += f"Username: {row[1]}\n"
        data += f"Password: {decrypted_password}\n\n"

    if data == "":
        data = "No passwords saved."

    messagebox.showinfo("Saved Passwords", data)

# ===============================
# Search Password
# ===============================


def search_password():
    website = website_entry.get()

    if website == "":
        messagebox.showwarning("Warning", "Please enter website name")
        return

    result = cursor.execute(
        "SELECT username, password FROM passwords WHERE website=?",
        (website,)
    ).fetchone()

    if result:
        decrypted_password = cipher.decrypt(result[1].encode()).decode()

        messagebox.showinfo(
            "Found",
            f"Username: {result[0]}\nPassword: {decrypted_password}"
        )
    else:
        messagebox.showerror("Not Found", "No record found")

# ===============================
# Delete Password
# ===============================


def delete_password():
    website = website_entry.get()

    if website == "":
        messagebox.showwarning("Warning", "Please enter website name")
        return

    cursor.execute("DELETE FROM passwords WHERE website=?", (website,))
    conn.commit()

    if cursor.rowcount > 0:
        messagebox.showinfo("Deleted", "Password deleted successfully")
    else:
        messagebox.showerror("Not Found", "No record found")


# ===============================
# GUI Design
# ===============================
root = tk.Tk()
root.title("Password Manager")
root.geometry("450x550")
root.config(bg="#1e1e2f")
root.resizable(False, False)

title = tk.Label(
    root,
    text="🔐 Password Manager",
    font=("Arial", 18, "bold"),
    bg="#1e1e2f",
    fg="white"
)
title.pack(pady=15)

# Website
tk.Label(root, text="Website", bg="#1e1e2f", fg="white").pack()
website_entry = tk.Entry(root, width=35, font=("Arial", 11))
website_entry.pack(pady=5)

# Username
tk.Label(root, text="Username", bg="#1e1e2f", fg="white").pack()
username_entry = tk.Entry(root, width=35, font=("Arial", 11))
username_entry.pack(pady=5)

# Password
tk.Label(root, text="Password", bg="#1e1e2f", fg="white").pack()
password_entry = tk.Entry(root, width=35, font=("Arial", 11))
password_entry.pack(pady=5)

# Buttons
tk.Button(
    root,
    text="Generate Password",
    width=20,
    command=generate_password,
    bg="#3498db",
    fg="white"
).pack(pady=8)

tk.Button(
    root,
    text="Save Password",
    width=20,
    command=save_password,
    bg="#2ecc71",
    fg="white"
).pack(pady=8)

tk.Button(
    root,
    text="View Passwords",
    width=20,
    command=view_passwords,
    bg="#9b59b6",
    fg="white"
).pack(pady=8)

tk.Button(
    root,
    text="Search Password",
    width=20,
    command=search_password,
    bg="#f39c12"
).pack(pady=8)

tk.Button(
    root,
    text="Delete Password",
    width=20,
    command=delete_password,
    bg="#e74c3c",
    fg="white"
).pack(pady=8)

root.mainloop()
