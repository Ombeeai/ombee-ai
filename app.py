import streamlit as st
import time
import re
from src.router import detect_domain
from src.retriever import retrieve_context
from src.llm import generate_response
from src.demo_responses import get_demo_response, get_coming_soon_message
from src.theme import (
    apply_theme, 
    apply_login_page_styles, 
    apply_main_page_styles,
    apply_sidebar_styles,
    get_base64_image
)
from src.monitoring import get_monitor
from src.auth import (
    init_auth_state,
    is_authenticated,
    render_login_page,
    render_user_profile_sidebar,
    get_current_user,
    get_user_context_for_rag,
    is_admin
)

monitor = get_monitor()

# Page config with Ombee branding
st.set_page_config(
    page_title="Ombee AI Assistant",
    page_icon="ombee_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply main theme (inject CSS)
apply_theme()

# Initialize authentication state
init_auth_state()

# ==== AUTHENTICATION STATE =====
if not is_authenticated():
    apply_login_page_styles()
    render_login_page()
    st.stop()

# Apply main page styles
apply_main_page_styles()

current_user = get_current_user()
user_context = get_user_context_for_rag(current_user)

# Hide admin page from sidebar for non-admin users
if not is_admin(current_user):
    st.markdown("""
    <style>
    /* Hide admin_upload page from sidebar navigation */
    [data-testid="stSidebarNav"] a[href*="admin_upload"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for query handling
if 'query_input' not in st.session_state:
    st.session_state['query_input'] = ''
if 'current_query' not in st.session_state:
    st.session_state['current_query'] = ''
if 'process_query' not in st.session_state:
    st.session_state['process_query'] = False
if 'last_response' not in st.session_state:
    st.session_state['last_response'] = None

def convert_markdown_to_html(text):
    """Convert basic markdown syntax to HTML for rendering."""
    # Convert bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Convert italics
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Convert line breaks
    text = text.replace('\n', '<br>')
    return text

# Callback to submit when Enter is pressed in the text input
def submit_on_enter():
    if st.session_state.get('query_input','').strip():
        st.session_state['current_query'] = st.session_state.get('query_input', '')
        st.session_state['process_query'] = True
        # Clear input after submission
        st.session_state['query_input'] = ''  

# Header with logo
logo_base64 = get_base64_image("ombee_icon.png")
if logo_base64:
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <img src='data:image/png;base64,{logo_base64}' style='width: 80px; height: 80px; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 12px rgba(236, 199, 25, 0.3));'>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Ombee AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your personal multi-domain AI companion for health, finance, and connectivity</p>", unsafe_allow_html=True)

# Domain status cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='domain-card' style='border: 2px solid #4CAF50;'>
        <h3>Holistic Health</h3>
        <p style='color: #4CAF50; font-weight: bold; font-size: 1.3rem; margin: 0.5rem 0;'>✅ Active</p>
        <p style='font-size: 0.9rem; color: #cccccc; margin: 0;'>Nutrition & Wellness</p>
        <p style='font-size: 0.85rem; color: #999999; margin-top: 0.5rem;'>Live Now</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='domain-card' style='border: 2px solid #FFB300;'>
        <h3>Ombee Finance</h3>
        <p style='color: #FFB300; font-weight: bold; font-size: 1.3rem; margin: 0.5rem 0;'>🔄 In Development</p>
        <p style='font-size: 0.9rem; color: #cccccc; margin: 0;'>Budget & Spending</p>
        <p style='font-size: 0.85rem; color: #999999; margin-top: 0.5rem;'>Phase 2 - Q2 2026</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='domain-card' style='border: 2px solid #FFB300;'>
        <h3>Ombee Wireless</h3>
        <p style='color: #FFB300; font-weight: bold; font-size: 1.3rem; margin: 0.5rem 0;'>🔄 In Development</p>
        <p style='font-size: 0.9rem; color: #cccccc; margin: 0;'>Mobile & Plans</p>
        <p style='font-size: 0.85rem; color: #999999; margin-top: 0.5rem;'>Phase 2 - Q2 2026</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main chat interface
st.markdown("### Ask Ombee Anything")

# Example queries in a compact layout
st.markdown("**Try these examples:**")
col1, col2 = st.columns(2)

example_queries = {
    "🧘 Meditation for beginners": "What are some meditation techniques for beginners?",
    "🥗 Foods for high blood pressure": "What foods should I eat if I have high blood pressure?",
    "💤 Improve sleep quality": "How can I improve my sleep quality?",
    "💳 Restaurant spending": "How much did I spend on restaurants last month?",
    "📱 Current phone plan": "What's my current phone plan?",
    "📊 Data usage": "What's my data usage this month?"
}

# Display example buttons with proper callback
for idx, (label, query_text) in enumerate(example_queries.items()):
    col = col1 if idx % 2 == 0 else col2
    with col:
        if st.button(label, key=f"example_{idx}"):
            # fill input field and trigger processing
            st.session_state['query_input'] = ''
            st.session_state['current_query'] = query_text
            st.session_state['process_query'] = True
            st.rerun()

# Text input with Enter key support
query = st.text_input(
    "Your question:",
    placeholder="Ask about wellness, finances, or mobile services...",
    key="query_input",
    on_change=submit_on_enter,
    label_visibility="collapsed"
)

# Ask button
ask_clicked = st.button("Ask Ombee 🐝", type="primary", use_container_width=True)

# Process query if button clicked
if ask_clicked and st.session_state.get('query_input','').strip():
    st.session_state['current_query'] = st.session_state['query_input']
    st.session_state['process_query'] = True
    st.session_state['query_input'] = ''  # clear input after submission
    st.rerun()

query_to_process = st.session_state['current_query']

# Only show response if there's a query to process
if st.session_state['process_query'] and query_to_process:
    # Track start time for latency calculation
    start_time = time.time()
    
    # Create columns for response area
    response_col1, response_col2 = st.columns([3, 1])

    with response_col1:
        # Show user message
        st.markdown(f"**You asked:** {query_to_process}")
        st.markdown("")

        # Routing
        with st.spinner("🔍 Analyzing your question..."):
            time.sleep(0.3)
            domain, confidence = detect_domain(query_to_process)
        
        # Show routing decision with icon
        domain_icons = {"holistic": "💚", "financial": "💰", "telecom": "📱"}
        
        st.info(f"{domain_icons.get(domain, '🔍')} **Routed to {domain.upper()} domain** (confidence: {confidence:.0%})")
        
        context = ""
        retrieval_time = None
        generation_time = None
        cumulative_tokens = None
        cumulative_cost = None

        # Generate response
        with st.spinner("💭 Generating response..."):
            time.sleep(0.5)
            
            # Check for demo response first
            demo_response = get_demo_response(query_to_process, domain)
            
            if demo_response:
                # Demo data response
                response_text = demo_response['response']
                sources = demo_response['sources']
                status = demo_response['status']
                
            elif domain == 'holistic':
                # Real RAG response
                try:
                    context_enhanced_query = f"{user_context} | Query: {query_to_process}" if user_context else query_to_process
                    context, sources, retrieval_time = retrieve_context(context_enhanced_query)
                    response_text, generation_time, cumulative_tokens, cumulative_cost = generate_response(
                        query_to_process,
                        context,
                        user_context=user_context)
                    status = 'live'
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    response_text = "I encountered an error. Please try again."
                    sources = []
                    status = 'error'
            
            else:
                # Coming soon message
                response_text = get_coming_soon_message(domain, query_to_process)
                sources = []
                status = 'coming-soon'
        
        # Calculate latency
        end_time = time.time()
        latency = end_time - start_time

        # Log to Phoenix after response is generated
        if monitor and monitor.tracer:
            try:
                monitor.log_query(
                    query=query_to_process,
                    domain=domain,
                    confidence=confidence,
                    response=response_text,
                    sources=sources,
                    latency=latency,
                    context=context,
                    status=status,
                    retrieval_time=retrieval_time,
                    generation_time=generation_time,
                    cumulative_tokens=cumulative_tokens,
                    cumulative_cost=cumulative_cost,
                    user_id=current_user.get('user_id'),
                    user_context=user_context
                )
            except Exception as e:
                st.warning(f"Failed to log to Phoenix: {e}")
        
        # Display response in styled box with proper line breaks
        response_html = convert_markdown_to_html(response_text)
        st.markdown(f"""
        <div class='response-box'>
            {response_html}
        </div>
        """, unsafe_allow_html=True)
        
        # Status badge
        if status == 'live':
            st.success("✅ Live Response from Ombee Knowledge Base")
        elif status == 'demo':
            st.info("📊 Demo Data - Feature Preview (Phase 2)")
        elif status == 'coming-soon':
            st.warning("🔄 Feature In Development - Coming Q2 2026")
        
        # Sources
        if sources:
            with st.expander("📚 View Sources"):
                for source in sources:
                    st.markdown(f"• {source}")
                    
    with response_col2:
        # Info box
        st.markdown("### About This Response")
        if status == 'live':
            st.markdown(f"""
            **✅ Personalized for You**
            
            This answer considered:
            - Your dietary preferences
            - Your health goals
            - Ombee's knowledge base
            - Real-time AI synthesis
            
            *Tailored for {current_user['name']}*
            """)
        elif status == 'demo':
            st.markdown("""
            **📊 Demo Data**
            
            This is sample data showing how Ombee will work when integrated with:
            - Ombee Finance
            - Ombee Wireless
            
            Full integration coming Q2 2026.
            """)
        else:
            st.markdown("""
            **🔄 Coming Soon**
            
            This feature is currently in development as part of Phase 2.
            
            The holistic health domain is live now!
            """)
    
    # Store response data
    st.session_state['last_response'] = {
        'query': query_to_process,
        'domain': domain,
        'response': response_text,
        'status': status,
        'sources': sources
    }

    # Reset the process flag after handling
    st.session_state['process_query'] = False

# Sidebar with user profile and info
with st.sidebar:
    # Apply sidebar styles
    apply_sidebar_styles()
    
    # Add logo to sidebar
    if logo_base64:
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 1.5rem;'>
                <img src='data:image/png;base64,{logo_base64}' style='width: 100px; height: 100px; filter: drop-shadow(0 4px 12px rgba(236, 199, 25, 0.4));'>
            </div>
        """, unsafe_allow_html=True)
    
    render_user_profile_sidebar()

    st.markdown("---")

    st.markdown("### About Ombee AI")
    st.markdown("""
    Ombee AI is your intelligent personal assistant that understands your health, finances, and connectivity needs.
    
    **Currently Available:**
    - Holistic Health & Wellness
    - Nutrition guidance
    - Health education
    - Wellness support
    
    **Coming in Phase 2 (Q2 2026):**
    - 💰 Ombee Finance integration
    - 📱 Ombee Wireless integration
    """)
    
    st.markdown("---")
    
    st.markdown("### 📊 System Status")
    st.metric("Knowledge Base", "16 documents")
    st.metric("Domains Active", "1 of 3")
    st.metric("Response Quality", "High")
    
    st.markdown("---")
    
    st.markdown("""
    <div style='font-size: 0.85rem; color: #cccccc; text-align: center; padding: 1rem 0;'>
    <strong>Important:</strong><br>
    Ombee AI provides informational guidance only and is not a substitute for professional medical, financial, or technical advice.
    </div>
    """, unsafe_allow_html=True)