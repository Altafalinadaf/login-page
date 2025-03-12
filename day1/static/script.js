document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("expense-form").addEventListener("submit", async function (event) {
        event.preventDefault();
        const amount = document.getElementById("amount").value;
        const category = document.getElementById("category").value;
        const description = document.getElementById("description").value;
        const response = await fetch("/add_expense", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount, category, description })
        });
        if (response.ok) location.reload();
    });

    document.querySelectorAll(".delete").forEach(button => {
        button.addEventListener("click", async function () {
            const expenseId = this.getAttribute("data-id");
            await fetch(`/delete_expense/${expenseId}`, { method: "POST" });
            location.reload();
        });
    });
});
