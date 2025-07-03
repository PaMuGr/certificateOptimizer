from agno.agent import Agent
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import markdown
from bs4 import BeautifulSoup
import re
from datetime import datetime

class ResumeOptimizer(Agent):
    def __init__(self):
        super().__init__(name="ResumeOptimizer", description="Optimizes resumes for job descriptions")

    def run(self, resume: str, job_description: str, output_format: str = "text") -> str:
        """
        Generate optimized resume in specified format.
        
        Args:
            resume: Original resume text
            job_description: Job description to optimize for
            output_format: "text" or "pdf"
        
        Returns:
            If text: optimized resume as string
            If pdf: file path to generated PDF
        """
        message = f"""You are an expert resume writer. Rewrite the following resume to match the job description.

**Instructions:**
- Use strong action verbs and job-specific keywords.
- Focus on relevance (cut non-matching roles).
- Return resume in clean Markdown format (max one page).
- Add a section at the end titled "Additional Suggestions" with:
  - Extra skills to learn
  - Certifications to pursue
  - Project ideas

**Resume:**
{resume}

**Job Description:**
{job_description}"""

        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": message}
            ]
        )

        optimized_resume = response.content[0].text.strip()
        
        if output_format == "pdf":
            return self._generate_pdf(optimized_resume)
        else:
            return optimized_resume

    def _generate_pdf(self, markdown_text: str) -> str:
        """Convert markdown resume to PDF and return file path."""
        # Create output directory if it doesn't exist
        output_dir = "generated_resumes"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimized_resume_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.darkblue
        )
        
        # Parse markdown and convert to PDF elements
        self._parse_markdown_to_pdf(markdown_text, elements, styles, title_style, heading_style)
        
        # Build PDF
        doc.build(elements)
        
        return filepath

    def _parse_markdown_to_pdf(self, markdown_text: str, elements: list, styles, title_style, heading_style):
        """Parse markdown text and convert to PDF elements."""
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 12))
                continue
                
            # Handle headers
            if line.startswith('# '):
                # Main title
                title_text = line[2:].strip()
                elements.append(Paragraph(title_text, title_style))
                elements.append(Spacer(1, 12))
                
            elif line.startswith('## '):
                # Section headers
                header_text = line[3:].strip()
                elements.append(Paragraph(header_text, heading_style))
                
            elif line.startswith('### '):
                # Subsection headers
                subheader_text = line[4:].strip()
                elements.append(Paragraph(f"<b>{subheader_text}</b>", styles['Normal']))
                
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet points
                bullet_text = line[2:].strip()
                elements.append(Paragraph(f"• {bullet_text}", styles['Normal']))
                
            elif line.startswith('**') and line.endswith('**'):
                # Bold text (job titles, etc.)
                bold_text = line[2:-2].strip()
                elements.append(Paragraph(f"<b>{bold_text}</b>", styles['Normal']))
                
            else:
                # Regular text
                if line:
                    # Handle basic markdown formatting
                    formatted_line = self._format_markdown_inline(line)
                    elements.append(Paragraph(formatted_line, styles['Normal']))

        elements.append(Spacer(1, 12))

    def _format_markdown_inline(self, text: str) -> str:
        """Format inline markdown elements like bold, italic, etc."""
        # Bold text
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Italic text
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Email and phone formatting
        text = re.sub(r'(\S+@\S+\.\S+)', r'<u>\1</u>', text)
        text = re.sub(r'(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})', r'<u>\1</u>', text)
        
        return text