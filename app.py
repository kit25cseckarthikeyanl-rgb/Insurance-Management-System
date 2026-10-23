from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "insurance.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            address TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            policy_name TEXT NOT NULL,
            policy_type TEXT NOT NULL,
            premium REAL NOT NULL CHECK(premium >= 0),
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER NOT NULL,
            claim_date TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount >= 0),
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY(policy_id) REFERENCES policies(id) ON DELETE CASCADE
        );
        """)
        count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO customers (full_name,email,phone,address) VALUES (?,?,?,?)",
                [
                    ("Sample Customer One", "customer1@example.invalid", "0000000001", "Sample Address 1"),
                    ("Sample Customer Two", "customer2@example.invalid", "0000000002", "Sample Address 2"),
                    ("Sample Customer Three", "customer3@example.invalid", "0000000003", "Sample Address 3"),
                ],
            )
            conn.executemany(
                """INSERT INTO policies
                (customer_id,policy_name,policy_type,premium,start_date,end_date,status)
                VALUES (?,?,?,?,?,?,?)""",
                [
                    (1, "Family Health Secure", "Health", 12500, "2026-01-01", "2026-12-31", "Active"),
                    (2, "Smart Life Cover", "Life", 18000, "2026-02-01", "2027-01-31", "Active"),
                    (3, "Vehicle Protect Plus", "Vehicle", 7600, "2025-07-01", "2026-06-30", "Expired"),
                ],
            )
            conn.executemany(
                "INSERT INTO claims (policy_id,claim_date,amount,reason,status) VALUES (?,?,?,?,?)",
                [
                    (1, "2026-04-10", 8500, "Hospital treatment", "Approved"),
                    (2, "2026-06-18", 25000, "Accidental damage", "Pending"),
                ],
            )

@app.route("/")
def dashboard():
    with get_db() as conn:
        stats = {
            "customers": conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
            "policies": conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0],
            "active": conn.execute("SELECT COUNT(*) FROM policies WHERE status='Active'").fetchone()[0],
            "claims": conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0],
        }
        recent = conn.execute("""
            SELECT cl.id, c.full_name, p.policy_name, cl.claim_date, cl.amount, cl.status
            FROM claims cl JOIN policies p ON cl.policy_id=p.id
            JOIN customers c ON p.customer_id=c.id
            ORDER BY cl.id DESC LIMIT 5
        """).fetchall()
    return render_template("dashboard.html", stats=stats, recent=recent)

@app.route("/customers", methods=["GET", "POST"])
def customers():
    with get_db() as conn:
        if request.method == "POST":
            name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            if not all([name, email, phone, address]):
                flash("Please fill in every customer field.", "error")
            else:
                try:
                    conn.execute("INSERT INTO customers(full_name,email,phone,address) VALUES(?,?,?,?)",
                                 (name, email, phone, address))
                    flash("Customer added successfully.", "success")
                    return redirect(url_for("customers"))
                except sqlite3.IntegrityError:
                    flash("That email address already exists.", "error")
        rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    return render_template("customers.html", customers=rows)

@app.route("/customers/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    with get_db() as conn:
        conn.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    flash("Customer and associated records deleted.", "success")
    return redirect(url_for("customers"))

@app.route("/policies", methods=["GET", "POST"])
def policies():
    with get_db() as conn:
        if request.method == "POST":
            values = (
                request.form.get("customer_id"),
                request.form.get("policy_name", "").strip(),
                request.form.get("policy_type"),
                request.form.get("premium"),
                request.form.get("start_date"),
                request.form.get("end_date"),
                request.form.get("status"),
            )
            try:
                if not all(values):
                    raise ValueError()
                if float(values[3]) < 0:
                    raise ValueError()
                conn.execute("""INSERT INTO policies
                    (customer_id,policy_name,policy_type,premium,start_date,end_date,status)
                    VALUES(?,?,?,?,?,?,?)""", values)
                flash("Policy created successfully.", "success")
                return redirect(url_for("policies"))
            except (ValueError, sqlite3.IntegrityError):
                flash("Check the policy details and try again.", "error")
        rows = conn.execute("""
            SELECT p.*, c.full_name FROM policies p
            JOIN customers c ON p.customer_id=c.id ORDER BY p.id DESC
        """).fetchall()
        customer_rows = conn.execute("SELECT id,full_name FROM customers ORDER BY full_name").fetchall()
    return render_template("policies.html", policies=rows, customers=customer_rows)

@app.route("/policies/delete/<int:policy_id>", methods=["POST"])
def delete_policy(policy_id):
    with get_db() as conn:
        conn.execute("DELETE FROM policies WHERE id=?", (policy_id,))
    flash("Policy and associated claims deleted.", "success")
    return redirect(url_for("policies"))

@app.route("/claims", methods=["GET", "POST"])
def claims():
    with get_db() as conn:
        if request.method == "POST":
            values = (
                request.form.get("policy_id"),
                request.form.get("claim_date"),
                request.form.get("amount"),
                request.form.get("reason", "").strip(),
                request.form.get("status"),
            )
            try:
                if not all(values) or float(values[2]) < 0:
                    raise ValueError()
                conn.execute("""INSERT INTO claims(policy_id,claim_date,amount,reason,status)
                    VALUES(?,?,?,?,?)""", values)
                flash("Claim submitted successfully.", "success")
                return redirect(url_for("claims"))
            except (ValueError, sqlite3.IntegrityError):
                flash("Check the claim details and try again.", "error")
        rows = conn.execute("""
            SELECT cl.*, p.policy_name, c.full_name FROM claims cl
            JOIN policies p ON cl.policy_id=p.id
            JOIN customers c ON p.customer_id=c.id ORDER BY cl.id DESC
        """).fetchall()
        policy_rows = conn.execute("""
            SELECT p.id, p.policy_name, c.full_name FROM policies p
            JOIN customers c ON p.customer_id=c.id ORDER BY p.id DESC
        """).fetchall()
    return render_template("claims.html", claims=rows, policies=policy_rows)

@app.route("/claims/status/<int:claim_id>", methods=["POST"])
def update_claim_status(claim_id):
    status = request.form.get("status")
    if status not in ("Pending", "Approved", "Rejected"):
        flash("Invalid claim status.", "error")
    else:
        with get_db() as conn:
            conn.execute("UPDATE claims SET status=? WHERE id=?", (status, claim_id))
        flash("Claim status updated.", "success")
    return redirect(url_for("claims"))

@app.route("/claims/delete/<int:claim_id>", methods=["POST"])
def delete_claim(claim_id):
    with get_db() as conn:
        conn.execute("DELETE FROM claims WHERE id=?", (claim_id,))
    flash("Claim deleted.", "success")
    return redirect(url_for("claims"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
