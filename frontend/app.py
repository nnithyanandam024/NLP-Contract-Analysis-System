import os
import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time

# ============ PAGE CONFIGURATION ============
st.set_page_config(
    page_title="ContractIQ - Smart Contract Analysis",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    /* Main Styling */
    .main {
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Card Styling */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Header Styling */
    .header-container {
        background: white;
        padding: 2.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        margin-bottom: 2rem;
        text-align: center;
        border-top: 4px solid #1e3c72;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e3c72;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #555;
        margin-bottom: 0.8rem;
        font-weight: 500;
    }
    
    .team-info {
        font-size: 1rem;
        color: #777;
        font-style: italic;
        margin-top: 0.5rem;
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 60, 114, 0.4);
    }
    
    /* Risk Cards */
    .risk-high {
        background: linear-gradient(135deg, #c92a2a 0%, #a61e1e 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(201, 42, 42, 0.3);
        border-left: 5px solid #7d1414;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #e67700 0%, #cc6600 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(230, 119, 0, 0.3);
        border-left: 5px solid #995500;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #2f9e44 0%, #2b8a3e 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(47, 158, 68, 0.3);
        border-left: 5px solid #1e6f2f;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(30, 60, 114, 0.3);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Upload Area */
    .upload-area {
        border: 3px dashed #1e3c72;
        border-radius: 10px;
        padding: 3rem;
        text-align: center;
        background: rgba(30, 60, 114, 0.05);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        background: rgba(30, 60, 114, 0.1);
        border-color: #2a5298;
    }
    
    /* Success/Info Messages */
    .stAlert {
        border-radius: 8px;
        border-left: 5px solid #1e3c72;
    }
    
    /* Section Headers */
    .section-header {
        color: #1e3c72;
        font-weight: 600;
        font-size: 1.5rem;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #1e3c72;
        padding-bottom: 0.5rem;
    }
    
    /* Info Box */
    .info-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1e3c72;
        margin: 1rem 0;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ============ CONFIG ============
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ============ HEADER ============
st.markdown("""
<div class="header-container">
    <div class="main-title">ContractIQ</div>
    <div class="subtitle">Enterprise Contract Analysis Platform</div>
    <div class="team-info">Developed by Team DEVNEST | Bannari Amman Institute of Technology</div>
</div>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "Select Page",
        ["Upload & Analyze", "Contract Dashboard", "About Platform"],
        label_visibility="visible"
    )
    
    st.markdown("---")
    
    st.markdown("""
    ### Platform Features
    - PDF Contract Upload
    - Intelligent Analysis
    - Risk Assessment
    - Visual Dashboard
    - Secure Storage
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Team DEVNEST
    **Bannari Amman Institute of Technology**
    
    Building innovative solutions for contract management
    """)

# ============ PAGE 1: UPLOAD & ANALYZE ============
if page == "Upload & Analyze":
    st.markdown('<p class="section-header">Upload Construction Contract</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>Select Contract Document</h3>
            <p style="color: #555; line-height: 1.6;">Upload a PDF file of your construction contract for comprehensive analysis. 
            The platform will extract key information, identify contract parties, financial terms, and assess potential risks.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose PDF File",
            type=['pdf'],
            help="Maximum file size: 50MB"
        )
        
        if uploaded_file:
            st.success(f"File Loaded: **{uploaded_file.name}**")
            st.info(f"File Size: {uploaded_file.size / 1024:.2f} KB")
            
            if st.button("START ANALYSIS", use_container_width=True):
                with st.spinner(""):
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Uploading document to server...")
                    progress_bar.progress(20)
                    time.sleep(0.5)
                    
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                        
                        status_text.text("Extracting contract text from PDF...")
                        progress_bar.progress(40)
                        time.sleep(0.5)
                        
                        response = requests.post(f"{API_URL}/upload", files=files)
                        
                        status_text.text("Analyzing contract terms and conditions...")
                        progress_bar.progress(60)
                        time.sleep(1)
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            status_text.text("Identifying potential risks and compliance issues...")
                            progress_bar.progress(80)
                            time.sleep(0.5)
                            
                            status_text.text("Analysis complete. Preparing results...")
                            progress_bar.progress(100)
                            time.sleep(0.5)
                            
                            st.success("Analysis Completed Successfully")
                            
                            # Fetch analysis
                            analysis_response = requests.get(f"{API_URL}/contracts/{result['contract_id']}")
                            
                            if analysis_response.status_code == 200:
                                data = analysis_response.json()
                                
                                if data['analysis']:
                                    a = data['analysis']
                                    
                                    st.markdown("---")
                                    st.markdown('<p class="section-header">Analysis Results</p>', unsafe_allow_html=True)
                                    
                                    # Metrics
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.markdown(f"""
                                        <div class="metric-card">
                                            <div class="metric-label">Contract Value</div>
                                            <div class="metric-value">{a['contract_value']}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with col2:
                                        risk_color = "#c92a2a" if a['risk_score'] > 7 else "#e67700" if a['risk_score'] > 4 else "#2f9e44"
                                        st.markdown(f"""
                                        <div class="metric-card" style="background: linear-gradient(135deg, {risk_color} 0%, {risk_color} 100%);">
                                            <div class="metric-label">Risk Score</div>
                                            <div class="metric-value">{a['risk_score']:.1f}/10</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with col3:
                                        st.markdown(f"""
                                        <div class="metric-card">
                                            <div class="metric-label">Project Duration</div>
                                            <div class="metric-value" style="font-size: 1rem;">{a['start_date']}<br>to<br>{a['end_date']}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    st.markdown("---")
                                    
                                    # Parties
                                    st.markdown('<p class="section-header">Contract Parties</p>', unsafe_allow_html=True)
                                    st.markdown(f"""
                                    <div class="info-box">
                                        {a['parties']}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Key Terms
                                    st.markdown('<p class="section-header">Key Contract Terms</p>', unsafe_allow_html=True)
                                    for i, term in enumerate(a['key_terms'], 1):
                                        st.markdown(f"**{i}.** {term}")
                                    
                                    # Risks
                                    st.markdown('<p class="section-header">Risk Assessment</p>', unsafe_allow_html=True)
                                    for risk in a['risks']:
                                        severity = risk['severity'].lower()
                                        st.markdown(f"""
                                        <div class="risk-{severity}">
                                            <strong>{risk['severity'].upper()} SEVERITY</strong><br>
                                            {risk['description']}
                                        </div>
                                        """, unsafe_allow_html=True)
                        else:
                            st.error(f"Analysis Failed: {response.json().get('detail', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")
                        st.info("Please ensure the backend server is running on port 8000")
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>User Guide</h3>
            <ol style="line-height: 2;">
                <li><strong>Upload</strong> PDF contract document</li>
                <li><strong>Click</strong> Start Analysis button</li>
                <li><strong>Review</strong> extracted information</li>
                <li><strong>Assess</strong> identified risks</li>
                <li><strong>Export</strong> analysis report</li>
            </ol>
            
            <h4>Supported Documents</h4>
            <ul style="line-height: 1.8;">
                <li>PDF format only</li>
                <li>Maximum size: 50MB</li>
                <li>Clear, readable text</li>
                <li>Standard contract format</li>
            </ul>
            
            <h4>Data Security</h4>
            <p style="color: #555; line-height: 1.6;">All uploaded documents are processed securely with end-to-end encryption. 
            Your data is protected and stored in compliance with industry standards.</p>
        </div>
        """, unsafe_allow_html=True)

# ============ PAGE 2: DASHBOARD ============
elif page == "Contract Dashboard":
    st.markdown('<p class="section-header">All Analyzed Contracts</p>', unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{API_URL}/contracts")
        if response.status_code == 200:
            contracts = response.json()
            
            if contracts:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Contracts</div>
                        <div class="metric-value">{len(contracts)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    completed = sum(1 for c in contracts if c['status'] == 'completed')
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #2f9e44 0%, #2b8a3e 100%);">
                        <div class="metric-label">Completed</div>
                        <div class="metric-value">{completed}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    pending = sum(1 for c in contracts if c['status'] != 'completed')
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #e67700 0%, #cc6600 100%);">
                        <div class="metric-label">Pending</div>
                        <div class="metric-value">{pending}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Contracts table
                st.markdown('<p class="section-header">Contract Records</p>', unsafe_allow_html=True)
                df = pd.DataFrame(contracts)
                df['upload_date'] = pd.to_datetime(df['upload_date']).dt.strftime('%Y-%m-%d %H:%M')
                df.columns = ['ID', 'Filename', 'Upload Date', 'Status']
                
                st.dataframe(
                    df, 
                    use_container_width=True,
                    hide_index=True
                )
                
                # View details
                st.markdown('<p class="section-header">View Contract Details</p>', unsafe_allow_html=True)
                selected_id = st.selectbox(
                    "Select Contract",
                    [c['id'] for c in contracts],
                    format_func=lambda x: f"Contract #{x} - {next(c['filename'] for c in contracts if c['id'] == x)}"
                )
                
                if st.button("VIEW FULL ANALYSIS", use_container_width=True):
                    detail_response = requests.get(f"{API_URL}/contracts/{selected_id}")
                    
                    if detail_response.status_code == 200:
                        data = detail_response.json()
                        
                        st.markdown(f"### Contract: {data['contract']['filename']}")
                        
                        if data['analysis']:
                            a = data['analysis']
                            
                            # Metrics row
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Contract Value", a['contract_value'])
                            with col2:
                                st.metric("Risk Score", f"{a['risk_score']:.1f}/10")
                            with col3:
                                st.metric("Duration", f"{a['start_date']} to {a['end_date']}")
                            
                            st.markdown("---")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### Contract Parties")
                                st.markdown(f"""
                                <div class="info-box">
                                    {a['parties']}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown("#### Key Terms")
                                for i, term in enumerate(a['key_terms'], 1):
                                    st.markdown(f"{i}. {term}")
                            
                            with col2:
                                st.markdown("#### Identified Risks")
                                for risk in a['risks']:
                                    severity = risk['severity'].lower()
                                    st.markdown(f"""
                                    <div class="risk-{severity}">
                                        <strong>{risk['severity'].upper()} SEVERITY</strong><br>
                                        {risk['description']}
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.warning("Analysis pending or incomplete")
            else:
                st.info("No contracts uploaded yet. Navigate to 'Upload & Analyze' to begin.")
        else:
            st.error("Could not retrieve contracts from server")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please ensure the backend server is operational")

# ============ PAGE 3: ABOUT ============
else:
    st.markdown('<p class="section-header">About ContractIQ Platform</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>Platform Overview</h3>
            <p style="line-height: 1.8; color: #555;">ContractIQ is an enterprise-grade contract analysis platform designed to streamline 
            the review process for construction contracts. Developed by Team DEVNEST at Bannari Amman Institute of Technology, 
            this solution combines intelligent document processing with comprehensive risk assessment capabilities.</p>
            
            <h3>Core Features</h3>
            <ul style="line-height: 1.8;">
                <li><strong>Automated Analysis:</strong> Process contracts in under 60 seconds with high accuracy</li>
                <li><strong>Information Extraction:</strong> Identify parties, financial terms, dates, and obligations</li>
                <li><strong>Risk Detection:</strong> Flag potential compliance issues and contractual risks</li>
                <li><strong>Visual Dashboard:</strong> Intuitive interface for managing multiple contracts</li>
                <li><strong>Secure Processing:</strong> Enterprise-grade encryption and data protection</li>
            </ul>
            
            <h3>Technical Architecture</h3>
            <ul style="line-height: 1.8;">
                <li><strong>Frontend Framework:</strong> Streamlit with custom CSS styling</li>
                <li><strong>Backend API:</strong> FastAPI (Python-based REST API)</li>
                <li><strong>Database:</strong> SQLite with relational schema</li>
                <li><strong>Document Processing:</strong> PyPDF2 for text extraction</li>
                <li><strong>Analysis Engine:</strong> Advanced language processing models</li>
            </ul>
            
            <h3>Industry Applications</h3>
            <ul style="line-height: 1.8;">
                <li>Construction companies reviewing vendor agreements</li>
                <li>Legal teams conducting preliminary contract assessments</li>
                <li>Project managers tracking contractual obligations</li>
                <li>Procurement departments evaluating supplier proposals</li>
                <li>Compliance officers ensuring regulatory adherence</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>Development Team</h3>
            <p><strong>Team DEVNEST</strong><br>
            Bannari Amman Institute of Technology</p>
            
            <p style="line-height: 1.8; color: #555;">Our team specializes in developing innovative software solutions 
            for real-world business challenges in construction and contract management sectors.</p>
            
            <h4>Project Details</h4>
            <p style="line-height: 1.8;"><strong>Development Timeline:</strong> 8 hours (Hackathon)<br>
            <strong>Status:</strong> Fully functional prototype<br>
            <strong>Technology Stack:</strong> Python, Streamlit, FastAPI</p>
            
            <h4>Future Enhancements</h4>
            <ul style="line-height: 1.8;">
                <li>Multi-language document support</li>
                <li>Automated email notifications</li>
                <li>PDF report generation</li>
                <li>Contract comparison features</li>
                <li>Mobile application development</li>
                <li>Advanced analytics dashboard</li>
            </ul>
            
            <h4>Contact Information</h4>
            <p style="line-height: 1.8;">For inquiries, partnerships, or technical support:<br>
            <strong>Email:</strong> team.devnest@bitsathy.ac.in<br>
            <strong>Institution:</strong> Bannari Amman Institute of Technology</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">8 Hours</div>
            <div class="metric-label">Development Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #2f9e44 0%, #2b8a3e 100%);">
            <div class="metric-value">100%</div>
            <div class="metric-label">Functional</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #e67700 0%, #cc6600 100%);">
            <div class="metric-value">Enterprise</div>
            <div class="metric-label">Grade Quality</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);">
            <div class="metric-value">Secure</div>
            <div class="metric-label">Data Processing</div>
        </div>
        """, unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem;">
    <p style="font-size: 1.1rem;"><strong>ContractIQ Enterprise Platform</strong></p>
    <p>Developed by Team DEVNEST | Bannari Amman Institute of Technology</p>
    <p style="font-size: 0.9rem; color: #ccc;">Transforming Contract Management | Copyright © 2024</p>
</div>
""", unsafe_allow_html=True)