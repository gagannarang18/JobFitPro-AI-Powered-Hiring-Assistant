import os
import streamlit as st
import PyPDF2
import io
# In app.py, change imports to:
from src.agents.resume_agent import ResumeAnalysisAgent
from src.ui import components as ui
import atexit
os.environ["STREAMLIT_SERVER_ENABLE_STATIC_FILE_WATCHER"] = "false"  # Add this

# Rest of your imports...
from langchain_community.vectorstores import FAISS
import torch  # This will now load safely

# This MUST be the first Streamlit command
st.set_page_config(
    page_title="JobFitPro: AI Powered Hiring Assistant",
    page_icon="🚀",
    layout="wide"
)

# Role requirements dictionary
ROLE_REQUIREMENTS = {
    "AI/ML Engineer": [
        "Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning",
        "MLOps", "Scikit-Learn", "NLP", "Computer Vision", "Reinforcement Learning",
        "Hugging Face", "Data Engineering", "Feature Engineering", "AutoML"
    ],
    "Frontend Engineer": [
        "React", "Vue", "Angular", "HTML5", "CSS3", "JavaScript", "TypeScript",
        "Next.js", "Svelte", "Bootstrap", "Tailwind CSS", "GraphQL", "Redux",
        "WebAssembly", "Three.js", "Performance Optimization"
    ],
    "Backend Engineer": [
        "Python", "Java", "Node.js", "REST APIs", "Cloud services", "Kubernetes",
        "Docker", "GraphQL", "Microservices", "gRPC", "Spring Boot", "Flask",
        "FastAPI", "SQL & NoSQL Databases", "Redis", "RabbitMQ", "CI/CD"
    ],
    "Data Engineer": [
        "Python", "SQL", "Apache Spark", "Hadoop", "Kafka", "ETL Pipelines",
        "Airflow", "BigQuery", "Redshift", "Data Warehousing", "Snowflake",
        "Azure Data Factory", "GCP", "AWS Glue", "DBT"
    ],
    "DevOps Engineer": [
        "Kubernetes", "Docker", "Terraform", "CI/CD", "AWS", "Azure", "GCP",
        "Jenkins", "Ansible", "Prometheus", "Grafana", "Helm", "Linux Administration",
        "Networking", "Site Reliability Engineering (SRE)"
    ],
    "Full Stack Developer": [
        "JavaScript", "TypeScript", "React", "Node.js", "Express", "MongoDB",
        "SQL", "HTML5", "CSS3", "RESTful APIs", "Git", "CI/CD", "Cloud Services",
        "Responsive Design", "Authentication & Authorization"
    ],
    "Product Manager": [
        "Product Strategy", "User Research", "Agile Methodologies", "Roadmapping",
        "Market Analysis", "Stakeholder Management", "Data Analysis", "User Stories",
        "Product Lifecycle", "A/B Testing", "KPI Definition", "Prioritization",
        "Competitive Analysis", "Customer Journey Mapping"
    ],
    "Data Scientist": [
        "Python", "R", "SQL", "Machine Learning", "Statistics", "Data Visualization",
        "Pandas", "NumPy", "Scikit-learn", "Jupyter", "Hypothesis Testing",
        "Experimental Design", "Feature Engineering", "Model Evaluation"
    ]
}

# Initialize session state variables
if 'resume_agent' not in st.session_state:
    st.session_state.resume_agent = None

if 'resume_analyzed' not in st.session_state:
    st.session_state.resume_analyzed = False

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

def setup_agent(config):
    """Set up the resume analysis agent with proper error handling"""
    # Always use .get() to safely access dictionary keys
    if not config or not isinstance(config, dict):
        st.error("⚠️ Invalid configuration. Please check your settings.")
        return None

    api_key = config.get("groq_api_key")  # This is the safe way

    if not api_key:
        st.error("""
        ⚠️ Groq API Key Required
        Please enter your Groq API Key in the sidebar to enable resume analysis.
        """)
        return None

    try:
        if st.session_state.resume_agent is None:
            st.session_state.resume_agent = ResumeAnalysisAgent(api_key=api_key)
        else:
            st.session_state.resume_agent.api_key = api_key
        
        return st.session_state.resume_agent
        
    except Exception as e:
        st.error(f"⚠️ Failed to initialize agent: {str(e)}")
        return None

def analyze_resume(agent, resume_file, role, custom_jd):
    """Analyze the resume with the agent"""
    if not resume_file:
        st.error("⚠️ Please upload a resume.")
        return None

    try:
        with st.spinner("🔍 Analyzing resume... This may take a minute."):
            if custom_jd:
                # Handle custom job description analysis
                result = agent.analyze_resume(resume_file, custom_jd=custom_jd)
            else:
                # Handle role-based analysis
                result = agent.analyze_resume(resume_file, role_requirements=ROLE_REQUIREMENTS[role])

            # Update session state with analysis results
            st.session_state.resume_analyzed = True
            st.session_state.analysis_result = result
            return result
    except Exception as e:
        st.error(f"⚠️ Error analyzing resume: {e}")
        return None

def ask_question(agent, question):
    """Ask a question about the resume"""
    try:
        with st.spinner("Generating response..."):
            response = agent.ask_question(question)
            return response
    except Exception as e:
        return f"Error: {e}"

def generate_interview_questions(agent, question_types, difficulty, num_questions):
    """Generate interview questions based on the resume"""
    try:
        with st.spinner("Generating personalized interview questions..."):
            questions = agent.generate_interview_questions(question_types, difficulty, num_questions)
            return questions
    except Exception as e:
        st.error(f"⚠️ Error generating questions: {e}")
        return []

def improve_resume(agent, improvement_areas, target_role):
    """Generate resume improvement suggestions"""
    try:
        with st.spinner("Analyzing and generating improvements..."):
            return agent.improve_resume(improvement_areas, target_role)
    except Exception as e:
        st.error(f"⚠️ Error generating improvements: {e}")
        return {}

def get_improved_resume(agent, target_role, highlight_skills):
    """Get an improved version of the resume"""
    try:
        with st.spinner("Creating improved resume..."):
            return agent.get_improved_resume(target_role, highlight_skills)
    except Exception as e:
        st.error(f"⚠️ Error creating improved resume: {e}")
        return "Error generating improved resume."

def cleanup():
    """Clean up resources when the app exits"""
    if st.session_state.resume_agent:
        st.session_state.resume_agent.cleanup()

# Register cleanup function
atexit.register(cleanup)

def main():
    # Setup page UI
    ui.setup_page()
    ui.display_header()

    # Get config with proper error handling
    try:
        config = ui.setup_sidebar() or {}  # Ensure we always get a dict
    except Exception as e:
        st.error(f"⚠️ Failed to load configuration: {str(e)}")
        config = {}

    # Set up the agent (will show errors if API key missing)
    agent = setup_agent(config)

    # Create tabs for different functionalities
    tabs = ui.create_tabs()

    # Tab 1: Resume Analysis
    with tabs[0]:
        role, custom_jd = ui.role_selection_section(ROLE_REQUIREMENTS)
        uploaded_resume = ui.resume_upload_section()

        if st.button("🔍 Analyze Resume", type="primary"):
            if not agent:
                st.error("Please provide a valid Groq API Key in the sidebar")
            elif not uploaded_resume:
                st.error("Please upload a resume file")
            else:
                analyze_resume(agent, uploaded_resume, role, custom_jd)
        
        if st.session_state.analysis_result:
            ui.display_analysis_results(st.session_state.analysis_result)

    # Tab 2: Resume Q&A
    with tabs[1]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.resume_qa_section(
                has_resume=True,
                ask_question_func=lambda q: ask_question(st.session_state.resume_agent, q)
            )
        else:
            st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")

    # Tab 3: Interview Questions
    with tabs[2]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.interview_questions_section(
                has_resume=True,
                generate_questions_func=lambda types, diff, num: generate_interview_questions(st.session_state.resume_agent, types, diff, num)
            )
        else:
            st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")

    # Tab 4: Resume Improvement
    with tabs[3]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.resume_improvement_section(
                has_resume=True,
                improve_resume_func=lambda areas, role: improve_resume(st.session_state.resume_agent, areas, role)
            )
        else:
            st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")

    # Tab 5: Improved Resume
    with tabs[4]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.improved_resume_section(
                has_resume=True,
                get_improved_resume_func=lambda role, skills: get_improved_resume(st.session_state.resume_agent, role, skills)
            )
        else:
            st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")

if __name__ == "__main__":
    main()