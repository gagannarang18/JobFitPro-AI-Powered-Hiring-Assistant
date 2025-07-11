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
        "MLOps", "Scikit-learn", "NLP", "Computer Vision", "Reinforcement Learning",
        "Hugging Face", "Data Engineering", "Feature Engineering", "AutoML",
        "Experiment Tracking", "Model Deployment", "ONNX", "AWS SageMaker"
    ],
    "AI Developer": [
        "Python", "LangChain", "LLMs", "Prompt Engineering", "Hugging Face", 
        "Vector Databases", "FAISS", "ChromaDB", "RAG", "Streamlit", 
        "OpenAI APIs", "Groq", "Bedrock", "Mistral", "Gemini", 
        "FastAPI", "Docker", "CI/CD", "Multimodal Models", "Prompt Tuning",
        "Evaluation Frameworks", "LangChain Agents", "Streamlit Cloud"
    ],
    "Frontend Engineer": [
        "React", "Next.js", "Vue", "Angular", "HTML5", "CSS3", "JavaScript",
        "TypeScript", "Tailwind CSS", "Bootstrap", "Redux", "GraphQL",
        "SWR/React Query", "Web Performance", "Accessibility (a11y)", "Three.js",
        "Responsive Design", "Vite", "Jest", "Cypress"
    ],
    "Backend Engineer": [
        "Python", "Java", "Node.js", "Go", "REST APIs", "GraphQL", 
        "Microservices", "gRPC", "Docker", "Kubernetes", "PostgreSQL", "MongoDB",
        "Redis", "RabbitMQ", "FastAPI", "Flask", "Spring Boot", 
        "CI/CD", "API Security", "Cloud Services (AWS/GCP/Azure)"
    ],
    "Data Engineer": [
        "Python", "SQL", "Apache Spark", "Kafka", "Hadoop", "ETL Pipelines", 
        "Airflow", "DBT", "Data Lakes", "Redshift", "BigQuery", "Snowflake", 
        "Data Modeling", "Azure Data Factory", "AWS Glue", "Parquet", "Delta Lake"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "Terraform", "Ansible", "CI/CD Pipelines", 
        "Jenkins", "GitHub Actions", "AWS", "Azure", "GCP", "Prometheus",
        "Grafana", "Helm", "Linux System Admin", "Nginx", "Monitoring & Logging",
        "Incident Management", "Infrastructure as Code", "SRE Practices"
    ],
    "Full Stack Developer": [
        "JavaScript", "TypeScript", "React", "Node.js", "Express.js", "Next.js",
        "MongoDB", "PostgreSQL", "SQL", "HTML5", "CSS3", "REST APIs", 
        "Authentication", "JWT", "OAuth", "CI/CD", "Docker", "Cloud Services",
        "State Management", "Responsive UI", "Unit Testing", "GraphQL"
    ],
    "Product Manager": [
        "Product Strategy", "Agile Methodologies", "Scrum", "Stakeholder Management",
        "User Research", "Wireframing", "Figma", "Roadmapping", "Backlog Grooming",
        "A/B Testing", "Data-Driven Decision Making", "SQL", "KPI Metrics",
        "Market Analysis", "Customer Journey Mapping", "Competitive Benchmarking",
        "JIRA", "Confluence"
    ],
    "Data Scientist": [
        "Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "Matplotlib",
        "Seaborn", "Machine Learning", "Deep Learning", "Model Evaluation",
        "EDA", "Hypothesis Testing", "Experimental Design", "XGBoost", 
        "Time Series Analysis", "Statistical Modeling", "Data Storytelling",
        "Jupyter", "Dashboards", "Feature Engineering", "Model Interpretability"
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