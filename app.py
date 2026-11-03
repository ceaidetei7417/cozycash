# AI Assistance:
# I used ChatGPT during yhe development of this project to explore ideas,
# find relevant documentation and implementation approaches more efficiently
# and to better understand concepts related to Python, Flask, HTML, CSS and JavaScript.
# I also used it to help clarify errors and review parts of my code.
# The project design, implementation, and final code were completed and reviews by me.

import datetime
import calendar

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Import the decorator used to restrict access to logged-in users
from helpers import login_required

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect the application to the SQLite database
db = SQL("sqlite:///cozycash.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def landing():
    """Show landing page, redirect to dashboard if logged in"""
    if not session.get("id_account"):
        return render_template("landing.html")
    return redirect("/dashboard")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        # Clear any session data
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("login.html", message="Provide username!")
        elif not password:
            return render_template("login.html", message="Provide password!")

        rows = db.execute("SELECT * FROM accounts WHERE username = ?", request.form.get("username"))

        # Verify the submitted password
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], password):
            return render_template("login.html", message="Invalid username or password")

        # Store the account ID in the session
        session["id_account"] = rows[0]["id"]
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username:
            return render_template("register.html", message="Provide username!")
        elif not password:
            return render_template("register.html", message="Provide password!")
        elif not confirm_password:
            return render_template("register.html", message="Confirm password!")
        elif password != confirm_password:
            return render_template("register.html", message="Passwords do not match!")

        # Check whether the username is already registered
        rows = db.execute("SELECT * FROM accounts WHERE username = ?", username)
        if len(rows) > 0:
            return render_template("register.html", message="Username already taken!")

        # Create the new account, store a hashed version of the password
        db.execute("INSERT INTO accounts (username, password_hash) VALUES (?, ?)",
                   username, generate_password_hash(password))

        rows = db.execute("SELECT * FROM accounts WHERE username = ?", request.form.get("username"))
        session["id_account"] = rows[0]["id"]
        return redirect("/dashboard")
    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Show user's homepage"""
    id_account = session["id_account"]

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    username = db.execute("SELECT username FROM accounts WHERE id = ?", id_account)

    # https://www.geeksforgeeks.org/python/python-datetime-module/
    month = datetime.datetime.now().strftime("%m")
    month_name = calendar.month_name[int(month)]
    year = datetime.datetime.now().strftime("%Y")

    # Calculate the user's total income
    income_query = db.execute("SELECT SUM(transactions.amount) AS total FROM transactions " \
                              "JOIN categories ON categories.id = transactions.id_category " \
                              "WHERE id_account = ? AND categories.type = 'income'", id_account)
    if income_query[0]["total"] is None:
        income = 0
    else:
        income = income_query[0]["total"]

    # Calculate the user's total expenses
    expense_query = db.execute("SELECT SUM(transactions.amount) AS total FROM transactions " \
                               "JOIN categories ON categories.id = transactions.id_category " \
                               "WHERE id_account = ? AND categories.type = 'expense'", id_account)
    if expense_query[0]["total"] is None:
        expense = 0
    else:
        expense = expense_query[0]["total"]

    # Calculate the current balance
    balance = income - expense

    # Calculate income recorded during the current month
    month_income_query = db.execute("SELECT SUM(transactions.amount) AS total FROM transactions " \
                                    "JOIN categories ON categories.id = transactions.id_category " \
                                    "WHERE id_account = ? AND categories.type = 'income' " \
                                    "AND month = ? AND year = ?", id_account, month, year)

    if month_income_query[0]["total"] is None:
        month_income = 0
    else:
        month_income = month_income_query[0]["total"]

    # Calculate expenses recorded during the current month
    month_expense_query = db.execute("SELECT SUM(transactions.amount) AS total FROM transactions " \
                                     "JOIN categories ON categories.id = transactions.id_category " \
                                     "WHERE id_account = ? AND categories.type = 'expense' " \
                                     "AND month = ? AND year = ?", id_account, month, year)

    if month_expense_query[0]["total"] is None:
        month_expense = 0
    else:
        month_expense = month_expense_query[0]["total"]

    # Calculate the total budget during to the current month
    month_budget_query = db.execute("SELECT SUM(budgets.amount) AS total FROM budgets " \
                                    "WHERE id_account = ? AND month = ? AND year = ?", id_account, month, year)

    if month_budget_query[0]["total"] is None:
        month_budget = 0
    else:
        month_budget = month_budget_query[0]["total"]

    # Get the three most recent transactions, ordered
    recent_transactions = db.execute("SELECT amount, day, month, year, categories.name, categories.type FROM transactions " \
                                     "JOIN categories ON categories.id = transactions.id_category " \
                                     "WHERE id_account = ? ORDER BY year DESC, month DESC, day DESC, transactions.id DESC " \
                                     "LIMIT 3", id_account)

    return render_template("dashboard.html", username=username[0]["username"],
                           balance=balance,
                           month_income=month_income, month_expense=month_expense,
                           month_budget=month_budget,
                           recent_transactions=recent_transactions, month_name=month_name, currency=currency)


@app.route("/transactions")
@login_required
def transactions():
    """Show transactions"""
    id_account = session["id_account"]

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    # Get all transactions
    transactions = db.execute("SELECT transactions.id, description, amount, day, month, year, categories.name, categories.type FROM transactions " \
                              "JOIN categories ON categories.id = transactions.id_category " \
                              "WHERE id_account = ? ORDER BY year DESC, month DESC, day DESC, transactions.id DESC ", id_account)

    # Count the total number of transactions
    number_query = db.execute("SELECT COUNT(id) FROM transactions WHERE id_account = ?", id_account)
    number = number_query[0]["COUNT(id)"]

    # Calculate total income
    total_income = 0
    for transaction in transactions:
        if transaction["type"] == "income":
            total_income += transaction["amount"]

    # Calculate total expenses
    total_expense = 0
    for transaction in transactions:
        if transaction["type"] == "expense":
            total_expense += transaction["amount"]

    return render_template("transactions.html", transactions=transactions, total_income=total_income,
                           total_expense=total_expense, currency=currency, number=number)


@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    """Add a new transaction"""
    id_account = session["id_account"]

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    if request.method == "POST":
        # Get the values submitted
        amount = request.form.get("amount")
        id_category = request.form.get("id_category")
        date_str = request.form.get("date")
        description = request.form.get("description")
        type = request.form.get("type")

        # Get all available categories
        categories = db.execute("SELECT * FROM categories ORDER BY type, name")

        if not amount or not date_str or not id_category or not type:
            return render_template("add_transaction.html", message="Please complete all required fields!", categories=categories, currency=currency)

        # Convert the amount to a float number and ensure that it's positive
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return render_template("add_transaction.html", message="Please enter a valid positive amount!", categories=categories, currency=currency)

        # Convert the submitted date into a python datetime object
        try:
            # https://stackoverflow.com/questions/55971122/how-to-fetch-date-from-html-form-into-flask
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return render_template("add_transaction.html", message="Invalid date format!", categories=categories, currency=currency)

        # Extract the year, month and day separately
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")

        category = db.execute("SELECT type FROM categories WHERE id = ?", id_category)
        if len(category) != 1 or category[0]["type"] != type:
            return render_template("add_transaction.html", message="Invalid category for the selected transaction type!",
                                   categories=categories, currency=currency)

        # Insert the new transaction into the database
        db.execute("INSERT INTO transactions (id_account, id_category, amount, description, day, month, year) " \
                   "VALUES (?, ?, ?, ?, ?, ?, ?)", id_account, id_category, amount, description, day, month, year)

        return redirect("/transactions")

    categories = db.execute("SELECT * FROM categories ORDER BY type, name")

    return render_template("add_transaction.html", categories=categories, currency=currency)


@app.route("/edit_transaction", methods=["GET", "POST"])
@login_required
def edit_transaction():
    """Edit a transaction"""
    id_account = session["id_account"]

    id_transaction = request.args.get("id")

    if not id_transaction:
        return redirect("/transactions")

    # Get the requested transaction
    rows = db.execute("SELECT transactions.*, categories.type FROM transactions " \
                      "JOIN categories ON categories.id = transactions.id_category " \
                      "WHERE transactions.id = ? AND " \
                      "id_account = ?", id_transaction, id_account)

    if len(rows) != 1:
        return redirect("/transactions")

    transaction = rows[0]

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    if request.method == "POST":
        if request.form.get("action") == "delete":
            # Delete the transaction when the button was submitted
            db.execute("DELETE FROM transactions WHERE id = ? AND id_account = ?",
                       id_transaction, id_account)
            return redirect("/transactions")

        # Get the transaction's details
        amount = request.form.get("amount")
        id_category = request.form.get("id_category")
        date_str = request.form.get("date")
        description = request.form.get("description")
        type = request.form.get("type")

        categories = db.execute("SELECT * FROM categories ORDER BY type, name")

        if not amount or not date_str or not id_category or not type:
            return render_template("edit_transaction.html", message="Please complete all required fields!", categories=categories,
                                   transaction=transaction, currency=currency)

        # Convert the amount to a float number and ensure that it's positive
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return render_template("edit_transaction.html", message="Please enter a valid positive amount!", categories=categories,
                                   transaction=transaction, currency=currency)

        # Validate the submitted date
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return render_template("edit_transaction.html", message="Invalid date format!", transaction=transaction,
                                   categories=categories, currency=currency)

        # Extract the year, month and day separately
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")

        # Ensure that the selected category exists and matches the transaction type
        category = db.execute("SELECT type FROM categories WHERE id = ?", id_category)
        if len(category) != 1 or category[0]["type"] != type:
            return render_template("edit_transaction.html", message="Invalid category for the selected transaction type!",
                                   transaction=transaction, categories=categories, currency=currency)

        # Update the transaction
        db.execute("UPDATE transactions SET id_category = ?, amount = ?, description = ?, " \
                   "day = ?, month = ?, year = ? WHERE id = ? AND id_account = ?", id_category, amount,
                   description, day, month, year, id_transaction, id_account)

        return redirect("/transactions")

    categories = db.execute("SELECT * FROM categories ORDER BY type, name")

    return render_template("edit_transaction.html", transaction=transaction, categories=categories, currency=currency)


@app.route("/budget")
@login_required
def budget():
    """Show budgets and their progress"""
    id_account = session["id_account"]

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    month = datetime.datetime.now().strftime("%m")
    year = datetime.datetime.now().strftime("%Y")

    # Get the user's budgets for the current month and calculate the spending for each category
    budgets = db.execute("SELECT budgets.id, budgets.amount, categories.name, categories.type, " \
                         "(SELECT SUM(transactions.amount) FROM transactions " \
                         "WHERE transactions.id_category = budgets.id_category AND transactions.id_account = budgets.id_account AND " \
                         "transactions.month = budgets.month AND transactions.year = budgets.year) AS total_spent FROM budgets " \
                         "JOIN categories ON categories.id = budgets.id_category WHERE budgets.id_account = ? " \
                         "AND budgets.month = ? AND budgets.year = ?", id_account, month, year)

    # Calculate the total budget and total spending
    total_budget = 0
    total_spent = 0

    for budget in budgets:
        total_budget += budget["amount"]
        if budget["total_spent"] is not None:
            total_spent += budget["total_spent"]

    # Calculate the remaining amount
    total = total_budget - total_spent

    return render_template("budget.html", budgets=budgets, total_budget=total_budget, total_spent=total_spent,
                           total=total, month=month, currency=currency)


@app.route("/add_budget", methods=["GET", "POST"])
@login_required
def add_budget():
    """Add a new budget"""

    id_account = session["id_account"]
    month = datetime.datetime.now().strftime("%m")
    year = datetime.datetime.now().strftime("%Y")

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    if request.method == "POST":
        id_category = request.form.get("id_category")
        amount = request.form.get("amount")

        # Get only expense categories
        categories = db.execute("SELECT * FROM categories WHERE type = 'expense'")

        if not id_category or not amount:
            return render_template("add_budget.html", message="Please fill all fields!", categories=categories, currency=currency)

        # Convert the amount to a float number and ensure that it's positive
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return render_template("add_budget.html", message="Please enter a valid positive amount!", categories=categories, currency=currency)

        category = db.execute("SELECT type FROM categories WHERE id = ?", id_category)

        # Verify that the selected category exists and is an expense category
        if len(category) != 1 or category[0]["type"] != "expense":
            return render_template("add_budget.html", message="Please select a valid category!", categories=categories, currency=currency)

        # Check whether a budget already exists
        exist = db.execute("SELECT * FROM budgets WHERE id_account = ? AND id_category = ? " \
                           "AND month = ? AND year = ?", id_account, id_category, month, year)

        if len(exist) > 0:
            return render_template("add_budget.html",
                                   message="You already have a budget for this category!", categories=categories, currency=currency)

        # Create the budget
        db.execute("INSERT INTO budgets (id_account, id_category, amount, month, year) VALUES " \
                   "(?, ?, ?, ?, ?)", id_account, id_category, amount, month, year)

        return redirect("/budget")

    categories = db.execute("SELECT * FROM categories WHERE type = 'expense'")

    return render_template("add_budget.html", categories=categories, currency=currency)


@app.route("/edit_budget", methods=["GET", "POST"])
@login_required
def edit_budget():
    """Edit a budget"""
    id_account = session["id_account"]
    id_budget = request.args.get("id")

    if not id_budget:
        return redirect("/budget")

    # Get the requested budget
    rows = db.execute("SELECT budgets.*, categories.name FROM budgets " \
                      "JOIN categories ON categories.id = budgets.id_category WHERE " \
                      "budgets.id = ? AND budgets.id_account = ?", id_budget, id_account)

    if len(rows) != 1:
        return redirect("/budget")

    budget = rows[0]

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    if request.method == "POST":
        # Delete the budget when the button was submitted
        if request.form.get("action") == "delete":
            db.execute("DELETE FROM budgets WHERE id = ? AND id_account = ?",
                       id_budget, id_account)
            return redirect("/budget")

        amount = request.form.get("amount")

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return render_template("edit_budget.html", message="Please enter a valid positive amount!", budget=budget, currency=currency)

        # Update the budget amount
        db.execute("UPDATE budgets SET amount = ? WHERE id = ? AND id_account = ?",
                   amount, id_budget, id_account)

        return redirect("/budget")

    return render_template("edit_budget.html", budget=budget, currency=currency)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Show settings"""
    id_account = session["id_account"]

    if request.method == "POST":
        new_currency = request.form.get("currency")

        # Save the new currency preference
        if new_currency:
            db.execute("UPDATE accounts SET currency = ? WHERE id = ?", new_currency, id_account)

        return redirect("/settings")

    currency_query = db.execute("SELECT currency FROM accounts WHERE id = ?", id_account)
    currency = currency_query[0]["currency"]

    return render_template("settings.html", currency=currency)
