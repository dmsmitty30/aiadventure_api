document.addEventListener('DOMContentLoaded', function() {
    let isLoggedIn = false; // Simulate user state

    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const loginLink = document.querySelector('#login-link');
    const registerLink = document.querySelector('#register-link');
    const logoutLink = document.querySelector('#logout-link');
    const formContainer = document.querySelector('#form-container');
    const formTitle = document.querySelector('#form-title');
    const authForm = document.querySelector('#auth-form');

    // Toggle the menu visibility
    hamburger.addEventListener('click', () => {
        navMenu.style.display = navMenu.style.display === 'block' ? 'none' : 'block';
    });

    // Update menu based on user state
    function updateMenu() {
        if (isLoggedIn) {
            loginLink.style.display = 'none';
            registerLink.style.display = 'none';
            logoutLink.style.display = 'block';
        } else {
            loginLink.style.display = 'block';
            registerLink.style.display = 'block';
            //logoutLink.style.display = 'none';
        }
    }

    updateMenu();

    // Open form for Log In or Register
    loginLink.addEventListener('click', () => openForm('Log In'));
    registerLink.addEventListener('click', () => openForm('Register'));


    // Handle Log Out
    logoutLink.addEventListener('click', () => {
        fetch('/user/logout', { method: 'POST' })
            .then(response => {
                if (response.ok) {
                    isLoggedIn = false;
                    updateMenu();
                    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                    alert('Logged out successfully');
                } else {
                    alert('Failed to log out');
                }
            });
    });

    const parentElement = document.body; // or a more specific parent container

    // Add an event listener to the parent
    parentElement.addEventListener('click', function(event) {
      // Check if the clicked element matches the selector
      if (event.target && event.target.matches('a.dynamic-link')) {
        event.preventDefault(); // Prevent the default action if needed
        console.log('Dynamic link clicked!', event.target.href);
      }
    });


    // Open the form
    function openForm(type) {
        formTitle.textContent = type;
        formContainer.style.display = 'block';
    }

    // Close the form on submit
    authForm.addEventListener('submit', event => {
        event.preventDefault();
        const email = document.querySelector('#email').value;
        const password = document.querySelector('#password').value;

        if (!validateEmail(email)) {
            alert('Please enter a valid email address');
            return;
        }

        const endpoint = formTitle.textContent === 'Log In' ? '/user/login' : '/user/register';
        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.access_token) {
                document.cookie = `access_token=${data.access_token}; path=/;`;
                if (formTitle.textContent === 'Log In') {
                    isLoggedIn = true;
                }
                updateMenu();
                alert(`${formTitle.textContent} successful`);
                formContainer.style.display = 'none';
                authForm.reset();
            } else {
                alert(`${formTitle.textContent} failed`);
            }
        });
    });

    // Validate email format
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});