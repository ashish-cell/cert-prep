document.addEventListener('DOMContentLoaded', function() {
    // Get the signup form if it exists
    const signupForm = document.querySelector('form[action*="signup"]');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long!');
                return false;
            }
        });
    }

    // Add password visibility toggle
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle';
        toggleBtn.textContent = 'Show';
        
        toggleBtn.addEventListener('click', function() {
            const type = input.getAttribute('type');
            input.setAttribute('type', type === 'password' ? 'text' : 'password');
            toggleBtn.textContent = type === 'password' ? 'Hide' : 'Show';
        });
        
        input.parentNode.appendChild(toggleBtn);
    });
}); 