import streamlit as st
import hashlib
from dotenv import load_dotenv

load_dotenv(override=True)

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def render_auth_form():
    """Render a simple authentication form"""
    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        email = st.text_input("Email address", key="signin_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="signin_password", placeholder="Enter password")
        
        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
        
        if st.button("Sign In", type="primary", use_container_width=True, key="signin_btn"):
            if email and password:
                st.session_state['is_authenticated'] = True
                st.session_state['current_user'] = {
                    'id': hash_password(email)[:16],
                    'email': email,
                    'name': email.split('@')[0].title()
                }
                st.success("Signed in successfully")
                st.rerun()
            else:
                st.error("Please enter email and password")
    
    with tab2:
        new_name = st.text_input("Full name", key="signup_name", placeholder="Your name")
        new_email = st.text_input("Email address", key="signup_email", placeholder="you@example.com")
        new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Create password")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm", placeholder="Confirm password")
        
        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
        
        if st.button("Create Account", type="primary", use_container_width=True, key="signup_btn"):
            if new_name and new_email and new_password:
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    st.session_state['is_authenticated'] = True
                    st.session_state['current_user'] = {
                        'id': hash_password(new_email)[:16],
                        'email': new_email,
                        'name': new_name
                    }
                    st.success("Account created successfully")
                    st.rerun()
            else:
                st.error("Please fill in all fields")


def render_user_profile():
    """Render user profile for signed-in users"""
    user = get_current_user()
    if not user:
        return
    
    initial = user.get('name', 'U')[0].upper()
    
    st.markdown(f"""
    <div style="text-align: center; padding: 32px; background: white; border-radius: 12px; border: 1px solid #e5e7eb;">
        <div style="width: 72px; height: 72px; background: #1a56db; border-radius: 50%; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; font-weight: 600;">
            {initial}
        </div>
        <div style="font-size: 20px; font-weight: 600; color: #111827; margin-bottom: 4px;">{user.get('name', 'User')}</div>
        <div style="font-size: 14px; color: #6b7280;">{user.get('email', '')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    if st.button("Continue to Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
    
    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
    
    if st.button("Sign Out", use_container_width=True):
        logout()
        st.rerun()


def check_auth():
    """Check if user is authenticated"""
    return st.session_state.get('is_authenticated', False)


def get_current_user():
    """Get current user data"""
    return st.session_state.get('current_user', None)


def set_user(user_data):
    """Set user data in session"""
    st.session_state['is_authenticated'] = True
    st.session_state['current_user'] = user_data


def logout():
    """Clear user session"""
    st.session_state['is_authenticated'] = False
    st.session_state['current_user'] = None


def require_auth():
    """Redirect to sign in if not authenticated"""
    if not check_auth():
        st.warning("Please sign in to access this page.")
        if st.button("Go to Sign In", type="primary"):
            st.switch_page("pages/Sign_In.py")
        st.stop()
