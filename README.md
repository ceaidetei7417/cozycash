# COZYCASH
#### Video Demo: https://youtu.be/q8bxp_aEKU8
#### Description:

Cozycash is a personal finance tracking web application developed as my final project for CS50x. Its purpose is to help users organize their finances by recording income and expenses, managing transactions, and setting monthly budgets for different expense categories. Cozycash provides a single place where users can record their financial activity and get a clearer overview of their spending habits.

The application was built using Python and Flask for the back end, SQLite for data storage, and HTML, CSS, and JavaScript for the front end. This project allowed me to combine concepts learned throughout CS50x, including database management, user authentication, backend validation, and interaction between the front end and back end.

Cozycash supports multiple user accounts. Each user can register, log in, and manage their own financial information. Transactions and budgets are associated with the account that created them, keeping each user's records separate.

## Features

- ### User Accounts:

Users can create an account with a username and password. Passwords are stored as hashes rather than plain text. The application uses sessions to keep track of authenticated users and restrict access to pages that require login. Users can also log out of their accounts.

- ### Dashboard:

The dashboard provides an overview of the user's financial activity, including income, expenses, and budget information. It allows users to understand their financial situation without having to inspect every transaction individually.

- ### Transaction Management

Users can add income and expense transactions. Each transaction includes an amount, category, description, and date. Existing transactions can also be viewed, edited, or deleted.
The application distinguishes between income and expenses, ensuring that users select an appropriate category for each transaction.

- ### Categories

Transactions are organized into predefined categories. Income and expenses have separate category types, making financial records easier to organize and understand.

- ### Monthly Budgets

Users can create monthly budgets for individual expense categories. Each budget represents the amount they plan to spend in a particular category during a specific month. Users can view, edit, and delete their budgets and compare planned amounts with recorded expenses.

- ### Settings

The settings page allows users to select their preferred currency symbol. Changing this preference affects how amounts are displayed, but does not automatically convert values between currencies.

## Technologies Used

- ### Python:

Handles application logic, validation, and database operations.

- ### Flask:

Provides the web framework, routes, and template rendering.

- ### Jinja:

Used to render dynamic HTML pages and display data passed from Python.

- ### SQLite:

Stores accounts, categories, transactions, and budgets.

- ### CS50 SQL Library:

Allows Python to interact with the database.

- ### Flask-Session:

Manages user sessions.

- ### Werkzeug:

Provides password hashing and verification.

- ### HTML:

Defines the structure of the pages.

- ### CSS:

Handles the application's styling and layout.

- ### JavaScript:

Adds client-side interactions.

- ### Bootstrap:

Provides interface components and icons.

## Database Structure

The application uses an SQLite database named cozycash.db, containing four main tables. The accounts table stores usernames, password hashes, and currency preferences. The categories table stores predefined categories and identifies them as either income or expense categories. The transactions table stores each user's financial records, including the amount, description, date, account, and category. The budgets table stores monthly budgets associated with a user and an expense category.

Foreign keys connect related records, while a uniqueness constraint prevents a user from creating multiple budgets for the same category, month and year. The separation of the information into different tables makes the database more organized.

## Files and Project Structure

### Python Files:

 - #### app.py:
The main application file. It initializes Flask and the database connection and defines the routes for registration, login, the dashboard, transaction management, budgets, and settings.

 - #### helpers.py:

Contains the login_required decorator, which restricts access to pages requiring authentication.

- ### HTML Templates:
The templates directory contains the pages rendered by Flask

 - #### layout.html:
The base template shared by the other pages, containing the common page structure and links to static resources.

 - #### landing.html:
The landing page displayed to visitors.

 - #### login.html:
Contains the login form.

 - #### register.html:
Contains the registration form.

 - #### dashboard.html:
Displays the user's financial overview.

 - #### transactions.html:
Displays the user's recorded transactions.

 - #### add_transaction.html:
Contains the form for adding a new transaction.

 - #### edit_transaction.html:
Contains the form for editing an existing transaction.

 - #### budget.html:
Displays the user's budgets and budget management options.

 - #### add_budget.html:
Contains the form for creating a new budget.

 - #### edit_budget.html:
Contains the form for editing an existing budget.

 - #### settings.html:
Allows users to change their currency preference.

### Static Files

 - #### style.css:
Custom styling for the application's pages and interface elements.

 - #### script.js:
JavaScript functionality for client-side interactions, including form and category selection behavior.

## Design Choices

Since the application focuses on financial information, I chose a minimalist design with consistent styling across its pages. I decided to separate income and expense categories to make transaction creation more intuitive and reduce the possibility of selecting an inappropriate category.

By storing accounts, categories, transactions and budgets into separet databes tables allowed me to establish relationships between different types of information and associate financial records with individual users.

I also included monthly budgets because I wanted the application to do more than simply store transactions. Comparing planned budgets with actual expenses gives users a better understanding of their spending.

## Running the Application

To run cozycash locally, Python and the required libraries must be installed.

1. Open a terminal in the project directory.
2. Run the following command:

```
flask run
```

3. Open the local address displayed in the terminal in a web browser.
