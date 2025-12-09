"""
Simple authentication for demo purposes
"""
import streamlit as st

DEMO_USERS = {
    "demo@ombee.com" : {
        "password": "demo123",
        "name": "John Smith",
        "user_id": "user_001",
        "preferences": {
            "dietary_restrictions": ["vegetarian"],
            "health_goals": ["better sleep","sleep management"],
            "budget_limit": 3000,
            "phone_plan":"Max"
        },
        "created_at": "2025-12-08"
    },
    "ksavage@ombee.com" : {
        "password": "password",
        "name": "Kasey Savage",
        "user_id": "user_002",
        "preferences": {
            "dietary_restrictions": [],
            "health_goals": ["weight loss", "muscle gains"],
            "budget_limit": 2500,
            "phone_plan": "Plus"
        },
        "created_at": "2025-12-08"
    }
}

def init_auth_state():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    if 'process_login' not in st.session_state:
        st.session_state.process_login = False

def login(email: str, password: str) -> tuple[bool,str]:
    """
    Authenticate user with email and password
    Returns: (success, message)
    """
    if email in DEMO_USERS:
        if DEMO_USERS[email]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.user_data = DEMO_USERS[email].copy()
            st.session_state.user_data['email'] = email
            return True, "Login Successful!"
        else:
            return False, "Incorrect Password"
    else:
        return False, "User not found"
    
def logout():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.show_login = True

def get_current_user():
    """Get current logged-in user data"""
    return st.session_state.get('user_data', None)

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def submit_login():
    """Callback to trigger login when Enter is pressed"""
    st.session_state.process_login = True

def render_login_page():
    """Render the login page UI"""
    from src.theme import get_base64_image
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo
        logo_base64 = get_base64_image("ombee_icon.png")
        if logo_base64:
            st.markdown(f"""
                <div style='text-align: center; margin: 1rem 0 1.5rem 0;'>
                    <img src='data:image/png;base64,{logo_base64}' 
                         style='width: 100px; height: 100px; 
                                filter: drop-shadow(0 4px 12px rgba(236, 199, 25, 0.4));'>
                </div>
            """, unsafe_allow_html=True)
        
        # Title
        st.markdown("""
            <h1 style='text-align: center; color: #ECC719; margin-bottom: 0.5rem; font-size: 2.5rem;'>
                Welcome to Ombee AI
            </h1>
            <p style='text-align: center; color: #b8b8b8; margin-bottom: 2rem; font-size: 1rem;'>
                Sign in to access your personalized AI assistant
            </p>
        """, unsafe_allow_html=True)
            
        # Login form inputs
        email = st.text_input(
            "Email",
            placeholder="demo@ombee.com",
            key="login_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
            on_change=submit_login
        )
        
        # Add small spacing
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # Buttons
        col_a, col_b = st.columns(2)
        with col_a:
            login_clicked = st.button("🔐 Sign In", type="primary", use_container_width=True)
        with col_b:
            demo_clicked = st.button("👤 Try Demo", use_container_width=True)
        
        # Process login if button clicked OR Enter pressed
        if login_clicked or st.session_state.get('process_login', False):
            if email and password:
                success, message = login(email, password)
                if success:
                    st.success(message)
                    st.session_state.process_login = False
                    st.rerun()
                else:
                    st.error(message)
                    st.session_state.process_login = False
            else:
                st.warning("Please enter both email and password")
                st.session_state.process_login = False
        
        if demo_clicked:
            success, message = login("demo@ombee.com", "demo123")
            if success:
                st.success("Logged in as demo user!")
                st.rerun()
        
        # Demo credentials info
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; color: #999999; font-size: 0.9rem;'>
                <p style='margin-top: 1rem; font-size: 0.85rem; color: #777777;'>
                    This is a demo authentication system.<br>
                    Production will use secure authentication (Supabase/Auth0)
                </p>
            </div>
        """, unsafe_allow_html=True)

def render_user_profile_sidebar():
    """Render user profile in sidebar"""
    if not is_authenticated():
        return
    
    user = get_current_user()
    if not user:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Your Profile")
        
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
        with st.expander("⚙️ Preferences"):
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
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

def get_user_context_for_rag(user_data: dict) -> str:
    """
    Generate context string from user profile to enhance RAG responses.
    This will be prepended to queries for personalized responses.
    """
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