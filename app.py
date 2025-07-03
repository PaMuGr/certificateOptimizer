import streamlit as st
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import tempfile
import os
from datetime import datetime
import re
from dotenv import load_dotenv
from anthropic import Anthropic

#Cargar clave desde .env
load_dotenv()
anthropic = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

#Clase optimizadora de CV
class ResumeOptimizer:
    def __init__(self):
        pass

    def run(self, resume: str, job_description: str) -> str:
        prompt = f"""You are an expert resume writer. Rewrite the following resume to match the job description.

**Instructions:**
- Use strong action verbs and job-specific keywords.
- Focus on relevance (cut non-matching roles).
- Return resume in clean Markdown format (max one page).
- Add a section at the end titled "## Sugerencias adicionales" with:
  - Extra skills to learn
  - Certifications to pursue
  - Project ideas

**Resume:**
{resume}

**Job Description:**
{job_description}
"""

        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()


def format_markdown_inline(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(\S+@\S+\.\S+)', r'<u>\1</u>', text)
    text = re.sub(r'(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})', r'<u>\1</u>', text)
    return text

def generate_pdf(markdown_text: str) -> bytes:
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        doc = SimpleDocTemplate(tmp_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )

        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=8,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.black,
            fontName='Helvetica'
        )

        lines = markdown_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 8))
                continue

            if line.startswith('# '):
                elements.append(Paragraph(line[2:].strip(), title_style))
                elements.append(Spacer(1, 12))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:].strip(), heading_style))
                elements.append(Spacer(1, 6))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:].strip(), subheading_style))
            elif line.startswith('- ') or line.startswith('* '):
                bullet = format_markdown_inline(line[2:].strip())
                elements.append(Paragraph(f"• {bullet}", normal_style))
            elif line.startswith('**') and line.endswith('**'):
                elements.append(Paragraph(f"<b>{line[2:-2].strip()}</b>", normal_style))
            else:
                elements.append(Paragraph(format_markdown_inline(line), normal_style))

        doc.build(elements)

        with open(tmp_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

#Streamlit UI
st.set_page_config(page_title="Optimizador de Currículum 🇪🇸", layout="centered")
st.title("📄 Optimizador de CV con IA para el mercado laboral español")
st.markdown("Sube tu currículum y pega la descripción del trabajo para obtener una versión personalizada y optimizada para ATS.")

agent = ResumeOptimizer()

pdf = st.file_uploader("Sube tu currículum (PDF)", type=["pdf"])
jd = st.text_area("Pegue la descripción del trabajo aquí", height=250)

if st.button("🚀 Optimizar mi currículum"):
    if not pdf or not jd:
        st.warning("Por favor, sube un currículum y pega una descripción del trabajo.")
    else:
        with st.spinner("Extrayendo texto del currículum..."):
            reader = PdfReader(pdf)
            resume_text = "\n".join([page.extract_text() for page in reader.pages])

        with st.spinner("Hablando con Claude..."):
            result = agent.run(resume_text, jd)

        parts = result.split("## Sugerencias adicionales", maxsplit=1)
        resume_md = parts[0].strip()
        suggestions_md = "## Sugerencias adicionales\n" + parts[1].strip() if len(parts) > 1 else "No se devolvieron sugerencias."

        st.markdown("### ✅ Currículum optimizado")
        st.markdown(resume_md)

        st.markdown("---")
        st.markdown("### 🛠 Sugerencias adicionales")
        st.markdown(suggestions_md)

        st.markdown("---")
        st.markdown("### 📥 Descargar resultados")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📝 Descargar como Markdown",
                data=result,
                file_name=f"curriculum_optimizado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )

        with col2:
            with st.spinner("Generando PDF..."):
                try:
                    pdf_bytes = generate_pdf(resume_md)
                    st.download_button(
                        label="📄 Descargar como PDF",
                        data=pdf_bytes,
                        file_name=f"curriculum_optimizado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generando PDF: {str(e)}")
                    st.info("Puedes usar el botón de Markdown como alternativa.")

        st.success("¡Optimización del currículum completada!")

st.markdown("---")
st.markdown("### 💡 Consejos")
st.markdown("""
- **Formato Markdown**: Fácil de editar y personalizar  
- **Formato PDF**: Listo para enviar a empleadores  
- **Optimización ATS**: El contenido está optimizado para sistemas de seguimiento de candidatos  
- **Palabras clave**: Se incluyen términos relevantes de la descripción del trabajo  
""")

st.markdown("---")
st.markdown("*Powered by Claude AI - Optimiza tu currículum para el mercado laboral español 🇪🇸*")
