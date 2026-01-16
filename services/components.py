import streamlit as st

def load_css(file_name):
    """Load CSS from assets directory"""
    with open(f"assets/{file_name}", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def inject_styles():
    """Inject base styles into the page"""
    load_css("style.css")


def render_navbar(active_page="Dashboard"):
    """Render the navigation bar"""
    from services.auth import get_current_user, logout
    
    # Navbar styles are loaded via style.css

    user = get_current_user()
    user_name = user.get('name', 'User') if user else 'User'
    
    # Navigation row
    nav_items = [
        ("Dashboard", "pages/Dashboard.py"),
        ("Interview", "pages/Start_Interview.py"),
        ("History", "pages/History.py"),
    ]
    
    col_brand, col_nav1, col_nav2, col_nav3, col_user = st.columns([2, 1, 1, 1, 2])
    
    with col_brand:
        st.markdown(f"**AI Interview Coach** | {user_name}")
    
    for i, (name, page) in enumerate(nav_items):
        col = [col_nav1, col_nav2, col_nav3][i]
        with col:
            btn_type = "primary" if name == active_page else "secondary"
            if st.button(name, key=f"nav_{name}", type=btn_type, use_container_width=True):
                st.switch_page(page)
    
    with col_user:
        col_a, col_b = st.columns([2, 1])
        with col_b:
            if st.button("Sign Out", key="nav_signout"):
                logout()
                st.switch_page("Home.py")
    
    st.markdown("---")


def require_auth():
    """Check if user is authenticated, redirect if not"""
    from services.auth import check_auth
    
    if not check_auth():
        st.warning("Please sign in to access this page.")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Go to Sign In", type="primary", use_container_width=True):
                st.switch_page("pages/Sign_In.py")
        st.stop()
