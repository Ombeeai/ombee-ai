// Ombee AI Authentication

// Check if user is already logged in
async function checkAuth() {
    const { data: { session } } = await window.OmbeeConfig.supabase.auth.getSession();
    
    if (session) {
        // User is logged in, redirect to main app
        window.location.href = 'index.html';
    }
}

// Show/hide forms
function showLogin() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    clearMessage();
}

function showSignup() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.remove('hidden');
    clearMessage();
}

// Message helpers
function showMessage(message, type = 'error') {
    const messageEl = document.getElementById('authMessage');
    messageEl.textContent = message;
    messageEl.className = `alert alert-${type}`;
    messageEl.classList.remove('hidden');
    
    if (type === 'success') {
        setTimeout(() => clearMessage(), 3000);
    }
}

function clearMessage() {
    const messageEl = document.getElementById('authMessage');
    messageEl.classList.add('hidden');
}

// Backend user creation/sync
async function ensureBackendUser(supabaseUser) {
    try {
        // First, check if user exists in backend
        const checkResponse = await fetch(`${window.OmbeeConfig.API_URL}/api/users/${supabaseUser.id}`);
        
        if (checkResponse.ok) {
            // User exists, we're good
            console.log('Backend user exists');
            return true;
        }
        
        // User doesn't exist, create them
        console.log('Creating backend user...');
        const createResponse = await fetch(`${window.OmbeeConfig.API_URL}/api/users/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: supabaseUser.id,
                email: supabaseUser.email,
                name: supabaseUser.user_metadata?.name || supabaseUser.email.split('@')[0],
                preferences: {}
            })
        });
        
        if (!createResponse.ok) {
            const errorData = await createResponse.text();
            console.error('Failed to create backend user:', errorData);
            return false;
        }
        
        console.log('Backend user created');
        return true;
        
    } catch (error) {
        console.error('Backend user sync error:', error);
        // Don't block login for backend sync issues
        return true;
    }
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Basic validation
    if (!email || !password) {
        showMessage('Please fill in all fields');
        return;
    }
    
    try {
        const { data, error } = await window.OmbeeConfig.supabase.auth.signInWithPassword({
            email: email,
            password: password
        });
        
        if (error) {
            // Better error messages
            if (error.message.includes('Invalid login credentials')) {
                showMessage('Invalid email or password');
            } else if (error.message.includes('Email not confirmed')) {
                showMessage('Please verify your email before logging in');
            } else {
                showMessage(error.message);
            }
            return;
        }
        
        // Ensure backend user exists
        showMessage('Login successful! Setting up your account...', 'success');
        await ensureBackendUser(data.user);
        
        // Small delay to show success message
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
        
    } catch (error) {
        showMessage('An unexpected error occurred. Please try again.');
        console.error('Login error:', error);
    }
}


// Handle signup
async function handleSignup(event) {
    event.preventDefault();
    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupPasswordConfirm').value;
    
    // Check all validations and show appropriate messages
    if (!name || !email || !password || !confirmPassword) {
        showMessage('Please fill in all fields');
        return;
    }

    if (password !== confirmPassword) {
        showMessage('Passwords do not match');
        return;
    }
    
    if (password.length < 8) {
        showMessage('Password must be at least 8 characters');
        return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showMessage('Please enter a valid email address');
        return;
    }
    
    try {
        const { data, error } = await window.OmbeeConfig.supabase.auth.signUp({
            email: email,
            password: password,
            options: {
                data: {
                    name: name
                }
            }
        });
        
        if (error) {
            console.error('Signup error:', error);
            if (error.message.includes('User already registered')) {
                showMessage('An account with this email already exists');
            } else if (error.message.includes('invalid email')) {
                showMessage('Please enter a valid email address');
            } else if (error.message.includes('Password')) {
                showMessage('Password must be at least 8 characters');
            } else {
                showMessage(error.message || 'An error occurred during signup');
            }
            return;
        }
        
        // Create user in backend
        if (data.user) {
            await ensureBackendUser(data.user);
        }
        
        // Check if user is confirmed
        if (data.session) {
            showMessage('Account created and logged in! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            // User needs to verify email
            showMessage('Account created! Please check your email to verify.', 'success');
            setTimeout(() => showLogin(), 2000);
        }
    } catch (error) {
        showMessage('An unexpected error occurred. Please try again.');
        console.error('Signup error:', error);
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    // Form submissions
    document.getElementById('loginFormElement').addEventListener('submit', handleLogin);
    document.getElementById('signupFormElement').addEventListener('submit', handleSignup);
    
    // Switch forms
    document.getElementById('switchToSignup').addEventListener('click', showSignup);
    document.getElementById('switchToLogin').addEventListener('click', showLogin);
});