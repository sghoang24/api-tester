import streamlit as st
import requests
import json
import pandas as pd
import time
import os
from constants import DAI_COOKIES, SIT_COOKIES, UAT_COOKIES, DAI_BASE_URL, SIT_BASE_URL, UAT_BASE_URL
from utils import (
    get_base_url, 
    get_current_base_url, 
    get_user_specific_paths,
    cookies_dict_to_string,
    cookies_string_to_dict,
    load_user_apis,
    save_user_apis,
    load_api_configs,
    save_api_config,
    load_api_history,
    save_api_history,
    load_cookies_config,
    save_cookies_config,
    make_http_request,
    get_response_content,
    create_history_entry,
    get_existing_users,
    validate_username,
    ensure_path_format,
    load_environments_config,
    save_environments_config,
    get_enabled_environments
)


# Global admin cookies file
ADMIN_COOKIES_FILE = os.path.join(os.path.dirname(__file__), "admin_cookies_config.json")


def load_help_content():
    """Load help content from markdown file"""
    try:
        help_file_path = os.path.join(os.path.dirname(__file__), "HUONG_DAN_SU_DUNG.md")
        if os.path.exists(help_file_path):
            with open(help_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "Không tìm thấy file hướng dẫn sử dụng."
    except Exception as e:
        return f"Lỗi khi đọc file hướng dẫn: {str(e)}"


@st.dialog("📖 Hướng Dẫn Sử Dụng", width="large")
def show_help_dialog():
    """Show help dialog with markdown content"""
    help_content = load_help_content()
    st.markdown(help_content)


def save_to_predefined(api_name, api, file_paths):
    """Save API configuration to predefined configs shared by all users"""
    # Prepare config for saving
    save_config = api.copy()

    # Remove the full URL but keep the path
    if "url" in save_config:
        del save_config["url"]

    # Remove cookies as they are environment-specific
    if "cookies" in save_config:
        del save_config["cookies"]
    if "custom_cookies_string" in save_config:
        del save_config["custom_cookies_string"]

    # Save to predefined configurations
    configs = load_api_configs(file_paths["API_CONFIG_FILE"])
    configs[api_name] = save_config
    if save_api_config(configs, file_paths["API_CONFIG_FILE"]):
        st.success(f"API configuration for '{api_name}' saved to predefined configurations!")
    else:
        st.error("Failed to save to predefined configurations")


def show_multi_user_login():
    """Display the multi-user login page"""
    # Help button above title
    if st.button("📖 Hướng dẫn", key="login_help", help="Xem hướng dẫn sử dụng ứng dụng"):
        show_help_dialog()
    
    # Title
    st.title("API Client Tester")

    # Initialize logged in users if not exists
    if 'logged_in_users' not in st.session_state:
        st.session_state.logged_in_users = {}
    if 'active_user' not in st.session_state:
        st.session_state.active_user = None

    # Show currently logged in users
    if st.session_state.logged_in_users:
        st.subheader("Currently Logged In Users")
        cols = st.columns(len(st.session_state.logged_in_users) + 1)
        
        for i, (username, user_data) in enumerate(st.session_state.logged_in_users.items()):
            with cols[i]:
                is_active = st.session_state.active_user == username
                user_type = "Admin" if user_data.get('is_admin', False) else "User"
                status = "🟢 Active" if is_active else "⚫ Inactive"
                
                st.write(f"**{username}** ({user_type})")
                st.write(status)
                
                if not is_active:
                    if st.button(f"Switch to {username}", key=f"switch_{username}"):
                        st.session_state.active_user = username
                        _load_user_data(username)
                        st.rerun()
                
                if st.button(f"Logout {username}", key=f"logout_{username}"):
                    _logout_user(username)
                    st.rerun()

        # Add separator
        st.markdown("---")

        # Add New User button
        if st.button("➕ Add New User"):
            st.session_state.show_main_app = False
            st.rerun()

    # Get list of existing users
    user_dir = os.path.join(os.path.dirname(__file__), "user_data")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    # Get existing users but exclude already logged in users
    existing_users = get_existing_users()
    available_users = [u for u in existing_users if u not in st.session_state.logged_in_users]

    # Login options
    login_option = st.radio("Login Option", ["Existing User", "New User", "Admin Login"])

    if login_option == "Existing User":
        if available_users:
            username = st.selectbox("Select Username", available_users)
            login_button = st.button("Login")

            if login_button:
                _handle_multi_user_login(username, False)
        else:
            st.info("No available users to add. All existing users are already logged in.")

    elif login_option == "Admin Login":
        if "adminadmin" not in st.session_state.logged_in_users:
            st.subheader("Administrator Login")
            admin_password = st.text_input("Password", type="password", placeholder="Enter admin password")
            admin_login_button = st.button("Add Admin")

            if admin_login_button:
                if admin_password == "adminadmin":
                    _handle_multi_user_login("adminadmin", True)
                    st.success("Administrator added to session")
                    st.rerun()
                else:
                    st.error("Invalid admin password")
        else:
            st.info("Administrator is already logged in.")

    else:  # New User
        new_username = st.text_input("Enter New Username")
        create_button = st.button("Create and Add User")

        if create_button and new_username:
            all_users = list(st.session_state.logged_in_users.keys()) + existing_users
            error_msg = validate_username(new_username, all_users)
            if error_msg:
                st.error(error_msg)
            else:
                # Create user directory
                new_user_dir = os.path.join(user_dir, new_username)
                if not os.path.exists(new_user_dir):
                    os.makedirs(new_user_dir)

                _handle_multi_user_login(new_username, False)
                st.success(f"User {new_username} created and added to session")
                st.rerun()

    # Button to proceed to main app
    if st.session_state.logged_in_users:
        if st.button("🚀 Start Using API Tester", type="primary"):
            if not st.session_state.active_user:
                # Set first user as active if none selected
                st.session_state.active_user = list(st.session_state.logged_in_users.keys())[0]
                _load_user_data(st.session_state.active_user)

            st.session_state.show_main_app = True
            st.rerun()


def _handle_multi_user_login(username: str, is_admin: bool):
    """Handle multi-user login setup"""
    # Add user to logged in users
    st.session_state.logged_in_users[username] = {
        'is_admin': is_admin,
        'file_paths': get_user_specific_paths(username),
        'apis': {},
        'api_responses': {},
        'current_env': "SIT",
        'api_history': [],
        'cookies_config': {}
    }

    # Set as active user if it's the first one or if no active user
    if not st.session_state.active_user or len(st.session_state.logged_in_users) == 1:
        st.session_state.active_user = username
        _load_user_data(username)

    if not is_admin:
        st.success(f"User {username} added to session")


def _load_user_data(username: str):
    """Load data for the specified user and set as active"""
    if username not in st.session_state.logged_in_users:
        return

    user_data = st.session_state.logged_in_users[username]

    # Set current user context
    st.session_state.username = username
    st.session_state.is_admin = user_data['is_admin']
    st.session_state.file_paths = user_data['file_paths']

    # Load user's saved data if not already loaded
    if not user_data['apis']:
        try:
            user_data['apis'] = load_user_apis(user_data['file_paths']["USER_APIS_FILE"])
        except Exception as e:
            st.error(f"Error loading user APIs for {username}: {str(e)}")
            user_data['apis'] = {}

    if not user_data['api_history']:
        user_data['api_history'] = load_api_history(user_data['file_paths']["API_HISTORY_FILE"])

    if not user_data['cookies_config']:
        user_data['cookies_config'] = load_cookies_config(
            user_data['file_paths']["COOKIES_CONFIG_FILE"],
            ADMIN_COOKIES_FILE
        )

    # Set session state to current user's data
    st.session_state.apis = user_data['apis']
    st.session_state.api_responses = user_data['api_responses']
    st.session_state.current_env = user_data['current_env']
    st.session_state.api_history = user_data['api_history']
    st.session_state.cookies_config = user_data['cookies_config']


def _logout_user(username: str):
    """Logout a specific user"""
    if username in st.session_state.logged_in_users:
        # Save user's data before removing
        user_data = st.session_state.logged_in_users[username]
        if user_data['apis']:
            save_user_apis(user_data['apis'], user_data['file_paths']["USER_APIS_FILE"])

        # Remove user from logged in users
        del st.session_state.logged_in_users[username]

        # If this was the active user, switch to another user or clear session
        if st.session_state.active_user == username:
            if st.session_state.logged_in_users:
                # Switch to first available user
                new_active_user = list(st.session_state.logged_in_users.keys())[0]
                st.session_state.active_user = new_active_user
                _load_user_data(new_active_user)
            else:
                # No users left, clear session
                st.session_state.active_user = None
                st.session_state.show_main_app = False
                for key in ['username', 'is_admin', 'file_paths', 'apis', 'api_responses', 
                           'current_env', 'api_history', 'cookies_config']:
                    if key in st.session_state:
                        del st.session_state[key]


def _save_current_user_data():
    """Save current user's data back to the logged_in_users dict"""
    if st.session_state.active_user and st.session_state.active_user in st.session_state.logged_in_users:
        user_data = st.session_state.logged_in_users[st.session_state.active_user]
        user_data['apis'] = st.session_state.get('apis', {})
        user_data['api_responses'] = st.session_state.get('api_responses', {})
        user_data['current_env'] = st.session_state.get('current_env', 'SIT')
        user_data['api_history'] = st.session_state.get('api_history', [])
        user_data['cookies_config'] = st.session_state.get('cookies_config', {})

def show_admin_panel():
    """Display admin panel for global environment and cookie configuration"""
    if not st.session_state.get("is_admin", False):
        st.warning("Admin access required")
        return

    st.title("Admin Panel - Environment & Cookie Management")

    # Load environments configuration
    environments = load_environments_config()
    
    # Create tabs for different admin functions
    env_tab, cookie_tab = st.tabs(["🌐 Environment Management", "🍪 Cookie Configuration"])
    
    with env_tab:
        st.subheader("Environment Management")
        st.info("Manage environments that will be available to all users.")
        
        # Display existing environments
        st.write("**Current Environments:**")
        for env_name, config in environments.items():
            col1, col2, col3, col4 = st.columns([2, 4, 2, 1])
            
            with col1:
                status = "🟢 Enabled" if config.get('enabled', True) else "🔴 Disabled"
                st.write(f"**{env_name}**")
                st.write(status)
            
            with col2:
                st.text(config.get('base_url', ''))
            
            with col3:
                # Toggle enable/disable
                current_status = config.get('enabled', True)
                if st.button(f"{'Disable' if current_status else 'Enable'}", key=f"toggle_{env_name}"):
                    environments[env_name]['enabled'] = not current_status
                    if save_environments_config(environments):
                        st.success(f"Environment {env_name} {'disabled' if current_status else 'enabled'}")
                        st.rerun()
                    else:
                        st.error("Failed to update environment")
            
            with col4:
                # Delete environment (except core ones)
                if env_name not in ['SIT', 'DAI', 'UAT']:
                    if st.button("🗑️", key=f"delete_{env_name}", help="Delete environment"):
                        del environments[env_name]
                        if save_environments_config(environments):
                            st.success(f"Environment {env_name} deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete environment")
        
        st.markdown("---")
        
        # Add new environment
        st.subheader("Add New Environment")
        with st.form("add_environment_form"):
            new_env_name = st.text_input("Environment Name", help="e.g., PROD, DEV, STAGING")
            new_env_url = st.text_input("Base URL", help="e.g., https://api.example.com/v1")
            new_env_cookies = st.text_area("Default Cookies", help="Optional default cookies for this environment")
            
            submitted = st.form_submit_button("Add Environment")
            
            if submitted:
                if not new_env_name or not new_env_url:
                    st.error("Environment name and base URL are required")
                elif new_env_name.upper() in environments:
                    st.error(f"Environment {new_env_name.upper()} already exists")
                else:
                    # Add new environment
                    environments[new_env_name.upper()] = {
                        "name": new_env_name.upper(),
                        "base_url": new_env_url,
                        "default_cookies": new_env_cookies,
                        "enabled": True
                    }
                    
                    if save_environments_config(environments):
                        st.success(f"Environment {new_env_name.upper()} added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add environment")
    
    with cookie_tab:
        st.subheader("Global Cookie Configuration")
        st.info("Configure global cookies that will be used by all users unless they override them.")
        
        # Load admin cookies
        admin_cookies = {}
        if os.path.exists(ADMIN_COOKIES_FILE):
            try:
                admin_cookies = load_api_configs(ADMIN_COOKIES_FILE)
            except Exception:
                admin_cookies = {}

        # Get enabled environments for cookie configuration
        enabled_envs = get_enabled_environments()
        
        if enabled_envs:
            # Create tabs for each enabled environment
            env_tabs = st.tabs(enabled_envs)

            for i, env in enumerate(enabled_envs):
                with env_tabs[i]:
                    st.subheader(f"{env} Environment Cookies")
                    
                    # Get current cookies (from admin file or environment default)
                    env_cookies_string = admin_cookies.get(env, "")
                    if not env_cookies_string and env in environments:
                        env_cookies_string = environments[env].get('default_cookies', '')
                    
                    # Display as editable text area
                    cookies_string = st.text_area(
                        f"Edit cookies for {env} (format: name1=value1; name2=value2)",
                        value=env_cookies_string,
                        height=150,
                        key=f"admin_cookies_{env}"
                    )
                    
                    # Save button for this environment
                    if st.button(f"Save {env} Cookies", key=f"save_admin_{env}"):
                        admin_cookies[env] = cookies_string
                        if save_cookies_config(admin_cookies, ADMIN_COOKIES_FILE):
                            st.success(f"Global cookies for {env} saved successfully!")
                        else:
                            st.error(f"Failed to save cookies for {env}")

            # Reset to defaults button
            if st.button("Reset All to Environment Defaults"):
                admin_cookies = {}
                for env in enabled_envs:
                    if env in environments:
                        admin_cookies[env] = environments[env].get('default_cookies', '')
                
                if save_cookies_config(admin_cookies, ADMIN_COOKIES_FILE):
                    st.success("All environments reset to default cookies")
                else:
                    st.error("Failed to reset cookies")
                st.rerun()
        else:
            st.warning("No enabled environments found. Please enable at least one environment in the Environment Management tab.")

    if st.button("Back to API Tester"):
        st.session_state.admin_mode = False
        st.rerun()
def main():
    """Main."""
    # Initialize session state
    if "logged_in_users" not in st.session_state:
        st.session_state.logged_in_users = {}
    if "active_user" not in st.session_state:
        st.session_state.active_user = None
    if "show_main_app" not in st.session_state:
        st.session_state.show_main_app = False

    # Show login page if no users are logged in or main app not started
    if not st.session_state.logged_in_users or not st.session_state.show_main_app:
        show_multi_user_login()
        return

    # Check if admin mode is active
    if (st.session_state.get("is_admin", False) and 
        st.session_state.get("admin_mode", False)):
        show_admin_panel()
        return

    # Save current user data before any operations
    _save_current_user_data()

    # Get file paths for current user
    file_paths = st.session_state.file_paths

    # Help button above title
    if st.button("📖 Hướng dẫn", help="Xem hướng dẫn sử dụng ứng dụng"):
        show_help_dialog()

    # Create a layout with title and user switcher
    title_col, user_col, _ = st.columns([2, 3, 3])

    with title_col:
        st.markdown(
            f"<h3 style='margin:0;'>API Tester - {st.session_state.username}</h3>",
            unsafe_allow_html=True
        )

    with user_col:
        # User switcher dropdown
        user_options = list(st.session_state.logged_in_users.keys())
        current_index = user_options.index(st.session_state.active_user) if st.session_state.active_user in user_options else 0

        selected_user = st.selectbox(
            "Switch User",
            user_options,
            index=current_index,
            key="user_switcher"
        )

        if selected_user != st.session_state.active_user:
            st.session_state.active_user = selected_user
            _load_user_data(selected_user)
            st.rerun()

    # Initialize session state for current user
    if 'api_responses' not in st.session_state:
        st.session_state.api_responses = {}
    if 'current_env' not in st.session_state:
        st.session_state.current_env = "SIT"

    # Admin options and logout in sidebar
    st.sidebar.markdown(f"**Active User:** {st.session_state.username}")

    if st.session_state.get("is_admin", False):
        if st.sidebar.button("Admin Panel"):
            st.session_state.admin_mode = True
            st.rerun()

    # Individual user logout
    if st.sidebar.button(f"🚪 Logout {st.session_state.username}"):
        _logout_user(st.session_state.username)
        st.rerun()

    # Environment selector - use enabled environments
    enabled_envs = get_enabled_environments()
    current_env_index = 0
    
    if st.session_state.current_env in enabled_envs:
        current_env_index = enabled_envs.index(st.session_state.current_env)
    elif enabled_envs:
        # If current env is not available, default to first enabled env
        st.session_state.current_env = enabled_envs[0]
        current_env_index = 0
    
    if enabled_envs:
        env = st.sidebar.selectbox(
            "Environment", 
            enabled_envs,
            index=current_env_index
        )
        
        if env != st.session_state.current_env:
            st.session_state.current_env = env
            # Update current user's environment
            if st.session_state.active_user in st.session_state.logged_in_users:
                st.session_state.logged_in_users[st.session_state.active_user]['current_env'] = env

            # Update URLs for all APIs to use the new environment's base URL
            for api_name in st.session_state.apis:
                if "path" in st.session_state.apis[api_name]:
                    path = st.session_state.apis[api_name]["path"]
                    st.session_state.apis[api_name]["url"] = f"{get_current_base_url(env)}{path}"

            st.rerun()
    else:
        st.sidebar.warning("No environments enabled. Contact admin.")

    # Show current base URL
    st.sidebar.info(f"Base URL: {get_current_base_url(st.session_state.current_env)}")

    # Cookies management section in sidebar
    with st.sidebar.expander("Manage Environment Cookies"):
        manage_cookies(file_paths["COOKIES_CONFIG_FILE"])

    # Create a two-column layout
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("API Management")
        add_new_api()

        # Predefined API Tests
        st.subheader("Predefined API Tests")
        load_predefined_api(file_paths["API_CONFIG_FILE"])

        # List of saved APIs
        if st.session_state.apis:
            st.subheader("Saved APIs")

            # Create a container with fixed height for scrolling
            api_list_container = st.container()

            # Set max height with CSS to enable scrolling
            api_list_container.markdown("""
            <style>
            .api-list {
                max-height: 300px;
                overflow-y: auto;
                padding-right: 10px;
            }
            </style>
            """, unsafe_allow_html=True)

            # Create scrollable area
            with api_list_container:
                st.markdown('<div class="api-list">', unsafe_allow_html=True)

                # Display each API with open, rename and delete buttons
                for api_name in list(st.session_state.apis.keys()):  # Use list to avoid dictionary size change during iteration
                    cols = st.columns([3, 1, 1, 1])

                    # Display API name
                    cols[0].write(api_name)

                    # Open button
                    if cols[1].button("🔍", key=f"open_{api_name}"):
                        st.session_state.current_api = api_name
                        st.rerun()

                    # Rename button
                    if cols[2].button("✏️", key=f"rename_{api_name}"):
                        # Show rename form
                        st.session_state[f"rename_mode_{api_name}"] = True
                        st.rerun()

                    # Delete button
                    if cols[3].button("🗑️", key=f"del_{api_name}"):
                        # Delete the API
                        del st.session_state.apis[api_name]

                        # Also delete any associated response
                        if api_name in st.session_state.api_responses:
                            del st.session_state.api_responses[api_name]

                        # Update current_api if needed
                        if 'current_api' in st.session_state and st.session_state.current_api == api_name:
                            if st.session_state.apis:
                                st.session_state.current_api = next(iter(st.session_state.apis))
                            else:
                                del st.session_state.current_api

                        # Save the updated APIs to file
                        save_user_apis(st.session_state.apis, st.session_state.file_paths["USER_APIS_FILE"])

                        st.success(f"Deleted API: {api_name}")
                        st.rerun()

                    # Show rename form if in rename mode
                    if st.session_state.get(f"rename_mode_{api_name}", False):
                        with st.form(key=f"rename_form_{api_name}"):
                            new_name = st.text_input("New name", value=api_name)

                            rename_cols = st.columns(2)
                            rename_submit = rename_cols[0].form_submit_button("Save")
                            rename_cancel = rename_cols[1].form_submit_button("Cancel")

                            if rename_submit and new_name:
                                if new_name != api_name:
                                    if new_name in st.session_state.apis:
                                        st.error(f"Name '{new_name}' already exists")
                                    else:
                                        # Create a copy of the API with the new name
                                        st.session_state.apis[new_name] = st.session_state.apis[api_name].copy()

                                        # Copy response data if exists
                                        if api_name in st.session_state.api_responses:
                                            st.session_state.api_responses[new_name] = st.session_state.api_responses[api_name]

                                        # Delete old API
                                        del st.session_state.apis[api_name]

                                        # Update current_api if needed
                                        if 'current_api' in st.session_state and st.session_state.current_api == api_name:
                                            st.session_state.current_api = new_name

                                        # Save updated APIs to file
                                        save_user_apis(st.session_state.apis, st.session_state.file_paths["USER_APIS_FILE"])

                                        st.success(f"Renamed '{api_name}' to '{new_name}'")

                                        # Reset rename mode
                                        del st.session_state[f"rename_mode_{api_name}"]
                                        st.rerun()

                            if rename_cancel:
                                # Reset rename mode
                                del st.session_state[f"rename_mode_{api_name}"]
                                st.rerun()

                    # Add a separator line
                    st.markdown("---")

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No APIs added yet. Add one above or load from predefined tests.")

    with col2:
        if 'current_api' in st.session_state:
            if st.session_state.current_api in st.session_state.apis:
                display_api_tester(st.session_state.current_api, file_paths)
            else:
                st.info("Select an API to test or add a new one.")
        else:
            st.info("Select an API to test or add a new one.")


def manage_cookies(file_path):
    """Manage cookies for each environment using string format"""
    st.subheader("Cookies for " + st.session_state.current_env)
    
    # Get current environment cookies string
    env_cookies_string = st.session_state.cookies_config.get(st.session_state.current_env, "")

    # Display as editable text area with string format
    cookies_string = st.text_area(
        "Edit cookies (format: name1=value1; name2=value2)",
        value=env_cookies_string,
        height=150,
        help="Enter cookies in standard format: name1=value1; name2=value2"
    )

    # Save button
    if st.button("Save Cookies"):
        # Save the cookies string
        st.session_state.cookies_config[st.session_state.current_env] = cookies_string

        # Save to file and update user data
        if save_cookies_config(st.session_state.cookies_config, file_path):
            _save_current_user_data()  # Update the logged_in_users dict
            st.success(f"Cookies for {st.session_state.current_env} saved successfully!")
        else:
            st.error("Failed to save cookies configuration")

    # Reset to admin defaults button
    if st.button("Reset to Admin Defaults"):
        # Load admin cookies
        admin_cookies = {}
        if os.path.exists(ADMIN_COOKIES_FILE):
            try:
                admin_cookies = load_api_configs(ADMIN_COOKIES_FILE)
            except:
                admin_cookies = {}
        
        if st.session_state.current_env in admin_cookies:
            st.session_state.cookies_config[st.session_state.current_env] = admin_cookies[st.session_state.current_env]
        else:
            # Fallback to environment default cookies
            environments = load_environments_config()
            if st.session_state.current_env in environments:
                default_cookies = environments[st.session_state.current_env].get('default_cookies', '')
                st.session_state.cookies_config[st.session_state.current_env] = default_cookies
            else:
                # Final fallback to constants
                if st.session_state.current_env == "DAI":
                    st.session_state.cookies_config[st.session_state.current_env] = DAI_COOKIES
                elif st.session_state.current_env == "SIT":
                    st.session_state.cookies_config[st.session_state.current_env] = SIT_COOKIES
                elif st.session_state.current_env == "UAT":
                    st.session_state.cookies_config[st.session_state.current_env] = UAT_COOKIES
                else:
                    st.session_state.cookies_config[st.session_state.current_env] = ""
        
        # Save to file and update user data
        save_cookies_config(st.session_state.cookies_config, file_path)
        _save_current_user_data()
        st.success(f"Cookies for {st.session_state.current_env} reset to admin defaults")
        st.rerun()
def add_new_api():
    """Add new API."""
    with st.form("add_api_form"):
        api_name = st.text_input("API Name")
        
        # Instead of full URL, just ask for the path (with leading slash)
        api_path = st.text_input(
            "API Path (starts with /)", 
            help="Enter the API path starting with a slash (e.g., /subjectcomponent/list)"
        )

        method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE", "PATCH"])

        submitted = st.form_submit_button("Add API")
        if submitted and api_name and api_path:
            # Ensure path starts with a slash
            api_path = ensure_path_format(api_path)

            # Combine base URL with path
            api_url = f"{get_current_base_url(st.session_state.current_env)}{api_path}"

            st.session_state.apis[api_name] = {
                "url": api_url,
                "path": api_path,  # Store the path separately
                "method": method,
                "headers": {},
                "params": {},
                "body": {}
            }
            st.session_state.current_api = api_name

            # Save to file and update user data
            save_user_apis(st.session_state.apis, st.session_state.file_paths["USER_APIS_FILE"])
            _save_current_user_data()

            st.success(f"API '{api_name}' added successfully!")


def load_predefined_api(file_path):
    """Load predefined API for viewing without saving to user list"""
    # Load predefined API tests from JSON file
    predefined_configs = load_api_configs(file_path)

    if not predefined_configs:
        st.warning("No predefined API configurations found")
        return

    # Create a dropdown for predefined APIs
    selected_api = st.selectbox(
        "Select Predefined API Test",
        list(predefined_configs.keys())
    )

    if st.button("Load Predefined Test"):
        # Convert the configuration to a complete API configuration
        api_config = predefined_configs[selected_api].copy()

        # Get the path from the config
        path = api_config.get("path", "")

        # Ensure path starts with a slash
        path = ensure_path_format(path) if path else ""

        # Add the full URL based on current environment
        api_config["url"] = f"{get_current_base_url(st.session_state.current_env)}{path}"

        # Make sure path is stored
        api_config["path"] = path

        # Create a temporary name with special marker
        temp_api_name = f"temp_{selected_api}"

        # Store in session state directly in the apis dictionary, but with a flag
        st.session_state.apis[temp_api_name] = api_config
        st.session_state.apis[temp_api_name]["is_temporary"] = True
        st.session_state.apis[temp_api_name]["original_name"] = selected_api

        # Set as current API for viewing
        st.session_state.current_api = temp_api_name

        st.success(f"Loaded '{selected_api}' API test (preview)")
        st.info("This API is in preview mode. Save it to add permanently to your saved APIs.")
        st.rerun()

def _render_headers_section(api):
    """Render the headers section of the API tester"""
    with st.expander("Headers", expanded=False):
        st.write("Add or modify headers:")

        # Display existing headers
        if api.get('headers'):
            for header_key in list(api['headers'].keys()):
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.text(header_key)
                with col2:
                    new_value = st.text_input(f"Value for {header_key}", 
                                             value=api['headers'][header_key], 
                                             key=f"header_value_{header_key}")
                    api['headers'][header_key] = new_value
                with col3:
                    if st.button("Delete", key=f"delete_header_{header_key}"):
                        del api['headers'][header_key]
                        st.rerun()

        # Add new header
        new_header_key = st.text_input("New Header Name")
        new_header_value = st.text_input("New Header Value")
        if st.button("Add Header") and new_header_key:
            if 'headers' not in api:
                api['headers'] = {}
            api['headers'][new_header_key] = new_header_value
            st.rerun()

def _render_parameters_section(api):
    """Render the parameters section for GET requests"""
    with st.expander("Query Parameters", expanded=True):
        st.write("Add or modify query parameters:")

        # Display existing parameters
        if api.get('params'):
            for param_key in list(api['params'].keys()):
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.text(param_key)
                with col2:
                    new_value = st.text_input(f"Value for {param_key}", 
                                            value=api['params'][param_key], 
                                            key=f"param_value_{param_key}")
                    api['params'][param_key] = new_value
                with col3:
                    if st.button("Delete", key=f"delete_param_{param_key}"):
                        del api['params'][param_key]
                        st.rerun()

        # Add new parameter
        new_param_key = st.text_input("New Parameter Name")
        new_param_value = st.text_input("New Parameter Value")
        if st.button("Add Parameter") and new_param_key:
            if 'params' not in api:
                api['params'] = {}
            api['params'][new_param_key] = new_param_value
            st.rerun()


def _render_body_section(api):
    """Render the request body section for POST/PUT/PATCH requests"""
    with st.expander("Request Body", expanded=True):
        # Show as JSON editor
        if 'body' not in api:
            api['body'] = {}

        body_json = st.text_area(
            "JSON Body", 
            value=json.dumps(api['body'], indent=2),
            height=300
        )

        try:
            api['body'] = json.loads(body_json)
        except json.JSONDecodeError:
            st.error("Invalid JSON format")


def _render_cookies_section(api):
    """Render the cookies configuration section"""
    cookie_options = ["Use Environment Cookies", "No Cookies", "Custom Cookies"]
    cookie_choice = st.selectbox(
        "Cookie Options", 
        cookie_options,
        index=0  # Default to "Use Environment Cookies"
    )

    if cookie_choice == "Use Environment Cookies":
        # Use cookies from the cookies_config for the current environment
        cookies_string = st.session_state.cookies_config.get(st.session_state.current_env, "")
        api['cookies'] = cookies_string_to_dict(cookies_string)
        st.info(f"Using {st.session_state.current_env} environment cookies")
    elif cookie_choice == "Custom Cookies":
        # Allow custom cookies input as string
        with st.expander("Custom Cookies", expanded=True):
            # Store the string version for display
            if 'custom_cookies_string' not in api:
                api['custom_cookies_string'] = ""

            cookies_string = st.text_area(
                "Custom Cookies (format: name1=value1; name2=value2)", 
                value=api.get('custom_cookies_string', ""),
                height=150,
                help="Enter cookies in standard format: name1=value1; name2=value2"
            )

            api['custom_cookies_string'] = cookies_string
            api['cookies'] = cookies_string_to_dict(cookies_string)
    else:
        # No cookies
        api['cookies'] = {}


def _render_action_buttons(api_name, api, file_paths, is_temp):
    """Render the action buttons (Save, Send, Delete)"""
    # Add a state variable to track when save form should be shown
    if "show_save_form" not in st.session_state:
        st.session_state.show_save_form = False

    # Create columns with adjusted widths to bring buttons closer
    col_btn1, col_btn2, col_btn3, col_space = st.columns([1, 1, 1, 6])

    # Save API configuration with icon
    save_button = col_btn1.button(
        "💾", # Save icon
        key=f"save_btn_{api_name}",
        help="Save API Configuration"
    )

    # Send request with icon
    send_button = col_btn2.button(
        "▶️", # Play/send icon
        key=f"send_btn_{api_name}",
        help="Send Request"
    )

    # Delete API with icon
    delete_button = col_btn3.button(
        "🗑️", # Trash icon
        key=f"delete_btn_{api_name}",
        help="Delete API"
    )

    # Handle save button click
    if save_button:
        _handle_save_button(api_name, api, file_paths, is_temp)

    # Handle send button click
    if send_button:
        _handle_send_button(api_name, api, file_paths)

    # Handle delete button click
    if delete_button:
        _handle_delete_button(api_name, file_paths)


def _handle_save_button(api_name, api, file_paths, is_temp):
    """Handle save button click"""
    if is_temp:
        # Direct save for temporary APIs without showing form dialog
        # Use the original suggested name
        suggested_name = api.get("original_name", api_name.replace("temp_", ""))
        
        # Check if the name already exists
        if suggested_name in st.session_state.apis and suggested_name != api_name:
            # Add a number suffix to make it unique
            counter = 1
            base_name = suggested_name
            while f"{base_name}_{counter}" in st.session_state.apis:
                counter += 1
            suggested_name = f"{base_name}_{counter}"

        # Create a clean copy of the API without temporary flags
        permanent_api = api.copy()
        if "is_temporary" in permanent_api:
            del permanent_api["is_temporary"]
        if "original_name" in permanent_api:
            del permanent_api["original_name"]

        # Save the permanent version
        st.session_state.apis[suggested_name] = permanent_api

        # Remove the temporary version if different name
        if suggested_name != api_name:
            del st.session_state.apis[api_name]

        # Update current API reference
        st.session_state.current_api = suggested_name

        # Save to file and update user data
        if save_user_apis(st.session_state.apis, file_paths["USER_APIS_FILE"]):
            _save_current_user_data()  # Update the logged_in_users dict
            st.success(f"API configuration saved as '{suggested_name}'")
        else:
            st.error("Failed to save API configuration")
        st.rerun()
    else:
        # Direct save for non-temporary APIs
        st.session_state.apis[api_name] = api.copy()

        # Save to user's file and update user data
        if save_user_apis(st.session_state.apis, file_paths["USER_APIS_FILE"]):
            _save_current_user_data()  # Update the logged_in_users dict
            st.success("API configuration updated")
        else:
            st.error("Failed to update API configuration")
        st.rerun()


def _handle_send_button(api_name, api, file_paths):
    """Handle send request button click"""
    with st.spinner("Sending request..."):
        try:
            start_time = time.time()
            response = make_http_request(api)
            end_time = time.time()

            # Save response
            st.session_state.api_responses[api_name] = {
                "status_code": response.status_code,
                "time": round((end_time - start_time) * 1000, 2),
                "headers": dict(response.headers),
                "content": get_response_content(response)
            }

            # Save to history
            _save_to_history(api_name, api, st.session_state.api_responses[api_name], file_paths["API_HISTORY_FILE"])

            # Update user data
            _save_current_user_data()

            # Display success message
            st.success(f"Request completed in {st.session_state.api_responses[api_name]['time']} ms")

            # Rerun the app to update the history in the sidebar
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")


def _handle_delete_button(api_name, file_paths):
    """Handle delete API button click"""
    del st.session_state.apis[api_name]
    if api_name in st.session_state.api_responses:
        del st.session_state.api_responses[api_name]
    if 'current_api' in st.session_state:
        del st.session_state.current_api

    # Save updated APIs to file and update user data
    if save_user_apis(st.session_state.apis, file_paths["USER_APIS_FILE"]):
        _save_current_user_data()  # Update the logged_in_users dict
        st.success(f"API '{api_name}' deleted successfully")
    else:
        st.error("Failed to delete API")

    st.rerun()


def _render_response_section(api_name):
    """Render the response section"""
    if api_name in st.session_state.api_responses:
        resp = st.session_state.api_responses[api_name]
        st.subheader("Response")

        # Status and timing info
        st.write(f"Status Code: {resp['status_code']} | Time: {resp['time']} ms")

        # Response tabs
        tab1, tab2 = st.tabs(["Response Body", "Headers"])

        with tab1:
            if isinstance(resp['content'], dict) or isinstance(resp['content'], list):
                st.json(resp['content'])
            else:
                st.text(resp['content'])

        with tab2:
            st.json(resp['headers'])


def _save_to_history(api_name, api_config, response, file_path):
    """Save successful API calls to history"""
    if 'api_history' not in st.session_state:
        st.session_state.api_history = []

    # Create history entry
    history_entry = create_history_entry(
        api_name,
        api_config,
        response,
        st.session_state.current_env
    )

    # Add to history (limit to 50 entries)
    st.session_state.api_history.insert(0, history_entry)
    if len(st.session_state.api_history) > 50:
        st.session_state.api_history = st.session_state.api_history[:50]

    # Save history to file
    save_api_history(st.session_state.api_history, file_path)

    # Update user data
    _save_current_user_data()


def display_api_tester(api_name, file_paths):
    """Display API tester."""
    # Get the API configuration
    if api_name not in st.session_state.apis:
        st.error(f"API '{api_name}' not found.")
        return

    api = st.session_state.apis[api_name]

    # Check if this is a temporary API
    is_temp = api.get("is_temporary", False)

    st.subheader(f"Testing: {api_name}")

    # Display base URL and path separately
    base_url = get_current_base_url(st.session_state.current_env)
    path = api.get("path", "")
    url_path = api.get("url_path", "")

    st.write(f"Base URL: {base_url}")
    st.write(f"URL Path: {url_path}")  # Use the actual path that's stored in the API config
    st.write(f"Method: {api['method']}")

    # Option to edit the path
    new_path = st.text_input(
        "Edit Path", 
        value=path,
        help="Edit the API path (should start with a slash)"
    )

    if new_path != path:
        # Ensure path starts with a slash
        new_path = ensure_path_format(new_path)

        # Update path and URL
        api["path"] = new_path
        api["url"] = f"{base_url}{new_path}"
        st.success("Path updated!")
    elif not path and url_path:
        # If path is empty but url_path exists, use url_path
        path_to_use = ensure_path_format(url_path)

        # Update the URL using url_path
        api["url"] = f"{base_url}{path_to_use}"

    # Headers section
    _render_headers_section(api)

    # Parameters section (for GET requests)
    if api['method'] == "GET":
        _render_parameters_section(api)

    # Request Body (for POST, PUT, etc.)
    if api['method'] in ["POST", "PUT", "PATCH"]:
        _render_body_section(api)

    # Cookie options
    _render_cookies_section(api)

    # Action buttons
    _render_action_buttons(api_name, api, file_paths, is_temp)

    # Show response
    _render_response_section(api_name)


def show_history():
    """Display API call history in sidebar for current user"""
    if ('api_history' in st.session_state and st.session_state.api_history and 
        st.session_state.get('show_main_app', False)):
        st.sidebar.subheader(f"API History ({st.session_state.username})")

        # Create a dataframe for display
        history_df = pd.DataFrame([
            {
                "Time": entry["timestamp"],
                "API": entry["name"],
                "Method": entry["method"],
                "Path": entry.get("path", ""),
                "Status": entry["status_code"],
                "Env": entry["environment"]
            }
            for entry in st.session_state.api_history
        ])

        st.sidebar.dataframe(history_df, use_container_width=True)

        # Allow loading from history
        if st.sidebar.button("Load Selected API from History"):
            selected_index = st.sidebar.number_input(
                "Select history entry (0 is most recent)", 
                0, 
                len(st.session_state.api_history)-1 if st.session_state.api_history else 0,
                0
            )

            if st.session_state.api_history:
                entry = st.session_state.api_history[selected_index]
                api_name = f"{entry['name']} (from history)"

                # Get config from history
                config = entry['config'].copy()

                # Update URL based on current environment
                if "path" in config:
                    config["url"] = f"{get_current_base_url(st.session_state.current_env)}{config['path']}"

                st.session_state.apis[api_name] = config
                st.session_state.current_api = api_name

                # Save and update user data
                save_user_apis(st.session_state.apis, st.session_state.file_paths["USER_APIS_FILE"])
                _save_current_user_data()
                st.rerun()

        # Clear history option
        if st.sidebar.button("Clear History"):
            st.session_state.api_history = []
            if save_api_history([], st.session_state.file_paths["API_HISTORY_FILE"]):
                _save_current_user_data()
                st.sidebar.success("History cleared!")
            else:
                st.sidebar.error("Failed to clear history")
            st.rerun()


if __name__ == "__main__":
    st.set_page_config(
        page_title="API Tester",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Always show history for logged in users
    show_history()

    main()
