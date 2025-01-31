// static/js/app.js
function showDetails(element) {
    const details = document.getElementById(`${element}`);
    if (details.style.display === "none") {
        details.style.display = "block";
    } else {
        details.style.display = "none";
    }
}

// Send JSON data to the FastAPI endpoint
const response =  fetch('/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(jsonData),
});

const result =  response.json();
window.location.replace('/');
console.log(result);


