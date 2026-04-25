from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS sales(name TEXT, total REAL, received REAL, balance REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS stock(qty INTEGER)")
    conn.commit()
    conn.close()

def get_stock():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT SUM(qty) FROM stock")
    r = c.fetchone()[0]
    conn.close()
    return r if r else 0

@app.route("/")
def index():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT name, total, received, balance FROM sales")
    data = c.fetchall()
    conn.close()
    return render_template("index.html", data=data, stock=get_stock())

@app.route("/add_stock", methods=["POST"])
def add_stock():
    qty = int(request.form["qty"])
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO stock(qty) VALUES(?)", (qty,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/add_sale", methods=["POST"])
def add_sale():
    name = request.form["name"]
    qty = int(request.form["qty"])
    price = float(request.form["price"])
    received = float(request.form["received"])

    stock = get_stock()
    if qty > stock:
        return "Not enough stock"

    total = qty * price
    balance = total - received

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO sales VALUES(?,?,?,?)", (name, total, received, balance))
    c.execute("INSERT INTO stock(qty) VALUES(?)", (-qty,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/pay", methods=["POST"])
def pay():
    name = request.form["name"]
    amount = float(request.form["amount"])

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT rowid, balance FROM sales WHERE name=? AND balance>0", (name,))
    rows = c.fetchall()

    for r in rows:
        id, bal = r
        if amount <= 0:
            break
        if amount >= bal:
            c.execute("UPDATE sales SET balance=0, received=received+? WHERE rowid=?", (bal, id))
            amount -= bal
        else:
            c.execute("UPDATE sales SET balance=balance-?, received=received+? WHERE rowid=?", (amount, amount, id))
            amount = 0

    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run()
    import os

import os

init_db()

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
