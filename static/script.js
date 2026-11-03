document.addEventListener("DOMContentLoaded", function() {
    let login = document.getElementById("btn-login");
    if (login) {
        login.addEventListener("click", function() {
            window.location.href =
            "/login"; // https://www.geeksforgeeks.org/html/how-to-get-browser-to-navigate-url-in-javascript/
        });
    }

    let register = document.getElementById("btn-register")
    if (register) {
        register.addEventListener("click", function() {
            window.location.href = "/register";
        });
    }

    let logout = document.getElementById("btn-logout");
    if (logout) {
        logout.addEventListener("click", function() {
            window.location.href = "/logout";
        });
    }
});

// https://stackoverflow.com/questions/4423132/how-to-hide-a-select-tag
function showIncome() {
    let income = document.getElementById("select-income");
    let expense = document.getElementById("select-expense");

    income.style.display = "block";
    expense.style.display = "none";

    income.disabled = false;
    expense.disabled = true;
}

function showExpense() {
    let income = document.getElementById("select-income");
    let expense = document.getElementById("select-expense");

    income.style.display = "none";
    expense.style.display = "block";

    income.disabled = true;
    expense.disabled = false;
}

function changeCategory(select) {
    if (select.value == "income")
        showIncome();
    else if (select.value == "expense")
        showExpense();
}
