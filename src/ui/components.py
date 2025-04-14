# Change this import at top:
from src.agents.resume_agent import ResumeAnalysisAgent  # If needed
# Most agent interactions happen through app.py

import streamlit as st
import base64
import io
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def setup_page():
    """Apply custom CSS and setup page (without setting page config)"""
    apply_custom_css()
    
    st.markdown("""
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var logoImg = document.querySelector('.logo-image');
            if (logoImg) {
                logoImg.onerror = function() {
                    var logoContainer = document.querySelector('.logo-container');
                    if (logoContainer) {
                        logoContainer.innerHTML = '<div style="font-size: 40px;">🚀</div>';
                    }
                };
            }
        });
    </script>
    """, unsafe_allow_html=True)

def display_header():
    try:
        with open("job.jpg", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
            logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" alt="JobFitPro Logo" class="logo-image" style="height: 80px; margin-bottom: 10px;">'
    except:
        logo_html = '<div style="font-size: 50px; margin-bottom: 10px;">🚀</div>'

    st.markdown(f"""
    <div class="main-header">
        <div class="header-container" style="text-align: center; padding: 20px 0;">
            <div class="logo-container">
                {logo_html}
            </div>
            <h1 style="margin-bottom: 0; color: #2a52be; font-weight: 700;">JobFitPro</h1>
            <p style="margin-top: 5px; font-size: 1.1rem; color: #555;">AI Powered Hiring Assistant</p>
            <div style="height: 3px; background: linear-gradient(90deg, #2a52be 0%, #4CAF50 100%); margin: 10px auto 15px; width: 100px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def apply_custom_css(accent_color="#2a52be"):
    st.markdown(f"""
    <style>
        /* Main container */
        .main {{
            background-color: #f8f9fa !important;
            color: #333 !important;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background-color: #ffffff !important;
            border-right: 1px solid #e0e0e0 !important;
        }}
        
        /* Active tabs and highlights */
        .stTabs [aria-selected=\"true\"] {{
            color: {accent_color} !important;
            border-bottom: 3px solid {accent_color} !important;
            font-weight: 600;
        }}
        
        .stTabs [aria-selected=\"false\"] {{
            color: #666 !important;
        }}
        
        /* Buttons */
        .stButton button {{
            background-color: {accent_color} !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            border: none !important;
        }}
        
        .stButton button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        /* Input fields */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {{
            background-color: #ffffff !important;
            border: 1px solid #ddd !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
        }}
        
        /* Cards */
        .card {{
            background-color: #ffffff !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
            border-left: 4px solid {accent_color} !important;
        }}
        
        /* Skill tags */
        .skill-tag {{
            display: inline-block;
            background-color: {accent_color}20;
            color: {accent_color};
            padding: 4px 12px;
            border-radius: 16px;
            margin: 4px;
            font-size: 0.85rem;
            border: 1px solid {accent_color}30;
            font-weight: 500;
        }}
        
        .skill-tag.missing {{
            background-color: #f8d7da30;
            color: #dc3545;
            border: 1px solid #f8d7da50;
        }}
        
        /* Metrics */
        .stMetric {{
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        /* Expanders */
        .stExpander {{
            border: 1px solid #eee !important;
            border-radius: 8px !important;
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {accent_color}80;
            border-radius: 4px;
        }}
        
        /* Tooltips */
        .stTooltip {{
            background-color: #333 !important;
            color: white !important;
            border-radius: 8px !important;
        }}
        
        /* Progress bars */
        .stProgress > div > div {{
            background-color: {accent_color} !important;
        }}
        
        /* Custom HR */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, {accent_color} 50%, transparent 100%);
            margin: 20px 0;
        }}
        
        /* Custom file uploader */
        .stFileUploader {{
            border: 2px dashed #ddd !important;
            border-radius: 8px !important;
            padding: 20px !important;
        }}
        
        /* Download buttons */
        .download-btn {{
            display: inline-block;
            background-color: {accent_color} !important;
            color: white !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            text-decoration: none !important;
            margin: 5px 0 !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .download-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            color: white !important;
        }}

        /* Q&A Response */
        .qa-response {{
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
            border-left: 3px solid {accent_color};
        }}

        /* Interview Questions */
        .question-card {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 3px solid {accent_color};
        }}

        /* Resume Comparison */
        .comparison-box {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
    </style>
    """, unsafe_allow_html=True)

def setup_sidebar():
    """Set up the sidebar and return configuration with proper API key handling"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #2a52be; margin-bottom: 5px;">⚙️ Configuration</h3>
            <div style="height: 2px; background: linear-gradient(90deg, #2a52be 0%, #4CAF50 100%); margin: 0 auto 15px; width: 50%;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Groq API Key (with validation and placeholder)
        groq_api_key = st.text_input(
            "🔑 Groq API Key*",
            type="password",
            help="Get your API key from Groq's website (required for analysis)",
            placeholder="sk_xxxxxxxxxxxxxxxx"
        )
        
        st.markdown("---")
        
        # Theme customization
        st.markdown("""
        <div style="margin-bottom: 10px;">
            <h4 style="color: #2a52be; margin-bottom: 5px;">🎨 Theme</h4>
        </div>
        """, unsafe_allow_html=True)
        
        theme_color = st.color_picker("Accent Color", "#2a52be", key="theme_color")
        
        st.markdown("---")
        
        # Footer
        st.markdown(""" 
        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 0.85rem;">
            <p>🚀 JobFitPro v1.0.0</p>
            <p style="font-size: 0.75rem;">AI Powered Hiring Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        return {
            "groq_api_key": groq_api_key,
            "theme_color": theme_color
        }

def create_score_pie_chart(score):
    """Create a professional donut chart for the score visualization"""
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='none')
    
    # Create gradient color
    colors = ["#2a52be", "#e0e0e0"]
    
    # Data
    sizes = [score, 100 - score]
    labels = ['', '']
    explode = (0.05, 0)
    
    # Plot
    wedges, _ = ax.pie(
        sizes, 
        colors=colors,
        startangle=90,
        wedgeprops={'width': 0.5, 'edgecolor': 'white', 'linewidth': 2}
    )
    
    # Add circle in center
    centre_circle = plt.Circle((0, 0), 0.3, fc='white')
    ax.add_artist(centre_circle)
    
    # Add score text
    ax.text(0, 0.1, f"{score}", 
            ha='center', va='center', 
            fontsize=28, fontweight='bold', 
            color='#2a52be')
    
    ax.text(0, -0.15, "Score", 
            ha='center', va='center', 
            fontsize=12, 
            color='#666')
    
    # Status indicator
    status = "PASS" if score >= 75 else "FAIL"
    status_color = "#4CAF50" if score >= 75 else "#f44336"
    ax.text(0, -0.3, status, 
            ha='center', va='center', 
            fontsize=14, fontweight='bold', 
            color=status_color)
    
    # Remove axes
    ax.axis('equal')
    
    return fig

def role_selection_section(role_requirements):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #2a52be; margin-bottom: 15px;">
        <span style="display: inline-block; width: 30px; text-align: center;">📋</span> 
        Target Role Selection
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        role = st.selectbox(
            "Select the role you're applying for:", 
            list(role_requirements.keys()),
            index=0,
            help="Choose the job role you want to analyze your resume against"
        )
    
    with col2:
        upload_jd = st.checkbox(
            "Upload custom job description",
            help="Check this if you want to use a specific job description instead"
        )
    
    custom_jd = None
    if upload_jd:
        custom_jd_file = st.file_uploader(
            "Upload job description (PDF or TXT)", 
            type=["pdf", "txt"],
            label_visibility="collapsed"
        )
        if custom_jd_file:
            st.success("✅ Custom job description uploaded!")
            custom_jd = custom_jd_file
    
    if not upload_jd:
        with st.expander("🔍 View required skills for this role"):
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px;">
                <p style="font-weight: 500; margin-bottom: 8px;">Key Skills:</p>
                <div style="display: flex; flex-wrap: wrap;">
                    {''.join([f'<span class="skill-tag">{skill}</span>' for skill in role_requirements[role]])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.info(f"ℹ️ Cutoff Score for selection: **75/100**", icon="ℹ️")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return role, custom_jd

def resume_upload_section():
    st.markdown("""
    <div class="card">
        <h3 style="color: #2a52be; margin-bottom: 15px;">
            <span style="display: inline-block; width: 30px; text-align: center;">📄</span> 
            Upload Your Resume
        </h3>
        <p style="color: #666; margin-bottom: 15px;">Supported formats: PDF</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_resume = st.file_uploader(
        "Drag and drop your resume here or click to browse",
        type=["pdf"],
        label_visibility="collapsed"
    )
    
    if uploaded_resume:
        st.success("✅ Resume uploaded successfully!")
    
    return uploaded_resume

def display_analysis_results(analysis_result):
    if not analysis_result:
        return

    overall_score = analysis_result.get('overall_score', 0)
    selected = analysis_result.get("selected", False)
    skill_scores = analysis_result.get("skill_scores", {})
    detailed_weaknesses = analysis_result.get("detailed_weaknesses", [])

    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Analysis header with timestamp
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h2 style="color: #2a52be; margin-bottom: 0;">Resume Analysis Report</h2>
            <div style="font-size: 0.8rem; color: #666;">Generated just now</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Score and result section
    col1, col2 = st.columns([1, 2])

    with col1:
        # Score metric with icon
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1rem; color: #666; margin-bottom: 5px;">Overall Score</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #2a52be; margin-bottom: 10px;">
                {overall_score}<span style="font-size: 1.5rem; color: #666;">/100</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Donut chart
        fig = create_score_pie_chart(overall_score)
        st.pyplot(fig, use_container_width=True)

    with col2:
        # Result card
        if selected:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 1.5rem; margin-right: 10px;">✅</span>
                    <h2 style="color: #2e7d32; margin-bottom: 0;">Congratulations!</h2>
                </div>
                <p style="color: #2e7d32; margin-bottom: 0;">Your resume meets the requirements for this role.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #ffebee; padding: 20px; border-radius: 10px; border-left: 4px solid #f44336;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 1.5rem; margin-right: 10px;">❌</span>
                    <h2 style="color: #c62828; margin-bottom: 0;">Needs Improvement</h2>
                </div>
                <p style="color: #c62828; margin-bottom: 0;">Your resume doesn't yet meet the requirements for this role.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Reasoning in expandable section
        with st.expander("📝 Analysis Details", expanded=True):
            st.write(analysis_result.get('reasoning', 'No reasoning provided.'))

    st.markdown('<hr>', unsafe_allow_html=True)

    # Skills analysis section
    st.markdown('<div class="strengths-improvements">', unsafe_allow_html=True)

    # Strengths
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #e8f5e920; padding: 15px; border-radius: 10px;">
        <h3 style="color: #2e7d32; margin-bottom: 15px;">🌟 Strengths</h3>
    """, unsafe_allow_html=True)
    
    strengths = analysis_result.get("strengths", [])
    if strengths:
        st.markdown('<div style="display: flex; flex-wrap: wrap;">', unsafe_allow_html=True)
        for skill in strengths:
            st.markdown(f'<div class="skill-tag">{skill} ({skill_scores.get(skill, "N/A")}/10)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No notable strengths identified.", icon="ℹ️")
    st.markdown('</div>', unsafe_allow_html=True)

    # Weaknesses
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #ffebee20; padding: 15px; border-radius: 10px;">
        <h3 style="color: #c62828; margin-bottom: 15px;">🚩 Areas for Improvement</h3>
    """, unsafe_allow_html=True)
    
    missing_skills = analysis_result.get("missing_skills", [])
    if missing_skills:
        st.markdown('<div style="display: flex; flex-wrap: wrap;">', unsafe_allow_html=True)
        for skill in missing_skills:
            st.markdown(f'<div class="skill-tag missing">{skill} ({skill_scores.get(skill, "N/A")}/10)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No significant areas for improvement.", icon="ℹ️")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed weaknesses section
    if detailed_weaknesses:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown("""
        <h3 style="color: #2a52be; margin-bottom: 15px;">
            <span style="display: inline-block; width: 30px; text-align: center;">🔍</span> 
            Detailed Skill Analysis
        </h3>
        """, unsafe_allow_html=True)
        
        for weakness in detailed_weaknesses:
            skill_name = weakness.get('skill', '')
            score = weakness.get('score', 0)
            
            with st.expander(f"{skill_name} (Score: {score}/10)", expanded=False):
                # Clean detail display
                detail = weakness.get('detail', 'No specific details provided.')
                if detail.startswith('```json') or '{' in detail:
                    detail = "The resume lacks examples of this skill."
                
                st.markdown(f"""
                <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ffa000;">
                    <h4 style="color: #ff6f00; margin-top: 0;">Issue Identified</h4>
                    <p>{detail}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display improvement suggestions if available
                if 'suggestions' in weakness and weakness['suggestions']:
                    st.markdown("""
                    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4CAF50;">
                        <h4 style="color: #2e7d32; margin-top: 0;">How to Improve</h4>
                    """, unsafe_allow_html=True)
                    for i, suggestion in enumerate(weakness['suggestions']):
                        st.markdown(f'<p>{i+1}. {suggestion}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # In display_analysis_results() function, modify the detailed weaknesses section:

                # Display example if available
                if weakness.get('example'):  # Safely check using .get()
                 st.markdown(f"""
    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #2196F3;">
        <h4 style="color: #1565c0; margin-top: 0;">Example Improvement</h4>
        <p>{weakness.get('example', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Report download section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <h4 style="color: #2a52be; margin-bottom: 15px;">📊 Download Full Analysis Report</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate report content
    report_content = f"""
# JobFitPro - Resume Analysis Report

## Overall Score: {overall_score}/100
Status: {"✅ Shortlisted" if selected else "❌ Not Selected"}

## Analysis Reasoning
{analysis_result.get('reasoning', 'No reasoning provided.')}

## Strengths
{", ".join(strengths if strengths else ["None identified"])}

## Areas for Improvement
{", ".join(missing_skills if missing_skills else ["None identified"])}

## Detailed Weakness Analysis
"""
    
    # Add detailed weaknesses to report
    for weakness in detailed_weaknesses:
        skill_name = weakness.get('skill', '')
        score = weakness.get('score', 0)
        detail = weakness.get('detail', 'No specific details provided.')
        
        if detail.startswith('```json') or '{' in detail:
            detail = "The resume lacks examples of this skill."
            
        report_content += f"\n### {skill_name} (Score: {score}/10)\n"
        report_content += f"Issue: {detail}\n"
        
        if 'suggestions' in weakness and weakness['suggestions']:
            report_content += "\nImprovement suggestions:\n"
            for i, sugg in enumerate(weakness['suggestions']):
                report_content += f"- {sugg}\n"
        
        if 'example' in weakness and weakness['example']:
            report_content += f"\nExample: {weakness['example']}\n"
    
    report_content += "\n---\nAnalysis provided by JobFitPro"
    
    # Create download button
    report_b64 = base64.b64encode(report_content.encode()).decode()
    st.markdown(
        f'<a class="download-btn" href="data:text/plain;base64,{report_b64}" download="JobFitPro_resume_analysis.txt" style="display: inline-block; margin: 0 auto;">📥 Download Full Report (TXT)</a>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)
    
    
def resume_improvement_section(has_resume, improve_resume_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    # Unified blue styling
    st.markdown("""
    <style>
        /* Unified button styling */
        div.stButton > button {
            background-color: #2a52be !important;
            color: white !important;
            border-radius: 8px;
            padding: 8px 16px;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Comparison boxes */
        .comparison-box strong {color: #2a52be !important;}
        pre {border-left: 3px solid #2a52be !important;}
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="card">
            <h3 style="color: #2a52be; margin-bottom: 15px;">
                <span style="display: inline-block; width: 30px; text-align: center;">✨</span> 
                Resume Improvement Suggestions
            </h3>
            <p style="color: #666;">Get personalized recommendations to enhance your resume</p>
        """, unsafe_allow_html=True)

        improvement_areas = st.multiselect(
            "Select areas to improve:",
            ["Content", "Format", "Skills Highlighting", "Experience Description", 
             "Education", "Projects", "Achievements", "Overall Structure"],
            default=["Content", "Skills Highlighting"]
        )

        target_role = st.text_input("Target role (optional):", 
                                  placeholder="e.g., Senior Data Scientist at Google")

        if st.button("Generate Resume Improvements", type="primary"):
            if improve_resume_func:
                with st.spinner("Analyzing and generating improvements..."):
                    improvements = improve_resume_func(improvement_areas, target_role)
                    
                    if improvements:
                        download_content = f"# Resume Improvement Suggestions\n\nTarget Role: {target_role or 'Not specified'}\n\n"
                        
                        for area, suggestions in improvements.items():
                            with st.expander(f"Improvements for {area}", expanded=True):
                                # Main description
                                st.markdown(f"""
                                <div style="color: #333; line-height: 1.6;">
                                    {suggestions.get('description', '')}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Specific suggestions
                                st.markdown("#### Specific Suggestions")
                                for i, suggestion in enumerate(suggestions.get("specific", [])):
                                    st.markdown(f"""
                                    <div style="margin: 8px 0; padding-left: 15px; border-left: 3px solid #2a52be;">
                                        {i+1}. {suggestion}
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Before/After comparison
                                if "before_after" in suggestions:
                                    st.markdown("""
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                                        <div class="comparison-box">
                                            <strong>Before:</strong>
                                            <pre>{before_content}</pre>
                                        </div>
                                        <div class="comparison-box">
                                            <strong>After:</strong>
                                            <pre>{after_content}</pre>
                                        </div>
                                    </div>
                                    """.format(
                                        before_content=suggestions["before_after"]["before"],
                                        after_content=suggestions["before_after"]["after"]
                                    ), unsafe_allow_html=True)

                        # Download button
                        st.markdown("---")
                        report_b64 = base64.b64encode(download_content.encode()).decode()
                        st.markdown(
                            f'<a href="data:text/markdown;base64,{report_b64}" download="resume_improvements.md" '
                            'style="display: inline-block; padding: 0.5em 1em; background-color: #2a52be; '
                            'color: white; border-radius: 5px; text-decoration: none;">'
                            '📥 Download All Suggestions</a>',
                            unsafe_allow_html=True
                        )

        st.markdown("</div>", unsafe_allow_html=True)


def resume_qa_section(has_resume, ask_question_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.subheader("Ask Questions About the Resume")
    
    # Initialize session state for current question
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    
    user_question = st.text_input(
        "Enter your question about the resume:",
        value=st.session_state.current_question,
        placeholder="What is the candidate's most recent experience?"
    )
    
    if user_question and ask_question_func:
        with st.spinner("Searching resume and generating response..."):
            response = ask_question_func(user_question)
            
            st.markdown(
                '<div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 3px solid #2a52be;">',
                unsafe_allow_html=True
            )
            st.write(response)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Add example questions
    with st.expander("Example Questions"):
        example_questions = [
            "What is the candidate's most recent role?",
            "How many years of experience does the candidate have with Python?",
            "What educational qualifications does the candidate have?",
            "What are the candidate's key achievements?",
            "Has the candidate managed teams before?",
            "What projects has the candidate worked on?",
            "Does the candidate have experience with cloud technologies?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"q_{question}"):
                st.session_state.current_question = question
                st.rerun()  # Changed to current rerun method
    
    st.markdown('</div>', unsafe_allow_html=True)

def interview_questions_section(has_resume, generate_questions_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    # Custom CSS for consistent blue styling
    st.markdown("""
    <style>
        /* Blue button styling */
        div.stButton > button {
            background-color: #2a52be !important;
            color: white !important;
            border-radius: 8px;
            padding: 8px 16px;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Question type labels in multiselect */
        .st-c7 { color: #2a52be !important; }
        
        /* Coding block styling */
        .stCode pre { border-left: 3px solid #2a52be !important; }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="card">
            <h3 style="color: #2a52be; margin-bottom: 15px;">
                <span style="display: inline-block; width: 30px; text-align: center;">📝</span> 
                Interview Questions
            </h3>
            <p style="color: #666;">Generate role-specific questions</p>
        """, unsafe_allow_html=True)
        
        # Improved form layout
        cols = st.columns(2)
        with cols[0]:
            question_types = st.multiselect(
                "Question types:",
                ["Basic", "Technical", "Behavioral", "Scenario", "Coding", "Experience"],
                default=["Technical", "Basic"]
            )
        with cols[1]:
            difficulty = st.select_slider(
                "Difficulty:",
                options=["Easy", "Medium", "Hard"],
                value="Medium"
            )
        
        num_questions = st.slider("Number of questions:", 3, 15, 5)
        
        if st.button("Generate Questions", type="primary"):
            if generate_questions_func:
                with st.spinner("Creating personalized questions..."):
                    questions = generate_questions_func(question_types, difficulty, num_questions)
                    
                    if questions:
                        st.markdown("---")
                        for i, (q_type, question) in enumerate(questions):
                            st.markdown(f"""
                            <div class="question-card">
                                <strong>Q{i+1}:</strong> 
                                <span style="color: #2a52be; font-weight: 500;">({q_type})</span> 
                                {question}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if q_type == "Coding":
                                st.code("# Write your solution here", language="python")
                        
                        # Download option
                        st.markdown("---")
                        download_content = "# JobFitPro - Interview Questions\n\n"
                        download_content += f"Difficulty: {difficulty}\nTypes: {', '.join(question_types)}\n\n"
                        
                        for i, (q_type, question) in enumerate(questions):
                            download_content += f"## {i+1}. {q_type} Question\n\n{question}\n\n"
                            if q_type == "Coding":
                                download_content += "```python\n# Write your solution here\n```\n\n"
                        
                        download_content += "Generated by JobFitPro"
                        
                        questions_b64 = base64.b64encode(download_content.encode()).decode()
                        st.markdown(
                            f'<a class="download-btn" href="data:text/markdown;base64,{questions_b64}" download="JobFitPro_interview_questions.md">📥 Download All Questions</a>',
                            unsafe_allow_html=True
                        )
        
        st.markdown("</div>", unsafe_allow_html=True)

def improved_resume_section(has_resume, get_improved_resume_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    with st.container():
        st.markdown("""
        <div class="card">
            <h3 style="color: #2a52be; margin-bottom: 15px;">
                <span style="display: inline-block; width: 30px; text-align: center;">📄</span> 
                Improved Resume Generator
            </h3>
            <p style="color: #666;">Get an optimized version of your resume tailored for a specific role</p>
        """, unsafe_allow_html=True)
        
        target_role = st.text_input(
            "Target role:",
            placeholder="e.g., Senior Software Engineer at TechCo",
            key="improved_resume_role"
        )
        
        highlight_skills = st.text_area(
            "Key skills to highlight (or paste job description):",
            placeholder="Python, Machine Learning, Cloud Computing...",
            height=100
        )
        
        if st.button("Generate Improved Resume", type="primary"):
            if get_improved_resume_func and target_role:
                with st.spinner("Creating optimized resume..."):
                    improved_resume = get_improved_resume_func(target_role, highlight_skills)
                    
                    if improved_resume:
                        st.markdown("---")
                        st.markdown("""
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                            <h4 style="color: #2a52be; margin-top: 0;">Optimized Resume</h4>
                        """, unsafe_allow_html=True)
                        
                        st.text_area(
                            "Improved Resume Content", 
                            improved_resume, 
                            height=400,
                            label_visibility="collapsed"
                        )
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Download buttons
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Text file download
                            resume_b64 = base64.b64encode(improved_resume.encode()).decode()
                            st.markdown(
                                f'<a class="download-btn" href="data:text/plain;base64,{resume_b64}" download="JobFitPro_improved_resume.txt">📄 Download as TXT</a>',
                                unsafe_allow_html=True
                            )
                        
                        with col2:
                            # Markdown file download
                            md_content = f"# {target_role} Resume\n\n{improved_resume}\n\n---\nGenerated by JobFitPro"
                            md_b64 = base64.b64encode(md_content.encode()).decode()
                            st.markdown(
                                f'<a class="download-btn" href="data:text/markdown;base64,{md_b64}" download="JobFitPro_improved_resume.md">📝 Download as Markdown</a>',
                                unsafe_allow_html=True
                            )
        
        st.markdown("</div>", unsafe_allow_html=True)

def create_tabs():
    """Create styled tabs for navigation"""
    return st.tabs([
        "📊 Resume Analysis", 
        "💬 Resume Q&A", 
        "❓ Interview Questions", 
        "✨ Resume Improvement", 
        "📄 Improved Resume"
    ])