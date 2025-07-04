import streamlit as st
import requests
import json
import pandas as pd
from PIL import Image
from io import BytesIO
import time
import datetime

# Set page config
st.set_page_config(
    page_title=" Result Portal",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 30px;
    }
    .info-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .grade-s {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .grade-a {
        background-color: #cce5ff;
        color: #004085;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .grade-pa {
        background-color: #fff3cd;
        color: #856404;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session' not in st.session_state:
    st.session_state.session = requests.Session()
if 'result_data' not in st.session_state:
    st.session_state.result_data = None
if 'captcha_image' not in st.session_state:
    st.session_state.captcha_image = None
if 'captcha_loaded' not in st.session_state:
    st.session_state.captcha_loaded = False

def initialize_session():
    """Initialize session and get homepage"""
    try:
        # Create a fresh session with proper headers
        st.session_state.session = requests.Session()
        st.session_state.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Visit the homepage first
        homepage_response = st.session_state.session.get("https://resultcrescent.mastersofterp.in")
        if homepage_response.status_code == 200:
            st.success("✅ Session initialized successfully")
            return True
        else:
            st.error(f"Failed to initialize session: {homepage_response.status_code}")
            return False
    except Exception as e:
        st.error(f"Failed to initialize session: {e}")
        return False

def get_captcha_image():
    """Download and return CAPTCHA image"""
    try:
        captcha_url = "https://resultcrescent.mastersofterp.in/Result/ShowCaptchaImage"
        captcha_response = st.session_state.session.get(captcha_url)
        
        if captcha_response.status_code == 200:
            img = Image.open(BytesIO(captcha_response.content))
            st.session_state.captcha_image = img
            st.session_state.captcha_loaded = True
            return img
        else:
            st.error(f"Failed to load CAPTCHA: HTTP {captcha_response.status_code}")
            return None
    except Exception as e:
        st.error(f"Failed to load CAPTCHA: {e}")
        return None

def fetch_student_data(registration_number, dob, captcha):
    """Fetch student info and results"""
    try:
        info_url = "https://resultcrescent.mastersofterp.in/Result/GetStudentInfo/"
        result_url = "https://resultcrescent.mastersofterp.in/Result/GetResult/"
        
        payload = {
            "RegistrationNo": registration_number,
            "DOB": dob,
            "CaptchaText": captcha
        }

        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://resultcrescent.mastersofterp.in",
            "referer": "https://resultcrescent.mastersofterp.in/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

        # Debug: Show what we're sending
        st.info(f"Sending payload: {payload}")
        
        combined_data = {}
        
        # First, get student info
        info_response = st.session_state.session.post(info_url, headers=headers, data=payload)
        
        if info_response.status_code == 200:
            try:
                info_data = info_response.json()
                if info_data and info_data.get('StudentName'):
                    combined_data["Info"] = info_data
                    st.success("✅ Student info fetched successfully")
                    
                    # Small delay before fetching results
                    time.sleep(0.5)
                    
                    # Now fetch results using the same session
                    result_response = st.session_state.session.post(result_url, headers=headers, data=payload)
                    
                    if result_response.status_code == 200:
                        try:
                            result_data = result_response.json()
                            st.info(f"Result response received: {result_data}")
                            
                            if result_data and "Res" in result_data and result_data["Res"]:
                                combined_data["Res"] = result_data["Res"]
                                st.success("✅ Results fetched successfully")
                            else:
                                st.warning("⚠️ Results response is empty or null")
                                st.info("This might mean:")
                                st.info("- Results haven't been published yet")
                                st.info("- There's a delay between info and results publication")
                                combined_data["Res"] = None
                                
                        except Exception as e:
                            st.error(f"Could not decode Result JSON: {e}")
                            st.error(f"Raw Result response: {result_response.text}")
                            combined_data["Res"] = None
                    else:
                        st.error(f"❌ Result request failed with status: {result_response.status_code}")
                        st.error(f"Result response text: {result_response.text}")
                        combined_data["Res"] = None
                        
                else:
                    st.error("❌ Invalid student info response or wrong credentials")
                    st.error(f"Info response: {info_data}")
                    return None
                    
            except Exception as e:
                st.error(f"Could not decode Info JSON: {e}")
                st.error(f"Raw Info response: {info_response.text}")
                return None
        else:
            st.error(f"❌ Info request failed with status: {info_response.status_code}")
            st.error(f"Info response text: {info_response.text}")
            return None

        return combined_data
        
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def display_student_info(info_data):
    """Display student information in a formatted card"""
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Student Information**")
        st.write(f"**Name:** {info_data.get('StudentName', 'N/A')}")
        st.write(f"**Registration No:** {info_data.get('RegistrationNo', 'N/A')}")
        st.write(f"**Date of Birth:** {info_data.get('DOB', 'N/A')}")
        
    with col2:
        st.markdown("**Academic Details**")
        st.write(f"**Degree:** {info_data.get('Degree', 'N/A')}")
        st.write(f"**Branch:** {info_data.get('Branch', 'N/A')}")
        st.write(f"**Semester:** {info_data.get('Semester', 'N/A')}")
        st.write(f"**Session:** {info_data.get('Sessionno', 'N/A')}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display SGPA and Result prominently
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("SGPA", info_data.get('SGPA', 'N/A'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        result_status = info_data.get('Result', 'N/A')
        st.metric("Result", result_status)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Publish Date", info_data.get('PubDate', 'N/A').split(' ')[0])
        st.markdown('</div>', unsafe_allow_html=True)

def display_results_table(results_data):
    """Display results in a formatted table"""
    if not results_data:
        st.warning("No results data available")
        return
    
    # Create DataFrame
    df = pd.DataFrame(results_data)
    
    # Select and rename columns for display
    display_columns = {
        'COURSENAME': 'Course Name',
        'GRADE': 'Grade',
        'INTERMARK': 'Internal-Marks',
        'EXTERMARK': 'External-Marks',
        'MARKTOT': 'Total-Marks',
        'CREDITS': 'Credits',
        'GDPOINT': 'Grade Points',
        'COURSETYPE': 'Course Type'
    }
    
    display_df = df[display_columns.keys()].copy()
    display_df = display_df.rename(columns=display_columns)
    
    # Format numeric columns
    numeric_columns = ['Internal', 'External', 'Total', 'Credits', 'Grade Points']
    for col in numeric_columns:
        if col in display_df.columns:
            display_df[col] = pd.to_numeric(display_df[col], errors='coerce')
    
    # Display table with custom styling
    st.markdown("### 📊 Detailed Results")
    
    # Add grade color coding
    def color_grades(val):
        if val == 'S':
            return 'background-color: #d4edda; color: #155724; font-weight: bold'
        elif val == 'A':
            return 'background-color: #cce5ff; color: #004085; font-weight: bold'
        elif val == 'PA':
            return 'background-color: #fff3cd; color: #856404; font-weight: bold'
        else:
            return ''
    
    styled_df = display_df.style.applymap(color_grades, subset=['Grade'])
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Summary statistics
    st.markdown("### 📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_subjects = len(display_df)
        st.metric("Total Subjects", total_subjects)
    
    with col2:
        s_grades = len(display_df[display_df['Grade'] == 'S'])
        st.metric("S Grades", s_grades)
    
    with col3:
        a_grades = len(display_df[display_df['Grade'] == 'A'])
        st.metric("A Grades", a_grades)
    
    with col4:
        total_credits = display_df['Credits'].sum()
        st.metric("Total Credits", total_credits)

def create_download_data(data):
    """Create downloadable JSON data"""
    return json.dumps(data, indent=2)

# Main App
def main():

    #disclaimer Popup
    if 'disclaimer_accepted' not in st.session_state:
        st.session_state.disclaimer_accepted = False

    if not st.session_state.disclaimer_accepted:
        with st.container():
            st.warning("⚠️DISCLAIMER:  This tool is independently developed and is not affiliated with any Crescent institution.")
            st.markdown("""
                <div style='font-size: 16px; color: #999999;'>
                    <ul>
                        <strong><li>This tool is for educational use only.</li>
                        <li>No data is stored — everything is fetched in real-time.</li>
                        <li>Use at your own risk.</li>
                        <li>Not affiliated with Crescent university or its result portal.</li></strong>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            if st.button("✅ I Understand", use_container_width=True):
                st.session_state.disclaimer_accepted = True
                st.rerun()
        return  # Stop further execution until accepted

    st.markdown('<h1 class="main-header">🎓 Student Result Portal</h1>', unsafe_allow_html=True)
    
    # Initialize session only once
    if not st.session_state.get('session_initialized', False):
        if initialize_session():
            st.session_state.session_initialized = True
        else:
            st.error("Failed to initialize connection. Please refresh the page.")
            return
    
    # Load CAPTCHA only if not already loaded
    if not st.session_state.captcha_loaded:
        st.info("Loading CAPTCHA...")
        get_captcha_image()
    
    # Create form
    with st.form("result_form"):
        st.markdown("### 📝 Enter Your Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            registration_number = st.text_input("Registration Number", placeholder="e.g., 230201601069")
            dob = st.date_input("Date of Birth", min_value=datetime.date(1990, 1, 1), max_value=None,format="DD/MM/YYYY")
        
        with col2:
            # Display CAPTCHA
            st.markdown("**CAPTCHA Image:**")
            if st.session_state.captcha_image:
                st.image(st.session_state.captcha_image, width=200)
            else:
                st.error("Could not load CAPTCHA image")
            
            captcha = st.text_input("Enter CAPTCHA", placeholder="Enter the text from image")
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            refresh_captcha = st.form_submit_button("🔄 Refresh CAPTCHA", use_container_width=True)
        with col2:
            submitted = st.form_submit_button("🔍 Get Results", use_container_width=True, type="primary")
        
        # Handle form submissions
        if refresh_captcha:
            st.session_state.captcha_loaded = False
            st.session_state.captcha_image = None
            # Reinitialize session for fresh captcha
            initialize_session()
            st.rerun()
        
        if submitted:
            if not all([registration_number, dob, captcha]):
                st.error("Please fill in all fields")
            else:
                with st.spinner("Fetching results..."):
                    dob_formatted = dob.strftime("%d/%m/%Y")
                    result_data = fetch_student_data(registration_number, dob_formatted, captcha)
                    
                    if result_data:
                        st.session_state.result_data = result_data
                        st.success("Results fetched successfully!")
                        # Reset captcha after successful submission
                        st.session_state.captcha_loaded = False
                        st.session_state.captcha_image = None
                        st.rerun()
                    else:
                        st.error("Failed to fetch results. Please check your details and try again.")
                        # Reset captcha on failure
                        st.session_state.captcha_loaded = False
                        st.session_state.captcha_image = None
                        st.rerun()
    
    # Display results if available
    if st.session_state.result_data:
        st.markdown("---")
        
        # Display student info
        if "Info" in st.session_state.result_data:
            display_student_info(st.session_state.result_data["Info"])
        
        # Display results table
        if "Res" in st.session_state.result_data and st.session_state.result_data["Res"]:
            display_results_table(st.session_state.result_data["Res"])
        else:
            st.warning("📋 No detailed results available")
            st.info("• Try refreshing the page and fetching again")
        
        # Download button (show even if Res is null)
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            download_data = create_download_data(st.session_state.result_data)
            st.download_button(
                label="📥 Download Raw Data (JSON)",
                data=download_data,
                file_name=f"result_{st.session_state.result_data['Info']['RegistrationNo']}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Clear results button
        with col3:
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.result_data = None
                st.session_state.captcha_loaded = False
                st.session_state.captcha_image = None
                st.rerun()

if __name__ == "__main__":
    main()


# Footer
# Disclaimer section
st.markdown("""
    <hr style="margin-top: 50px; margin-bottom: 10px;">
    <div style='text-align: center; color: #999999; font-size: 14px;'>
        ⚠️ <strong>Disclaimer:</strong> This tool is independently developed for educational purposes.<br>
        It is <strong>not affiliated</strong> with or endorsed by Crescent university or result portal.<br>
        All data is fetched in real-time based on user input and <strong>is not stored</strong> and the Code is <strong>OPEN SOURCED</strong><br>
        <strong>Use at your own risk.</strong>
    </div>
""", unsafe_allow_html=True)


st.markdown("""
    <hr style="margin-top: 50px; margin-bottom: 10px;">
    <div style='text-align: center; color: gray; font-size: 16px;'>
        For Bugs and Legal issues contact : <strong>vishnuprasad25020@gmail.com</strong>
    </div>
""", unsafe_allow_html=True)
