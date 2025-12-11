"""
Supabase authentication for Ombee AI
"""
import streamlit as st
from datetime import datetime
from src.config import SUPABASE_URL, SUPABASE_API_KEY

def init_supabase():
    """Initialize Supabase client"""
    try:
        from supabase import create_client
        
        if not SUPABASE_URL or not SUPABASE_API_KEY:
            st.error("Supabase credentials not configured. Please check your config.py")
            return None
        
        return create_client(SUPABASE_URL, SUPABASE_API_KEY)
    except ImportError:
        st.error("Supabase not installed. Run: pip install supabase")
        return None
    except Exception as e:
        st.error(f"Supabase error: {e}")
        return None

def init_auth_state():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'  # 'login' or 'signup'
    if 'supabase_client' not in st.session_state:
        st.session_state.supabase_client = init_supabase()

def supabase_login(email: str, password: str, supabase) -> tuple[bool, str, dict]:
    """Supabase authentication"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Fetch user profile from database
            user_profile = supabase.table('user_profiles').select('*').eq('user_id', response.user.id).execute()
            
            if user_profile.data:
                user_data = user_profile.data[0]
                user_data['email'] = email
                return True, "Login Successful!", user_data
            else:
                # Create default profile if doesn't exist
                user_data = {
                    'user_id': response.user.id,
                    'email': email,
                    'name': email.split('@')[0].title(),
                    'preferences': {},
                    'is_admin': False
                }
                
                # Insert into database
                supabase.table('user_profiles').insert(user_data).execute()
                
                return True, "Login Successful!", user_data
        else:
            return False, "Login failed", None
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return False, "Invalid email or password", None
        return False, f"Authentication error: {error_msg}", None

def handle_email_confirmation():
    """Check URL parameters for email confirmation token and auto-login"""
    try:
        # Get query parameters from Streamlit
        query_params = st.query_params
        
        if "access_token" in query_params and st.session_state.supabase_client:
            access_token = query_params.get("access_token")
            token_type = query_params.get("type", "")
            
            if token_type == "recovery":
                st.info("Password reset link verified. Please enter your new password.")
                st.query_params.clear()
                return True
            else:
                # Generic token confirmation
                st.success("Verification successful! Please log in.")
                st.session_state.auth_mode = 'login'
                st.query_params.clear()
                return True
                
    except Exception as e:
        st.error(f"Confirmation error: {e}")
    
    return False

def supabase_signup(email: str, password: str, name: str, supabase) -> tuple[bool, str, dict | None]:
    """Supabase signup with trigger-based profile creation"""
    try:
        # Create auth user with name in metadata
        # The database trigger will automatically create the profile
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name
                }
            }
        })
        
        if response.user:
            # Check if this is an existing user trying to sign up again
            # Supabase returns the user but with identities empty for existing users
            if hasattr(response.user, 'identities') and len(response.user.identities) == 0:
                return False, "An account with this email already exists. Please log in instead.", None
            
            # Call login right after signup to set session
            success, message, user_data = supabase_login(email, password, supabase)
            
            if success:
                return True, "Account created successfully! Welcome to Ombee AI!", user_data
            else:
                return False, f"Account created, but automatic login failed: {message}", None
        else:
            return False, "Signup failed - no user returned", None
            
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's just the "Database error saving new user" message
        # but the user was actually created (common with triggers)
        if "Database error saving new user" in error_msg:
            return True, "Account created! Attempting to log you in...", None
        
        # Handle other specific errors
        if "User already registered" in error_msg or "already registered" in error_msg.lower():
            return False, "An account with this email already exists. Please log in instead.", None
        
        if "Password should be at least" in error_msg:
            return False, "Password is too weak. Please use at least 8 characters.", None
        
        
        # Generic error
        return False, f"Signup error: {error_msg}", None

def login(email: str, password: str) -> tuple[bool, str]:
    """Login with Supabase"""
    if not st.session_state.supabase_client:
        return False, "Database connection unavailable"
    
    success, message, user_data = supabase_login(email, password, st.session_state.supabase_client)
    if success:
        st.session_state.authenticated = True
        st.session_state.user_data = user_data
        return True, message
    else:
        return False, message

def signup(email: str, password: str, name: str) -> tuple[bool, str]:
    """User signup"""
    if not st.session_state.supabase_client:
        return False, "Database connection unavailable"
    
    success, message, user_data = supabase_signup(email, password, name, st.session_state.supabase_client)

    if success and user_data:
        st.session_state.authenticated = True
        st.session_state.user_data = user_data
        return True, message
    else:
        return success, message

def logout():
    """Logout current user"""
    if st.session_state.supabase_client:
        try:
            st.session_state.supabase_client.auth.sign_out()
        except:
            pass
    
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.show_login = True
    st.session_state.auth_mode = 'login'

def get_current_user():
    """Get current logged-in user data"""
    return st.session_state.get('user_data', None)

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def is_admin(user_data=None):
    """Check if current user is an admin based on Supabase user_profiles.is_admin"""
    if not user_data:
        user_data = get_current_user()
    if not user_data:
        return False
    
    # Check the is_admin flag from the database
    return user_data.get('is_admin', False)

def switch_to_login():
    """Switch to login mode"""
    st.session_state.auth_mode = 'login'

def switch_to_signup():
    """Switch to signup mode"""
    st.session_state.auth_mode = 'signup'

def render_login_page():
    """Render the login/signup page UI"""
    from src.theme import get_base64_image, apply_login_styles
    
    # Check for email confirmation
    handle_email_confirmation()

    # Apply login-specific styles
    apply_login_styles()
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo
        logo_base64 = get_base64_image("ombee_icon.png")
        if logo_base64:
            st.markdown(f"""
                <div class='login-logo-container'>
                    <img src='data:image/png;base64,{logo_base64}' class='login-logo'>
                </div>
            """, unsafe_allow_html=True)
        
        # Title
        st.markdown("""
            <h1 class='login-title'>Welcome to Ombee AI</h1>
            <p class='login-subtitle'>Your personalized holistic wellness assistant</p>
        """, unsafe_allow_html=True)
        
        # Check if Supabase is available
        if not st.session_state.supabase_client:
            st.error("Unable to connect to authentication service. Please check configuration.")
            st.stop()
        
        # Login Form
        if st.session_state.auth_mode == 'login':
            email = st.text_input(
                "Email Address",
                placeholder="you@example.com",
                key="login_email"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            login_clicked = st.button("Sign In", type="primary", use_container_width=True)
            
            if login_clicked:
                if email and password:
                    with st.spinner("Authenticating..."):
                        success, message = login(email, password)
                        if success:
                            st.success(message)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please enter both email and password")
            
            # Switch to signup
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            if st.button("Don't have an account? Sign Up", 
                        use_container_width=True,
                        on_click=switch_to_signup):
                pass
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Signup Form
        else:
            name = st.text_input(
                "Full Name",
                placeholder="John Smith",
                key="signup_name"
            )
            
            email = st.text_input(
                "Email Address",
                placeholder="you@example.com",
                key="signup_email"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Choose a strong password (min. 8 characters)",
                key="signup_password"
            )
            
            password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="signup_password_confirm"
            )
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

            signup_clicked = st.button("Create Account", type="primary", use_container_width=True)
            
            if signup_clicked:
                if not name or not email or not password:
                    st.warning("Please fill in all fields")
                    st.session_state.process_signup = False
                elif password != password_confirm:
                    st.error("Passwords do not match")
                    st.session_state.process_signup = False
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                    st.session_state.process_signup = False
                else:
                    with st.spinner("Creating your account..."):
                        success, message = signup(email, password, name)
                        if success:
                            st.success(message)
                            st.balloons()
                            # Rerun to reflect authenticated state
                            if is_authenticated():
                                st.rerun()
                            else:
                                st.session_state.auth_mode = 'login'
                        else:
                            st.error(message)
                        st.session_state.process_signup = False
            
            # Switch to login
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            if st.button("Already have an account? Sign In", 
                        use_container_width=True,
                        on_click=switch_to_login):
                pass
            st.markdown("</div>", unsafe_allow_html=True)

def render_user_profile_sidebar():
    """Render user profile in sidebar"""
    if not is_authenticated():
        return
    
    user = get_current_user()
    if not user:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Your Profile")
        
        # User info card
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(30, 30, 30, 0.95) 0%, rgba(40, 40, 40, 0.9) 100%);
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                        border: 1px solid rgba(236, 199, 25, 0.3);'>
                <p style='color: #ECC719; font-weight: 700; margin: 0 0 0.5rem 0;'>{user['name']}</p>
                <p style='color: #999999; font-size: 0.85rem; margin: 0;'>{user['email']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # User preferences expander
        with st.expander("Preferences"):
            prefs = user.get('preferences', {})
            
            if prefs.get('dietary_restrictions'):
                st.markdown(f"<p style='color: #e0e0e0;'><strong>Dietary:</strong> {', '.join(prefs['dietary_restrictions'])}</p>", unsafe_allow_html=True)
            
            if prefs.get('health_goals'):
                st.markdown("<p style='color: #e0e0e0;'><strong>Health Goals:</strong></p>", unsafe_allow_html=True)
                for goal in prefs['health_goals']:
                    st.markdown(f"<p style='color: #e0e0e0; margin-left: 1rem;'>• {goal}</p>", unsafe_allow_html=True)
            
            if prefs.get('budget_limit'):
                st.markdown(f"<p style='color: #e0e0e0;'><strong>Budget Limit:</strong> ${prefs['budget_limit']}/mo</p>", unsafe_allow_html=True)
            
            if prefs.get('phone_plan'):
                st.markdown(f"<p style='color: #e0e0e0;'><strong>Phone Plan:</strong> {prefs['phone_plan']}</p>", unsafe_allow_html=True)
        
        # Admin button (only show if user is admin)
        if is_admin(user):
            st.markdown("---")
            if st.button("Admin Panel", use_container_width=True):
                # Try to navigate to admin page
                import os
                
                # Debug: Check if file exists
                possible_paths = [
                    "pages/.admin_upload.py",
                    ".admin_upload.py",
                    "pages/admin_upload.py"
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        try:
                            st.switch_page(path)
                            return
                        except Exception as e:
                            continue
                
                # If none work, show error
                st.error(f"Could not find admin page. Please check file location.")
                st.info("Expected location: pages/admin_upload.py")
        
        # Logout button
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

def get_user_context_for_rag(user_data: dict) -> str:
    """Generate context string from user profile to enhance RAG responses"""
    if not user_data:
        return ""
    
    prefs = user_data.get('preferences', {})
    context_parts = [f"User: {user_data.get('name', 'User')}"]
    
    if prefs.get('dietary_restrictions'):
        context_parts.append(f"Dietary restrictions: {', '.join(prefs['dietary_restrictions'])}")
    
    if prefs.get('health_goals'):
        context_parts.append(f"Health goals: {', '.join(prefs['health_goals'])}")
    
    if prefs.get('budget_limit'):
        context_parts.append(f"Monthly budget: ${prefs['budget_limit']}")
    
    if prefs.get('phone_plan'):
        context_parts.append(f"Phone plan: {prefs['phone_plan']}")
    
    return " | ".join(context_parts)