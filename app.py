"""
Smart Resume AI - Main Application (Fixed & Enhanced)
"""
import time
from PIL import Image
from jobs.job_search import render_job_search
from datetime import datetime
from ui_components import (
    apply_modern_styles, hero_section, feature_card, about_section,
    page_header, render_analytics_section, render_activity_section,
    render_suggestions_section, render_navigation_buttons
)
from feedback.feedback import FeedbackManager
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx import Document
import io
import base64
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
from dashboard.dashboard import DashboardManager
from config.courses import COURSES_BY_CATEGORY, RESUME_VIDEOS, INTERVIEW_VIDEOS, get_courses_for_role, get_category_for_role
from config.job_roles import JOB_ROLES
from config.database import (
    get_database_connection, save_resume_data, save_analysis_data,
    init_database, verify_admin, log_admin_action, save_ai_analysis_data,
    get_ai_analysis_stats, reset_ai_analysis_stats, get_detailed_ai_analysis_stats
)
from utils.ai_resume_analyzer import AIResumeAnalyzer
from utils.resume_builder import ResumeBuilder
from utils.resume_analyzer import ResumeAnalyzer
import traceback
import plotly.express as px
import pandas as pd
import json
import streamlit as st

# Set page config at the very beginning
st.set_page_config(
    page_title="Smart Resume AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


class ResumeApp:
    def __init__(self):
        """Initialize the application"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'personal_info': {
                    'full_name': '',
                    'email': '',
                    'phone': '',
                    'location': '',
                    'linkedin': '',
                    'portfolio': ''
                },
                'summary': '',
                'experiences': [],
                'education': [],
                'projects': [],
                'skills_categories': {
                    'technical': [],
                    'soft': [],
                    'languages': [],
                    'tools': []
                }
            }

        # Initialize navigation state
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
        if 'page_history' not in st.session_state:
            st.session_state.page_history = ['home']

        # Initialize admin state
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False

        self.pages = {
            "🏠 HOME": self.render_home,
            "🔍 RESUME ANALYZER": self.render_analyzer,
            "📝 RESUME BUILDER": self.render_builder,
            "📊 DASHBOARD": self.render_dashboard,
            "🎯 JOB SEARCH": self.render_job_search,
            "💬 FEEDBACK": self.render_feedback_page,
            "ℹ️ ABOUT": self.render_about
        }

        # Initialize dashboard manager
        self.dashboard_manager = DashboardManager()

        self.analyzer = ResumeAnalyzer()
        self.ai_analyzer = AIResumeAnalyzer()
        self.builder = ResumeBuilder()
        self.job_roles = JOB_ROLES

        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_user'
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None

        # Initialize database
        init_database()

        # Load external CSS
        with open('style/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

        # Load Google Fonts
        st.markdown("""
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """, unsafe_allow_html=True)

        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = []
        if 'ai_analysis_stats' not in st.session_state:
            st.session_state.ai_analysis_stats = {
                'score_distribution': {},
                'total_analyses': 0,
                'average_score': 0
            }

    def load_lottie_url(self, url: str):
        """Load Lottie animation from URL"""
        try:
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()
        except:
            return None

    def apply_global_styles(self):
        """Apply enhanced global styles"""
        st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');

        /* Root Variables */
        :root {
            --primary-color: #4CAF50;
            --primary-dark: #45a049;
            --secondary-color: #2196F3;
            --accent-color: #FF9800;
            --success-color: #4CAF50;
            --warning-color: #FFA500;
            --error-color: #FF4444;
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-tertiary: #2d2d2d;
            --text-primary: #ffffff;
            --text-secondary: #b3b3b3;
            --border-color: rgba(255,255,255,0.1);
            --shadow-sm: 0 2px 8px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.2);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.3);
            --shadow-xl: 0 16px 48px rgba(0,0,0,0.4);
        }

        /* Global Styles */
        * {
            font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif;
        }

        .main {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        }

        /* Enhanced Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, var(--primary-dark) 0%, #3d8b40 100%);
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }

        /* Enhanced Header */
        .main-header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 50%, #2196F3 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-xl);
            text-align: center;
            position: relative;
            overflow: hidden;
            animation: headerGlow 3s ease-in-out infinite alternate;
        }

        @keyframes headerGlow {
            0% { box-shadow: 0 10px 40px rgba(76, 175, 80, 0.3); }
            100% { box-shadow: 0 15px 60px rgba(76, 175, 80, 0.6); }
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }

        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .main-header h1 {
            color: white;
            font-size: 3rem;
            font-weight: 800;
            margin: 0;
            position: relative;
            z-index: 2;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            letter-spacing: -1px;
        }

        /* Enhanced Cards */
        .feature-card, .template-card {
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            border-radius: 20px;
            padding: 2.5rem;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-md);
        }

        .feature-card:hover, .template-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 60px rgba(76, 175, 80, 0.3);
            border-color: var(--primary-color);
        }

        .feature-card::before, .template-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, transparent 0%, rgba(76,175,80,0.1) 100%);
            z-index: 1;
            transition: opacity 0.4s ease;
            opacity: 0;
        }

        .feature-card:hover::before, .template-card:hover::before {
            opacity: 1;
        }

        .feature-icon, .template-icon {
            font-size: 3.5rem;
            color: var(--primary-color);
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
            display: inline-block;
            animation: iconFloat 3s ease-in-out infinite;
        }

        @keyframes iconFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .feature-title, .template-title {
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1rem;
            position: relative;
            z-index: 2;
            background: linear-gradient(135deg, #ffffff 0%, #b3b3b3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Enhanced Buttons */
        .stButton > button, .action-button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white !important;
            padding: 1rem 2.5rem;
            border-radius: 50px;
            border: none;
            font-weight: 600;
            font-size: 1.1rem;
            cursor: pointer;
            width: 100%;
            text-align: center;
            position: relative;
            overflow: hidden;
            z-index: 1;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stButton > button::before, .action-button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s ease, height 0.6s ease;
            z-index: -1;
        }

        .stButton > button:hover::before, .action-button:hover::before {
            width: 300px;
            height: 300px;
        }

        .stButton > button:hover, .action-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.5);
        }

        .stButton > button:active, .action-button:active {
            transform: translateY(-1px);
        }

        /* Enhanced Form Elements */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background: rgba(30, 30, 30, 0.95) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 1rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2) !important;
            background: rgba(40, 40, 40, 0.95) !important;
        }

        /* Enhanced Progress Indicators */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #4CAF50 0%, #45a049 50%, #2196F3 100%);
            border-radius: 10px;
        }

        /* Enhanced Metrics */
        .stMetric {
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
        }

        .stMetric:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-color);
        }

        /* Enhanced Expanders */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            padding: 1rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            border-color: var(--primary-color);
            background: linear-gradient(135deg, rgba(55, 55, 55, 0.95) 0%, rgba(40, 40, 40, 0.95) 100%);
        }

        /* Enhanced Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            border-radius: 12px;
            padding: 1rem 2rem;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            font-weight: 600;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, rgba(55, 55, 55, 0.95) 0%, rgba(40, 40, 40, 0.95) 100%);
            border-color: var(--primary-color);
            color: var(--text-primary);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%) !important;
            color: white !important;
            border-color: var(--primary-color) !important;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }

        /* Enhanced File Uploader */
        .stFileUploader {
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            border-radius: 15px;
            padding: 2rem;
            border: 2px dashed var(--border-color);
            transition: all 0.3s ease;
        }

        .stFileUploader:hover {
            border-color: var(--primary-color);
            background: linear-gradient(135deg, rgba(55, 55, 55, 0.95) 0%, rgba(40, 40, 40, 0.95) 100%);
        }

        /* Enhanced Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #0a0a0a 100%);
            border-right: 1px solid var(--border-color);
        }

        [data-testid="stSidebar"] .stButton > button {
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            border: 1px solid var(--border-color);
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            border-color: var(--primary-color);
        }

        /* Animation Classes */
        .animate-slide-in {
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-fade-in {
            animation: fadeIn 0.8s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Score Pills */
        .score-pill {
            display: inline-block;
            padding: 0.5rem 1.5rem;
            border-radius: 50px;
            font-weight: 700;
            text-align: center;
            box-shadow: var(--shadow-sm);
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .score-high {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }

        .score-medium {
            background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
            color: white;
        }

        .score-low {
            background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
            color: white;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem;
            }
            
            .feature-card, .template-card {
                padding: 1.5rem;
            }
            
            .stButton > button, .action-button {
                padding: 0.8rem 1.5rem;
                font-size: 1rem;
            }
        }

        /* Loading Spinner Enhancement */
        .stSpinner > div {
            border-color: var(--primary-color) transparent transparent transparent !important;
        }

        /* Toast Notifications */
        .stToast {
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            border: 1px solid var(--primary-color);
            border-radius: 12px;
            box-shadow: var(--shadow-lg);
        }

        /* Info/Warning/Error Boxes */
        .stAlert {
            border-radius: 12px;
            border: none;
            box-shadow: var(--shadow-md);
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    def add_footer(self):
        """Add an enhanced footer to all pages"""
        st.markdown("<hr style='margin-top: 50px; margin-bottom: 20px; border-color: var(--border-color);'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            # GitHub star button with enhanced styling
            st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; margin-bottom: 20px;'>
                <a href='https://github.com/SurinderTech' rel="noopener noreferrer" target='_blank' style='text-decoration: none;'>
                    <div style='
                        display: flex; 
                        align-items: center; 
                        background: linear-gradient(135deg, #24292e 0%, #1a1d23 100%);
                        padding: 12px 24px; 
                        border-radius: 50px; 
                        transition: all 0.3s ease;
                        border: 1px solid rgba(255,255,255,0.1);
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    '>
                        <svg height="20" width="20" viewBox="0 0 16 16" version="1.1" style='margin-right: 10px;'>
                            <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" fill="gold"></path>
                        </svg>
                        <span style='color: white; font-size: 16px; font-weight: 600;'>Star this repo</span>
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced footer text
            st.markdown("""
            <div style='text-align: center; color: var(--text-secondary);'>
                <p style='margin-bottom: 10px; font-size: 1rem;'>
                    Powered by <b style='color: #4CAF50;'>Streamlit</b> and <b style='color: #4285F4;'>Google Gemini AI</b>
                </p>
                <p style='margin-bottom: 10px;'>
                    Developed with ❤️ by 
                    <a href="https://www.linkedin.com/in/surinder-kumar-948343321" target="_blank" 
                       style='text-decoration: none; color: #4CAF50; font-weight: 600; transition: color 0.3s ease;'
                       onmouseover="this.style.color='#45a049'" 
                       onmouseout="this.style.color='#4CAF50'">
                        Surinder Kumar
                    </a>
                </p>
                <p style='font-size: 0.9rem; font-style: italic; color: var(--text-secondary);'>
                    "Every star counts! If you find this project helpful, please consider starring the repo."
                </p>
            </div>
            """, unsafe_allow_html=True)

    def render_empty_state(self, icon, message):
        """Render an enhanced empty state with icon and message"""
        return f"""
        <div style='
            text-align: center; 
            padding: 4rem 2rem; 
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.5) 0%, rgba(30, 30, 30, 0.5) 100%);
            border-radius: 20px;
            border: 2px dashed var(--border-color);
            margin: 2rem 0;
        '>
            <i class='{icon}' style='
                font-size: 4rem; 
                margin-bottom: 1.5rem; 
                color: var(--primary-color);
                animation: iconFloat 3s ease-in-out infinite;
            '></i>
            <p style='
                margin: 0; 
                font-size: 1.2rem; 
                color: var(--text-secondary);
                font-weight: 500;
            '>{message}</p>
        </div>
        """

    def render_dashboard(self):
        """Render the dashboard page"""
        self.dashboard_manager.render_dashboard()

    def render_builder(self):
        """Render the resume builder page with enhanced UI"""
        st.markdown("""
        <div class="main-header animate-fade-in">
            <h1><i class="fas fa-file-alt"></i> Resume Builder</h1>
            <p style='font-size: 1.2rem; margin-top: 1rem; color: rgba(255,255,255,0.9);'>
                Create your professional resume with our intelligent builder
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Template selection with enhanced UI
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1rem;'><i class="fas fa-palette"></i> Choose Your Template</h3>
        """, unsafe_allow_html=True)
        
        template_options = ["Modern", "Professional", "Minimal", "Creative"]
        selected_template = st.selectbox("Select Resume Template", template_options, label_visibility="collapsed")
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
            text-align: center;
            color: white;
            font-weight: 600;
        '>
            <i class="fas fa-check-circle"></i> Currently using: {selected_template} Template
        </div>
        </div>
        """, unsafe_allow_html=True)

        # Personal Information Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1.5rem;'>
                <i class="fas fa-user"></i> Personal Information
            </h3>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", value=st.session_state.form_data['personal_info']['full_name'], placeholder="John Doe")
            email = st.text_input("Email", value=st.session_state.form_data['personal_info']['email'], key="email_input", placeholder="john@example.com")
            phone = st.text_input("Phone", value=st.session_state.form_data['personal_info']['phone'], placeholder="+1 (555) 123-4567")

        with col2:
            location = st.text_input("Location", value=st.session_state.form_data['personal_info']['location'], placeholder="New York, NY")
            linkedin = st.text_input("LinkedIn URL", value=st.session_state.form_data['personal_info']['linkedin'], placeholder="linkedin.com/in/yourprofile")
            portfolio = st.text_input("Portfolio Website", value=st.session_state.form_data['personal_info']['portfolio'], placeholder="www.yourportfolio.com")

        # Update personal info in session state
        st.session_state.form_data['personal_info'] = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'portfolio': portfolio
        }

        st.markdown("</div>", unsafe_allow_html=True)

        # Professional Summary Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1.5rem;'>
                <i class="fas fa-align-left"></i> Professional Summary
            </h3>
        """, unsafe_allow_html=True)
        
        summary = st.text_area(
            "Professional Summary", 
            value=st.session_state.form_data.get('summary', ''), 
            height=150,
            placeholder="Write a compelling summary highlighting your key skills and experience...",
            label_visibility="collapsed"
        )
        st.session_state.form_data['summary'] = summary
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Experience Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1.5rem;'>
                <i class="fas fa-briefcase"></i> Work Experience
            </h3>
        """, unsafe_allow_html=True)
        
        if 'experiences' not in st.session_state.form_data:
            st.session_state.form_data['experiences'] = []

        if st.button("➕ Add Experience", use_container_width=True):
            st.session_state.form_data['experiences'].append({
                'company': '', 'position': '', 'start_date': '', 'end_date': '',
                'description': '', 'responsibilities': [], 'achievements': []
            })
            st.rerun()

        for idx, exp in enumerate(st.session_state.form_data['experiences']):
            with st.expander(f"Experience {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    exp['company'] = st.text_input("Company Name", key=f"company_{idx}", value=exp.get('company', ''))
                    exp['position'] = st.text_input("Position", key=f"position_{idx}", value=exp.get('position', ''))
                with col2:
                    exp['start_date'] = st.text_input("Start Date", key=f"start_date_{idx}", value=exp.get('start_date', ''))
                    exp['end_date'] = st.text_input("End Date", key=f"end_date_{idx}", value=exp.get('end_date', ''))

                exp['description'] = st.text_area("Role Overview", key=f"desc_{idx}", value=exp.get('description', ''))

                resp_text = st.text_area("Key Responsibilities (one per line)", key=f"resp_{idx}", 
                                        value='\n'.join(exp.get('responsibilities', [])), height=100)
                exp['responsibilities'] = [r.strip() for r in resp_text.split('\n') if r.strip()]

                achv_text = st.text_area("Key Achievements (one per line)", key=f"achv_{idx}",
                                        value='\n'.join(exp.get('achievements', [])), height=100)
                exp['achievements'] = [a.strip() for a in achv_text.split('\n') if a.strip()]

                if st.button("🗑️ Remove Experience", key=f"remove_exp_{idx}"):
                    st.session_state.form_data['experiences'].pop(idx)
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Education Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1.5rem;'>
                <i class="fas fa-graduation-cap"></i> Education
            </h3>
        """, unsafe_allow_html=True)
        
        if 'education' not in st.session_state.form_data:
            st.session_state.form_data['education'] = []

        if st.button("➕ Add Education", use_container_width=True):
            st.session_state.form_data['education'].append({
                'school': '', 'degree': '', 'field': '', 'graduation_date': '', 'gpa': '', 'achievements': []
            })
            st.rerun()

        for idx, edu in enumerate(st.session_state.form_data['education']):
            with st.expander(f"Education {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edu['school'] = st.text_input("School/University", key=f"school_{idx}", value=edu.get('school', ''))
                    edu['degree'] = st.text_input("Degree", key=f"degree_{idx}", value=edu.get('degree', ''))
                with col2:
                    edu['field'] = st.text_input("Field of Study", key=f"field_{idx}", value=edu.get('field', ''))
                    edu['graduation_date'] = st.text_input("Graduation Date", key=f"grad_date_{idx}", value=edu.get('graduation_date', ''))

                edu['gpa'] = st.text_input("GPA (optional)", key=f"gpa_{idx}", value=edu.get('gpa', ''))

                edu_achv_text = st.text_area("Achievements & Activities (one per line)", key=f"edu_achv_{idx}",
                                            value='\n'.join(edu.get('achievements', [])), height=100)
                edu['achievements'] = [a.strip() for a in edu_achv_text.split('\n') if a.strip()]

                if st.button("🗑️ Remove Education", key=f"remove_edu_{idx}"):
                    st.session_state.form_data['education'].pop(idx)
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Projects Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1.5rem;'>
                <i class="fas fa-project-diagram"></i> Projects
            </h3>
        """, unsafe_allow_html=True)
        
        if 'projects' not in st.session_state.form_data:
            st.session_state.form_data['projects'] = []

        if st.button("➕ Add Project", use_container_width=True):
            st.session_state.form_data['projects'].append({
                'name': '', 'technologies': '', 'description': '', 'responsibilities': [], 'achievements': [], 'link': ''
            })
            st.rerun()

        for idx, proj in enumerate(st.session_state.form_data['projects']):
            with st.expander(f"Project {idx + 1}", expanded=True):
                proj['name'] = st.text_input("Project Name", key=f"proj_name_{idx}", value=proj.get('name', ''))
                proj['technologies'] = st.text_input("Technologies Used", key=f"proj_tech_{idx}", value=proj.get('technologies', ''))
                proj['description'] = st.text_area("Project Overview", key=f"proj_desc_{idx}", value=proj.get('description', ''))

                proj_resp_text = st.text_area("Key Responsibilities (one per line)", key=f"proj_resp_{idx}",
                                            value='\n'.join(proj.get('responsibilities', [])), height=100)
                proj['responsibilities'] = [r.strip() for r in proj_resp_text.split('\n') if r.strip()]

                proj_achv_text = st.text_area("Key Achievements (one per line)", key=f"proj_achv_{idx}",
                                            value='\n'.join(proj.get('achievements', [])), height=100)
                proj['achievements'] = [a.strip() for a in proj_achv_text.split('\n') if a.strip()]

                proj['link'] = st.text_input("Project Link (optional)", key=f"proj_link_{idx}", value=proj.get('link', ''))

                if st.button("🗑️ Remove Project", key=f"remove_proj_{idx}"):
                    st.session_state.form_data['projects'].pop(idx)
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Skills Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1.5rem;'>
                <i class="fas fa-tools"></i> Skills
            </h3>
        """, unsafe_allow_html=True)

        if 'skills_categories' not in st.session_state.form_data:
            st.session_state.form_data['skills_categories'] = {
                'technical': [], 'soft': [], 'languages': [], 'tools': []
            }

        col1, col2 = st.columns(2)

        with col1:
            tech_skills = st.text_area(
                "Technical Skills (one per line)",
                value='\n'.join(st.session_state.form_data['skills_categories']['technical']),
                height=150,
                placeholder="Python, JavaScript, React..."
            )
            st.session_state.form_data['skills_categories']['technical'] = [s.strip() for s in tech_skills.split('\n') if s.strip()]

            soft_skills = st.text_area(
                "Soft Skills (one per line)",
                value='\n'.join(st.session_state.form_data['skills_categories']['soft']),
                height=150,
                placeholder="Leadership, Communication..."
            )
            st.session_state.form_data['skills_categories']['soft'] = [s.strip() for s in soft_skills.split('\n') if s.strip()]

        with col2:
            languages = st.text_area(
                "Languages (one per line)",
                value='\n'.join(st.session_state.form_data['skills_categories']['languages']),
                height=150,
                placeholder="English (Native), Spanish (Fluent)..."
            )
            st.session_state.form_data['skills_categories']['languages'] = [l.strip() for l in languages.split('\n') if l.strip()]

            tools = st.text_area(
                "Tools & Technologies (one per line)",
                value='\n'.join(st.session_state.form_data['skills_categories']['tools']),
                height=150,
                placeholder="Git, Docker, AWS..."
            )
            st.session_state.form_data['skills_categories']['tools'] = [t.strip() for t in tools.split('\n') if t.strip()]

        st.markdown("</div>", unsafe_allow_html=True)

        # Generate Resume Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Generate Resume", type="primary", use_container_width=True):
            current_name = st.session_state.form_data['personal_info']['full_name'].strip()
            current_email = st.session_state.get('email_input', '')

            if not current_name:
                st.error("⚠️ Please enter your full name.")
                return

            if not current_email:
                st.error("⚠️ Please enter your email address.")
                return

            st.session_state.form_data['personal_info']['email'] = current_email

            try:
                resume_data = {
                    "personal_info": st.session_state.form_data['personal_info'],
                    "summary": st.session_state.form_data.get('summary', '').strip(),
                    "experience": st.session_state.form_data.get('experiences', []),
                    "education": st.session_state.form_data.get('education', []),
                    "projects": st.session_state.form_data.get('projects', []),
                    "skills": st.session_state.form_data.get('skills_categories', {}),
                    "template": selected_template
                }

                resume_buffer = self.builder.generate_resume(resume_data)
                if resume_buffer:
                    try:
                        save_resume_data(resume_data)
                        st.success("✅ Resume generated successfully!")
                        st.snow()

                        st.download_button(
                            label="📥 Download Resume",
                            data=resume_buffer,
                            file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as db_error:
                        st.warning("⚠️ Resume generated but couldn't be saved to database")
                        st.download_button(
                            label="📥 Download Resume",
                            data=resume_buffer,
                            file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                else:
                    st.error("❌ Failed to generate resume. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    def render_about(self):
        """Render the about page with enhanced UI"""
        apply_modern_styles()

        # Hero Section
        st.markdown("""
        <div class="main-header animate-fade-in">
            <h1><i class="fas fa-info-circle"></i> About Smart Resume AI</h1>
            <p style='font-size: 1.2rem; margin-top: 1rem; color: rgba(255,255,255,0.9);'>
                Revolutionizing career advancement through AI-powered technology
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Profile Section - Split into separate components
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 3rem;
            border-radius: 20px;
            margin: 2rem auto;
            max-width: 900px;
            text-align: center;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-xl);
        '>
            <img src="https://raw.githubusercontent.com/SurinderTech/Mywebsite/main/Picsart_24-11-24_23-55-52-635.jpg"
                 alt="Surinder Kumar"
                 style='
                     width: 200px;
                     height: 200px;
                     border-radius: 50%;
                     margin: 0 auto 2rem;
                     display: block;
                     object-fit: cover;
                     border: 4px solid var(--primary-color);
                     box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
                 '>
            <h2 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>Surinder Kumar</h2>
            <p style='color: var(--primary-color); font-size: 1.3rem; margin-bottom: 2rem; font-weight: 600;'>
                Full Stack Developer & AI/ML Enthusiast
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Social Links Section - Using Streamlit columns
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        
        with col2:
            st.markdown("""
            <a href='https://github.com/SurinderTech' target='_blank'>
                <div style='
                    font-size: 2rem;
                    color: #4CAF50;
                    transition: all 0.3s ease;
                    padding: 1rem;
                    border-radius: 50%;
                    background: rgba(76, 175, 80, 0.1);
                    width: 70px;
                    height: 70px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-decoration: none;
                    margin: 0 auto;
                '>
                    <i class="fab fa-github"></i>
                </div>
            </a>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <a href='https://www.linkedin.com/in/surinder-kumar-948343321' target='_blank'>
                <div style='
                    font-size: 2rem;
                    color: #4CAF50;
                    transition: all 0.3s ease;
                    padding: 1rem;
                    border-radius: 50%;
                    background: rgba(76, 175, 80, 0.1);
                    width: 70px;
                    height: 70px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-decoration: none;
                    margin: 0 auto;
                '>
                    <i class="fab fa-linkedin"></i>
                </div>
            </a>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <a href='mailto:surinderkumar3182@gmail.com' target='_blank'>
                <div style='
                    font-size: 2rem;
                    color: #4CAF50;
                    transition: all 0.3s ease;
                    padding: 1rem;
                    border-radius: 50%;
                    background: rgba(76, 175, 80, 0.1);
                    width: 70px;
                    height: 70px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-decoration: none;
                    margin: 0 auto;
                '>
                    <i class="fas fa-envelope"></i>
                </div>
            </a>
            """, unsafe_allow_html=True)

        # Bio Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem auto;
            max-width: 900px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-xl);
        '>
            <p style='color: #b3b3b3; line-height: 1.8; font-size: 1.1rem; text-align: left;'>
                Hello! I'm a passionate Full Stack Developer with expertise in AI and Machine Learning.
                I created Smart Resume AI to revolutionize how job seekers approach their career journey.
                With my background in both software development and AI, I've designed this platform to
                provide intelligent, data-driven insights for resume optimization.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Vision Section
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 3rem;
            border-radius: 20px;
            margin: 2rem auto;
            max-width: 900px;
            text-align: center;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-xl);
        '>
            <i class="fas fa-lightbulb" style='font-size: 3rem; color: var(--primary-color); margin-bottom: 1rem; display: block;'></i>
            <h2 style='color: white; font-size: 2rem; margin-bottom: 1.5rem;'>Our Vision</h2>
            <p style='color: var(--text-secondary); line-height: 1.8; font-size: 1.1rem; font-style: italic;'>
                "Smart Resume AI represents my vision of democratizing career advancement through technology.
                By combining cutting-edge AI with intuitive design, this platform empowers job seekers at
                every career stage to showcase their true potential and stand out in today's competitive job market."
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Features Grid
        st.markdown("<h2 style='text-align: center; color: white; margin: 3rem 0 2rem 0;'>Platform Features</h2>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        features = [
            ("fas fa-robot", "AI-Powered Analysis", "Advanced AI algorithms provide detailed insights and suggestions to optimize your resume for maximum impact."),
            ("fas fa-chart-line", "Data-Driven Insights", "Make informed decisions with our analytics-based recommendations and industry insights."),
            ("fas fa-shield-alt", "Privacy First", "Your data security is our priority. We ensure your information is always protected and private.")
        ]
        
        for col, (icon, title, desc) in zip(cols, features):
            with col:
                st.markdown(f"""
                <div class='feature-card animate-slide-in'>
                    <i class='{icon}' style='font-size: 3rem; color: var(--primary-color); margin-bottom: 1rem; display: block;'></i>
                    <h3 style='color: white; font-size: 1.5rem; margin-bottom: 1rem;'>{title}</h3>
                    <p style='color: var(--text-secondary); line-height: 1.6;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

    def render_analyzer(self):
        """Render the resume analyzer page"""
        apply_modern_styles()

        # Page Header
        st.markdown("""
        <div class="main-header animate-fade-in">
            <h1><i class="fas fa-search"></i> Resume Analyzer</h1>
            <p style='font-size: 1.2rem; margin-top: 1rem; color: rgba(255,255,255,0.9);'>
                Get instant AI-powered feedback to optimize your resume
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Create tabs for analyzers
        analyzer_tabs = st.tabs(["📊 Standard Analyzer", "🤖 AI Analyzer"])

        with analyzer_tabs[0]:
            self.render_standard_analyzer()

        with analyzer_tabs[1]:
            self.render_ai_analyzer()

    def render_standard_analyzer(self):
        """Render standard analyzer content"""
        # Job Role Selection
        categories = list(self.job_roles.keys())
        selected_category = st.selectbox("Job Category", categories, key="standard_category")

        roles = list(self.job_roles[selected_category].keys())
        selected_role = st.selectbox("Specific Role", roles, key="standard_role")

        role_info = self.job_roles[selected_category][selected_role]

        # Display role information
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1.5rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white; margin-bottom: 1rem;'>{selected_role}</h3>
            <p style='color: var(--text-secondary); margin-bottom: 1rem;'>{role_info['description']}</p>
            <h4 style='color: var(--primary-color); margin-bottom: 0.5rem;'>Required Skills:</h4>
            <p style='color: var(--text-secondary);'>{', '.join(role_info['required_skills'])}</p>
        </div>
        """, unsafe_allow_html=True)

        # File Upload
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'], key="standard_file")

        if not uploaded_file:
            st.markdown(
                self.render_empty_state(
                    "fas fa-cloud-upload-alt",
                    "Upload your resume to get started with standard analysis"
                ),
                unsafe_allow_html=True
            )
        else:
            if st.button("🔍 Analyze My Resume", type="primary", use_container_width=True):
                with st.spinner("Analyzing your document..."):
                    try:
                        # Extract text
                        if uploaded_file.type == "application/pdf":
                            text = self.analyzer.extract_text_from_pdf(uploaded_file)
                        else:
                            text = self.analyzer.extract_text_from_docx(uploaded_file)

                        if not text or text.strip() == "":
                            st.error("Could not extract any text from the uploaded file.")
                            return

                        # Analyze
                        analysis = self.analyzer.analyze_resume({'raw_text': text}, role_info)

                        if 'error' in analysis:
                            st.error(analysis['error'])
                            return

                        st.snow()

                        # Display results
                        self.display_standard_analysis_results(analysis, selected_role, selected_category)

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    def display_standard_analysis_results(self, analysis, selected_role, selected_category):
        """Display standard analysis results"""
        col1, col2 = st.columns(2)

        with col1:
            # ATS Score Card
            st.markdown(f"""
            <div class='feature-card'>
                <h2 style='color: white; margin-bottom: 2rem;'>ATS Score</h2>
                <div style='position: relative; width: 150px; height: 150px; margin: 0 auto;'>
                    <div style='
                        position: absolute;
                        width: 150px;
                        height: 150px;
                        border-radius: 50%;
                        background: conic-gradient(
                            var(--primary-color) 0% {analysis['ats_score']}%,
                            var(--bg-tertiary) {analysis['ats_score']}% 100%
                        );
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    '>
                        <div style='
                            width: 120px;
                            height: 120px;
                            background: var(--bg-secondary);
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 2rem;
                            font-weight: bold;
                            color: var(--primary-color);
                        '>
                            {analysis['ats_score']}
                        </div>
                    </div>
                </div>
                <div style='text-align: center; margin-top: 1.5rem;'>
                    <span class='score-pill score-{"high" if analysis["ats_score"] >= 80 else "medium" if analysis["ats_score"] >= 60 else "low"}'>
                        {"Excellent" if analysis["ats_score"] >= 80 else "Good" if analysis["ats_score"] >= 60 else "Needs Improvement"}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Skills Match Card
            st.markdown(f"""
            <div class='feature-card'>
                <h2 style='color: white; margin-bottom: 1.5rem;'>Skills Match</h2>
                <div style='text-align: center; margin: 2rem 0;'>
                    <span style='font-size: 3rem; font-weight: bold; color: var(--primary-color);'>
                        {int(analysis.get('keyword_match', {}).get('score', 0))}%
                    </span>
                </div>
            """, unsafe_allow_html=True)

            if analysis['keyword_match']['missing_skills']:
                st.markdown("<h4 style='color: var(--primary-color);'>Missing Skills:</h4>", unsafe_allow_html=True)
                for skill in analysis['keyword_match']['missing_skills']:
                    st.markdown(f"<p style='color: var(--text-secondary);'>• {skill}</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    def render_ai_analyzer(self):
        """Render AI analyzer content"""
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1.5rem 0;
            border: 1px solid var(--border-color);
        '>
            <h3 style='color: white;'><i class="fas fa-robot"></i> AI-Powered Resume Analysis</h3>
            <p style='color: var(--text-secondary); margin-top: 1rem;'>
                Get detailed insights from advanced AI models that analyze your resume and provide personalized recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # AI Model Selection
        ai_model = st.selectbox("Select AI Model", ["Google Gemini"], help="Choose the AI model to analyze your resume")

        # Custom job description option
        use_custom_job_desc = st.checkbox("Use custom job description", value=False)
        custom_job_description = ""
        
        if use_custom_job_desc:
            custom_job_description = st.text_area(
                "Paste the job description here",
                height=200,
                placeholder="Paste the full job description from the company here..."
            )

        # Job Role Selection
        categories = list(self.job_roles.keys())
        selected_category = st.selectbox("Job Category", categories, key="ai_category")
        roles = list(self.job_roles[selected_category].keys())
        selected_role = st.selectbox("Specific Role", roles, key="ai_role")
        role_info = self.job_roles[selected_category][selected_role]

        # File Upload
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'], key="ai_file")

        if not uploaded_file:
            st.markdown(
                self.render_empty_state(
                    "fas fa-robot",
                    "Upload your resume to get AI-powered analysis"
                ),
                unsafe_allow_html=True
            )
        else:
            if st.button("🤖 Analyze with AI", type="primary", use_container_width=True):
                with st.spinner(f"Analyzing with {ai_model}..."):
                    try:
                        # Extract text
                        if uploaded_file.type == "application/pdf":
                            text = self.ai_analyzer.extract_text_from_pdf(uploaded_file)
                        else:
                            text = self.ai_analyzer.extract_text_from_docx(uploaded_file)

                        # Analyze with AI
                        if use_custom_job_desc and custom_job_description:
                            analysis_result = self.ai_analyzer.analyze_resume_with_gemini(
                                text, job_role=selected_role, job_description=custom_job_description
                            )
                        else:
                            analysis_result = self.ai_analyzer.analyze_resume_with_gemini(
                                text, job_role=selected_role
                            )

                        if analysis_result and "error" not in analysis_result:
                            # Save to database
                            save_ai_analysis_data(None, {
                                "model_used": ai_model,
                                "resume_score": analysis_result.get("resume_score", 0),
                                "job_role": selected_role
                            })

                            st.snow()
                            st.success("✅ Analysis complete!")

                            # Display results
                            self.display_ai_analysis_results(analysis_result, selected_role)
                        else:
                            st.error(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    def display_ai_analysis_results(self, analysis_result, job_role):
        """Display AI analysis results"""
        full_response = analysis_result.get("analysis", "")
        resume_score = analysis_result.get("resume_score", 0)
        ats_score = analysis_result.get("ats_score", 0)

        # Score gauges
        col1, col2 = st.columns(2)

        with col1:
            fig1 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=resume_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Resume Score", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#4CAF50" if resume_score >= 80 else "#FFA500" if resume_score >= 60 else "#FF4444"},
                    'steps': [
                        {'range': [0, 60], 'color': 'rgba(255, 68, 68, 0.2)'},
                        {'range': [60, 80], 'color': 'rgba(255, 165, 0, 0.2)'},
                        {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                    ]
                }
            ))
            fig1.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ats_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "ATS Score", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#4CAF50" if ats_score >= 80 else "#FFA500" if ats_score >= 60 else "#FF4444"},
                    'steps': [
                        {'range': [0, 60], 'color': 'rgba(255, 68, 68, 0.2)'},
                        {'range': [60, 80], 'color': 'rgba(255, 165, 0, 0.2)'},
                        {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                    ]
                }
            ))
            fig2.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig2, use_container_width=True)

        # Full analysis report
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(30, 30, 30, 0.95) 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        '>
            <h2 style='color: white;'><i class="fas fa-file-alt"></i> Full Analysis Report</h2>
        """, unsafe_allow_html=True)

        st.markdown(f"<div style='color: var(--text-secondary); line-height: 1.8;'>{full_response}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # PDF Download
        pdf_buffer = self.ai_analyzer.generate_pdf_report(
            analysis_result={"score": resume_score, "ats_score": ats_score, "full_response": full_response},
            candidate_name="Candidate",
            job_role=job_role
        )

        if pdf_buffer:
            st.download_button(
                label="📊 Download PDF Report",
                data=pdf_buffer,
                file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    def render_home(self):
        """Render the home page with enhanced UI"""
        apply_modern_styles()

        # Hero Section
        st.markdown("""
        <div class="main-header animate-fade-in">
            <h1 class="hero-title"><i class="fas fa-rocket"></i> Welcome to Smart Resume AI</h1>
            <p style='font-size: 1.3rem; margin-top: 1rem; color: rgba(255,255,255,0.9); font-weight: 500;'>
                Your personal AI-powered resume assistant for career success
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Info message
        st.info("🎉 Welcome to the Smart AI Resume Analyzer!")

        # Features Section
        st.markdown("""
        <h2 style='
            text-align: center; 
            color: white; 
            font-size: 2.5rem; 
            margin: 3rem 0 2rem 0;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        '>
            <i class="fas fa-star"></i> Key Features
        </h2>
        """, unsafe_allow_html=True)

        cols = st.columns(3)

        features = [
            ("fas fa-robot", "AI-Powered Analysis", "Get in-depth analysis of your resume with AI-driven suggestions to improve your chances of getting hired."),
            ("fas fa-file-alt", "Resume Builder", "Create a professional resume from scratch with our easy-to-use builder and customizable templates."),
            ("fas fa-chart-line", "Performance Tracking", "Track your resume's performance with our analytics dashboard and get insights to optimize your job search.")
        ]

        for col, (icon, title, desc) in zip(cols, features):
            with col:
                st.markdown(f"""
                <div class='feature-card animate-slide-in'>
                    <i class='{icon} feature-icon'></i>
                    <h3 class='feature-title'>{title}</h3>
                    <p style='color: var(--text-secondary); line-height: 1.6;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

        # Call to Action
        st.markdown("""
        <div style='text-align: center; margin: 4rem 0;'>
            <a href='?page=analyzer' style='text-decoration: none;'>
                <button class='action-button' style='
                    font-size: 1.2rem;
                    padding: 1.5rem 3rem;
                    cursor: pointer;
                    border: none;
                    display: inline-block;
                '>
                    Get Started Now <i class="fas fa-arrow-right" style="margin-left: 10px;"></i>
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    def render_job_search(self):
        """Render the job search page"""
        render_job_search()

    def render_feedback_page(self):
        """Render the feedback page"""
        apply_modern_styles()

        st.markdown("""
        <div class="main-header animate-fade-in">
            <h1><i class="fas fa-comments"></i> Feedback & Suggestions</h1>
            <p style='font-size: 1.2rem; margin-top: 1rem; color: rgba(255,255,255,0.9);'>
                Help us improve by sharing your thoughts
            </p>
        </div>
        """, unsafe_allow_html=True)

        feedback_manager = FeedbackManager()

        form_tab, stats_tab = st.tabs(["📝 Submit Feedback", "📊 Feedback Stats"])

        with form_tab:
            feedback_manager.render_feedback_form()

        with stats_tab:
            feedback_manager.render_feedback_stats()

    def main(self):
        """Main application entry point"""
        self.apply_global_styles()

        # Sidebar
        with st.sidebar:
            lottie_anim = self.load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_xyadoh9h.json")
            if lottie_anim:
                st_lottie(lottie_anim, height=200, key="sidebar_animation")

            st.markdown("""
            <h1 style='
                text-align: center; 
                color: white; 
                font-size: 1.8rem;
                margin: 1rem 0;
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            '>
                Smart Resume AI
            </h1>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Navigation buttons
            for page_name in self.pages.keys():
                if st.button(page_name, use_container_width=True):
                    cleaned_name = page_name.lower().replace(" ", "_")
                    for emoji in ["🏠", "🔍", "📝", "📊", "🎯", "💬", "ℹ️"]:
                        cleaned_name = cleaned_name.replace(emoji, "").strip()
                    if cleaned_name != st.session_state.page:
                        st.session_state.page = cleaned_name
                        st.session_state.page_history.append(cleaned_name)
                        st.rerun()

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")

        # Force home page on first load
        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
            st.session_state.page = 'home'
            st.rerun()

        # Render navigation buttons
        render_navigation_buttons()

        # Get current page
        current_page = st.session_state.get('page', 'home')

        # Page mapping
        page_mapping = {
            name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "")
            .replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").strip(): name
            for name in self.pages.keys()
        }

        # Render page
        if current_page in page_mapping:
            self.pages[page_mapping[current_page]]()
        else:
            self.render_home()

        # Add footer
        self.add_footer()


if __name__ == "__main__":
    app = ResumeApp()
    app.main()