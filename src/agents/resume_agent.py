import re
import PyPDF2
import io
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
import json

class ResumeAnalysisAgent:
    def __init__(self, api_key, cutoff_score=75):
        self.api_key = api_key
        self.cutoff_score = cutoff_score
        self.resume_text = None
        self.rag_vectorstore = None
        self.analysis_result = None
        self.jd_text = None
        self.extracted_skills = None
        self.resume_weaknesses = []
        self.resume_strengths = []
        self.improvement_suggestions = {}

        # Initialize Hugging Face embeddings once in init
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def create_rag_vector_store(self, text):
        """Create a vector store for RAG using Hugging Face embeddings and FAISS."""
        
        # Split text into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)

        # Use the pre-initialized Hugging Face embeddings
        vectorstore = FAISS.from_texts(chunks, self.embeddings)
        
        return vectorstore


    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file"""
        try:
            # Handle different file types
            if hasattr(pdf_file, 'read'):
                # In-memory file (BytesIO)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
            elif isinstance(pdf_file, (str, os.PathLike)):
                # File path
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
            else:
                # Assume it's a file-like object in bytes
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_text_from_txt(self, txt_file):
        """Extract text from a text file"""
        try:
            # Handle both in-memory files and file paths
            if hasattr(txt_file, 'read'):
                if 'b' in txt_file.mode:  # Binary mode
                    return txt_file.read().decode('utf-8')
                else:  # Text mode
                    return txt_file.read()
            else:  # Assume it's a file path
                with open(txt_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error extracting text from text file: {e}")
            return ""

    def extract_text_from_file(self, file):
        """Extract text from a file (PDF or TXT)"""
        if hasattr(file, 'name'):
            file_extension = file.name.split('.')[-1].lower()
        else:
            file_extension = file.split('.')[-1].lower()
            
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(file)
        else:
            print(f"Unsupported file extension: {file_extension}")
            return ""



    def create_vector_store(self, text):
        """Create a simpler vector store for skill analysis using Hugging Face embeddings"""
    
        # Use the pre-initialized Hugging Face embeddings
        vectorstore = FAISS.from_texts([text], self.embeddings)
    
        return vectorstore


    def analyze_skill(self, qa_chain, skill):
        """Analyze a skill in the resume using Groq"""
        query = f"On a scale of 0-10, how clearly does the candidate mention proficiency in {skill}? Provide a numeric rating first, followed by reasoning."
        
        # Get response from the Groq-based qa_chain
        response = qa_chain.run(query)
        
        # Extract numeric score from the response (assuming it is in the format 'score. reasoning')
        match = re.search(r"(\d{1,2})", response)
        score = int(match.group(1)) if match else 0

        # Extract reasoning (everything after the first period)
        reasoning = response.split('.', 1)[1].strip() if '.' in response and len(response.split('.')) > 1 else ""
        
        # Return the skill name, score, and reasoning
        return skill, min(score, 10), reasoning



    def analyze_resume_weaknesses(self):
        """Analyze specific weaknesses in the resume based on missing skills using Groq API"""
        if not self.resume_text or not self.extracted_skills or not self.analysis_result:
            return []
        
        weaknesses = []
        
        for skill in self.analysis_result.get("missing_skills", []):
            # Initialize Groq with the free model (adjust model name if needed)
            llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.api_key)
            
            # Construct the prompt for skill analysis
            prompt = f"""
            Analyze why the resume is weak in demonstrating proficiency in "{skill}".
            
            For your analysis, consider:
            1. What's missing from the resume regarding this skill?
            2. How could it be improved with specific examples?
            3. What specific action items would make this skill stand out?
            
            Resume Content:
            {self.resume_text[:3000]}...
            
            Provide your response in this JSON format:
            {{
                "weakness": "A concise description of what's missing or problematic (1-2 sentences)",
                "improvement_suggestions": [
                    "Specific suggestion 1",
                    "Specific suggestion 2",
                    "Specific suggestion 3"
                ],
                "example_addition": "A specific bullet point that could be added to showcase this skill"
            }}
            
            Return only valid JSON, no other text.
            """
            
            # Get the response from Groq
            response = llm.invoke(prompt)
            weakness_content = response.content.strip()
            
            try:
                # Attempt to parse the response as JSON
                weakness_data = json.loads(weakness_content)
                
                weakness_detail = {
                    "skill": skill,
                    "score": self.analysis_result.get("skill_scores", {}).get(skill, 0),
                    "detail": weakness_data.get("weakness", "No specific details provided."),
                    "suggestions": weakness_data.get("improvement_suggestions", []),
                    "example": weakness_data.get("example_addition", "")
                }
                
                weaknesses.append(weakness_detail)

                # Store the improvement suggestions for later use
                self.improvement_suggestions[skill] = {
                    "suggestions": weakness_data.get("improvement_suggestions", []),
                    "example": weakness_data.get("example_addition", "")
                }
            except json.JSONDecodeError:
                # If response is not valid JSON, store a truncated version of the content
                weaknesses.append({
                    "skill": skill,
                    "score": self.analysis_result.get("skill_scores", {}).get(skill, 0),
                    "detail": weakness_content[:200]  # Truncate if it's not proper JSON
                })
        
        # Store the weaknesses found during the analysis
        self.resume_weaknesses = weaknesses
        return weaknesses

    
    
    def extract_skills_from_jd(self, jd_text):
        """Extract skills from a job description using Groq API"""
        try:
            llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.api_key)
            prompt = f"""
            Extract a comprehensive list of technical skills, technologies, and competencies required from this job description. 
            Format the output as a Python list of strings. Only include the list, nothing else.
            
            Job Description:
            {jd_text}
            """
            
            response = llm.invoke(prompt)
            skills_text = response.content
            
            # Extract list using regex
            match = re.search(r'\[(.*?)\]', skills_text, re.DOTALL)
            if match:
                skills_text = match.group(0)
            
            try:
                skills_list = eval(skills_text)
                if isinstance(skills_list, list):
                    return skills_list
            except:
                pass
            
            # Fallback method: Extract bullet points or quoted text
            skills = []
            for line in skills_text.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):  # Bullet points
                    skill = line[2:].strip()
                    if skill:
                        skills.append(skill)
                elif line.startswith('"') and line.endswith('"'):  # Quoted items
                    skill = line.strip('"')
                    if skill:
                        skills.append(skill)
            
            return skills
        except Exception as e:
            print(f"Error extracting skills from job description: {e}")
            return []


  

    def semantic_skill_analysis(self, resume_text, skills):
        """Analyze skills semantically using Groq"""
        vectorstore = self.create_vector_store(resume_text)
        retriever = vectorstore.as_retriever()
        
        # Use Groq's Chat model
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.api_key)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False
        )
        

        skill_scores = {}
        skill_reasoning = {}
        missing_skills = []
        total_score = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda skill: self.analyze_skill(qa_chain, skill), skills))

        for skill, score, reasoning in results:
            skill_scores[skill] = score
            skill_reasoning[skill] = reasoning
            total_score += score
            if score <= 5:
                missing_skills.append(skill)

        overall_score = int((total_score / (10 * len(skills))) * 100)
        selected = overall_score >= self.cutoff_score

        reasoning = "Candidate evaluated based on explicit resume content using semantic similarity and clear numeric scoring."
        strengths = [skill for skill, score in skill_scores.items() if score >= 7]
        improvement_areas = missing_skills if not selected else []

        self.resume_strengths = strengths

        return {
            "overall_score": overall_score,
            "skill_scores": skill_scores,
            "skill_reasoning": skill_reasoning,
            "selected": selected,
            "reasoning": reasoning,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "improvement_areas": improvement_areas
        }


    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):
        """Analyze a resume against role requirements or a custom JD using Groq"""
        self.resume_text = self.extract_text_from_file(resume_file)
        
        # Save resume text to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tmp:
            tmp.write(self.resume_text)
            self.resume_file_path = tmp.name
        
        # Create RAG vector store using the resume text
        self.rag_vectorstore = self.create_rag_vector_store(self.resume_text)
        
        # If custom job description is provided
        if custom_jd:
            self.jd_text = self.extract_text_from_file(custom_jd)
            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)
            
            # Perform semantic skill analysis
            self.analysis_result = self.semantic_skill_analysis(self.resume_text, self.extracted_skills)

        # If role requirements are provided
        elif role_requirements:
            self.extracted_skills = role_requirements
            
            # Perform semantic skill analysis
            self.analysis_result = self.semantic_skill_analysis(self.resume_text, role_requirements)
        
        # Analyze weaknesses if any missing skills are found
        if self.analysis_result and "missing_skills" in self.analysis_result and self.analysis_result["missing_skills"]:
            self.analyze_resume_weaknesses()
            
            # Add detailed weaknesses to the result
            self.analysis_result["detailed_weaknesses"] = self.resume_weaknesses
        
        return self.analysis_result


    def ask_question(self, question):
        """Ask a question about the resume"""
        if not self.rag_vectorstore or not self.resume_text:
            return "Please analyze a resume first."
        
        try:
            # Create the retriever from the vector store
            retriever = self.rag_vectorstore.as_retriever(
                search_kwargs={"k": 3}  # Retrieve top 3 relevant results
            )
            
            # Use Groq's model for QA with the retriever
            qa_chain = RetrievalQA.from_chain_type(
                llm=ChatGroq(model_name="llama-3.3-70b-versatile", api_key=self.api_key),  # Updated to use Groq
                chain_type="stuff",  # Using "stuff" chain type
                retriever=retriever,
                return_source_documents=False,
            )
            
            # Run the question with the retriever and model
            response = qa_chain.run(question)
            return response
        except Exception as e:
            print(f"Error in asking question: {e}")
            return "Error processing the question."

    def generate_interview_questions(self, question_types, difficulty, num_questions):
        """Generate interview questions based on the resume"""
        if not self.resume_text or not self.extracted_skills:
            return []
        
        try:
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=self.api_key)  # Updated to use Groq
            
            context = f"""
            Resume Content:
            {self.resume_text[:2000]}...
            
            Skills to focus on: {', '.join(self.extracted_skills)}
            
            Strengths: {', '.join(self.analysis_result.get('strengths', []))}
            
            Areas for improvement: {', '.join(self.analysis_result.get('missing_skills', []))}
            """
            
            prompt = f"""
            Generate {num_questions} personalized {difficulty.lower()} level interview questions for this candidate 
            based on their resume and skills. Include only the following question types: {', '.join(question_types)}.
            
            For each question:
            1. Clearly label the question type
            2. Make the question specific to their background and skills
            3. For coding questions, include a clear problem statement
            
            {context}
            
            Format the response as a list of tuples with the question type and the question itself.
            Each tuple should be in the format: ("Question Type", "Full Question Text")
            """
            
            response = llm.invoke(prompt)
            questions_text = response.content
            
            questions = []
            pattern = r'[("]([^"]+)[",)\s]+[(",\s]+([^"]+)[")\s]+'
            matches = re.findall(pattern, questions_text, re.DOTALL)
            
            for match in matches:
                if len(match) >= 2:
                    question_type = match[0].strip()
                    question = match[1].strip()
                    
                    for requested_type in question_types:
                        if requested_type.lower() in question_type.lower():
                            questions.append((requested_type, question))
                            break

            if not questions:
                lines = questions_text.split('\n')
                current_type = None
                current_question = ""
                
                for line in lines:
                    line = line.strip()
                    if any(t.lower() in line.lower() for t in question_types) and not current_question:
                        current_type = next((t for t in question_types if t.lower() in line.lower()), None)
                        if ":" in line:
                            current_question = line.split(":", 1)[1].strip()
                    elif current_type and line:
                        current_question += " " + line
                    elif current_type and current_question:
                        questions.append((current_type, current_question))
                        current_type = None
                        current_question = ""

            questions = questions[:num_questions]
            
            return questions
        
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            return []

    def improve_resume(self, improvement_areas, target_role=""):
        """Generate suggestions to improve the resume"""
        if not self.resume_text:
            return {}
    
        try:
            improvements = {}
            
            # Process known improvement area "Skills Highlighting"
            if "Skills Highlighting" in improvement_areas and self.resume_weaknesses:
                skill_improvements = {
                    "description": "Your resume needs to better highlight key skills that are important for the role.",
                    "specific": []
                }
                before_after_examples = {}
                
                for weakness in self.resume_weaknesses:
                    skill_name = weakness.get("skill", "")
                    if "suggestions" in weakness and weakness["suggestions"]:
                        for suggestion in weakness["suggestions"]:
                            if isinstance(suggestion, str):  # Ensure it's a string
                                skill_improvements["specific"].append(f"**{skill_name}**: {suggestion}")
                    
                    if "example" in weakness and weakness["example"]:
                        resume_chunks = self.resume_text.split('\n\n')
                        relevant_chunk = ""
                        
                        for chunk in resume_chunks:
                            if skill_name.lower() in chunk.lower() or "experience" in chunk.lower():
                                relevant_chunk = chunk
                                break
                        
                        if relevant_chunk:
                            before_after_examples = {
                                "before": relevant_chunk.strip(),
                                "after": relevant_chunk.strip() + "\n• " + str(weakness["example"])
                            }
                
                if before_after_examples:
                    skill_improvements["before_after"] = before_after_examples
                
                improvements["Skills Highlighting"] = skill_improvements
            
            # Determine remaining areas that haven't been covered
            remaining_areas = [area for area in improvement_areas if area not in improvements]
            
            if remaining_areas:
                try:
                    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=self.api_key)
                    
                    # Safely build weaknesses_text
                    weaknesses_text = ""
                    if self.resume_weaknesses:
                        weaknesses_parts = []
                        for i, weakness in enumerate(self.resume_weaknesses):
                            part = f"{i+1}. {weakness.get('skill', '')}: {weakness.get('detail', '')}"
                            if "suggestions" in weakness:
                                suggestions = [f"   - {s}" for s in weakness["suggestions"]] if isinstance(weakness["suggestions"], list) else [f"   - {weakness['suggestions']}"]
                                part += "\n" + "\n".join(suggestions)
                            weaknesses_parts.append(part)
                        weaknesses_text = "Resume Weaknesses:\n" + "\n".join(weaknesses_parts)
                    
                    # Safely convert all list values to strings
                    def safe_join(items, sep=", "):
                        if items is None:
                            return ""
                        if isinstance(items, str):
                            return items
                        if isinstance(items, list):
                            return sep.join(str(item) for item in items)
                        return str(items)
                    
                    context = f"""
    Resume Content:
    {self.resume_text}
    
    Skills to focus on: {safe_join(self.extracted_skills)}
    
    Strengths: {safe_join(self.analysis_result.get('strengths', []))}
    
    Areas for improvement: {safe_join(self.analysis_result.get('missing_skills', []))}
    
    {weaknesses_text}
    
    Target role: {target_role if target_role else "Not specified"}
    """
                    prompt = f"""
    Provide detailed suggestions to improve this resume in the following areas: {', '.join(remaining_areas)}.
    
    {context}
    
    For each improvement area, provide:
    1. A general description of what needs improvement
    2. 3-5 specific actionable suggestions
    3. Where relevant, provide a before/after example
    
    Format the response as a JSON object with improvement areas as keys, each containing:
    - "description": general description
    - "specific": list of specific suggestions
    - "before_after": (where applicable) a dict with "before" and "after" examples
    
    Only include the requested improvement areas that aren't already covered.
    Focus particularly on addressing the resume weaknesses identified.
    """
                    
                    response = llm.invoke(prompt)
                    
                    # Parse the response
                    ai_improvements = {}
                    if hasattr(response, 'content'):
                        content = response.content
                        # Try to find JSON in the response
                        json_match = re.search(r'```(?:json)?\s*({[\s\S]+?})\s*```', content)
                        if json_match:
                            try:
                                ai_improvements = json.loads(json_match.group(1))
                            except json.JSONDecodeError as e:
                                print(f"Error parsing JSON response: {e}")
                                # Fall back to text parsing
                                ai_improvements = self._parse_improvement_text(content, remaining_areas)
                        else:
                            ai_improvements = self._parse_improvement_text(content, remaining_areas)
                    
                    # Merge improvements
                    improvements.update(ai_improvements)
                    
                except Exception as e:
                    print(f"Error during LLM processing: {e}")
                    # Fallback for each remaining area
                    for area in remaining_areas:
                        improvements[area] = {
                            "description": f"Could not generate suggestions for {area} due to an error",
                            "specific": ["Please try again later or provide more specific feedback"]
                        }
            
            return improvements
        
        except Exception as e:
            print(f"Error in improve_resume: {str(e)}")
            return {area: {"description": "Error generating suggestions", "specific": ["An error occurred while processing your request"]} for area in improvement_areas}

    def _parse_improvement_text(self, text, areas):
        """Helper to parse improvement text when JSON parsing fails"""
        improvements = {}
        current_area = None
        
        # Try to find each area in the text
        for area in areas:
            if area.lower() in text.lower():
                improvements[area] = {
                    "description": "",
                    "specific": []
                }
                current_area = area
        
        # If we couldn't find structured areas, just return generic improvements
        if not improvements:
            for area in areas:
                improvements[area] = {
                    "description": f"General improvements suggested for {area}",
                    "specific": ["Review and enhance this section based on your experience"]
                }
        
        return improvements

    def get_improved_resume(self, target_role="", highlight_skills=""):
        """Generate an improved version of the resume optimized for the job description"""
        if not self.resume_text:
            return "Please upload and analyze a resume first."
        
        try:
            # Parse highlight skills if provided
            skills_to_highlight = []
            if highlight_skills:
                if len(highlight_skills) > 100: 
                    self.jd_text = highlight_skills
                    try:
                        parsed_skills = self.extract_skills_from_jd(highlight_skills)
                        if parsed_skills:
                            skills_to_highlight = parsed_skills
                        else:
                            skills_to_highlight = [s.strip() for s in highlight_skills.split(",") if s.strip()]
                    except:
                        skills_to_highlight = [s.strip() for s in highlight_skills.split(",") if s.strip()]
                else:
                    skills_to_highlight = [s.strip() for s in highlight_skills.split(",") if s.strip()]
            
            if not skills_to_highlight and self.analysis_result:
                skills_to_highlight = self.analysis_result.get('missing_skills', [])
                skills_to_highlight.extend([skill for skill in self.analysis_result.get('strengths', []) if skill not in skills_to_highlight])

                if self.extracted_skills:
                    skills_to_highlight.extend([skill for skill in self.extracted_skills if skill not in skills_to_highlight])

            weakness_context = ""
            improvement_examples = ""
            
            if self.resume_weaknesses:
                weakness_context = "Address these specific weaknesses:\n"
                for weakness in self.resume_weaknesses:
                    skill_name = weakness.get('skill', '')
                    weakness_context += f"- {skill_name}: {weakness.get('detail', '')}\n"
                    
                    if 'suggestions' in weakness and weakness['suggestions']:
                        weakness_context += "  Suggested improvements:\n"
                        for suggestion in weakness['suggestions']:
                            weakness_context += f"  * {suggestion}\n"
            
                    if 'example' in weakness and weakness['example']:
                        improvement_examples += f"For {skill_name}: {weakness['example']}\n\n"
            
            # Use Groq for generating the improved resume
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=self.api_key)  # Updated to Groq
            
            jd_context = ""
            if self.jd_text:
                jd_context = f"Job Description:\n{self.jd_text}\n\n"
            elif target_role:
                jd_context = f"Target Role: {target_role}\n\n"
            
            prompt = f"""
            Rewrite and improve this resume to make it highly optimized for the target job.
            
            {jd_context}
            Original Resume:
            {self.resume_text}
            
            Skills to highlight (in order of priority): {', '.join(skills_to_highlight)}
            
            {weakness_context}
            
            Here are specific examples of content to add:
            {improvement_examples}
            
            Please improve the resume by:
            1. Adding strong, quantifiable achievements
            2. Highlighting the specified skills strategically for ATS scanning
            3. Addressing all the weakness areas identified with the specific suggestions provided
            4. Incorporating the example improvements provided above
            5. Structuring information in a clear, professional format
            6. Using industry-standard terminology
            7. Ensuring all relevant experience is properly emphasized
            8. Adding measurable outcomes and achievements
            
            Return only the improved resume text without any additional explanations.
            Format the resume in a modern, clean style with clear section headings.
            """
            
            response = llm.invoke(prompt)
            improved_resume = response.content.strip()
            
            # Save the improved resume to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tmp:
                tmp.write(improved_resume)
                self.improved_resume_path = tmp.name
            
            return improved_resume
        
        except Exception as e:
            print(f"Error generating improved resume: {e}")
            return "Error generating improved resume. Please try again."

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if hasattr(self, 'resume_file_path') and os.path.exists(self.resume_file_path):
                os.unlink(self.resume_file_path)
            
            if hasattr(self, 'improved_resume_path') and os.path.exists(self.improved_resume_path):
                os.unlink(self.improved_resume_path)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")