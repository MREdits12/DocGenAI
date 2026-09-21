"""DocGen AI - AI Generation Service using Google Gemini"""
import google.generativeai as genai
from app.config import get_settings
from app.models import DocumentType

# Prompt templates for each document type
PROMPTS = {
    DocumentType.PROPOSAL: """You are a professional business proposal writer. 
Generate a polished, compelling business proposal based on the following information.

The output MUST be valid HTML that can be rendered in a browser and converted to PDF.
Use professional formatting with these HTML elements:
- <h1> for the main title
- <h2> for section headers  
- <h3> for subsections
- <p> for body text
- <ul>/<li> for bullet lists
- <table> with <thead>/<tbody> for any data tables
- <strong> and <em> for emphasis

Include these sections:
1. Cover page with title, client name, date, and your company name
2. Executive Summary
3. Problem Statement / Client Needs
4. Proposed Solution
5. Scope of Work (with deliverables)
6. Timeline / Milestones
7. Pricing / Investment
8. Why Choose Us
9. Terms & Conditions (brief)
10. Next Steps / Call to Action

Make the language professional, persuasive, and specific to the details provided.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",
    DocumentType.INVOICE: """You are a professional invoice generator.
Generate a clean, professional invoice based on the following information.

The output MUST be valid HTML that can be rendered in a browser and converted to PDF.
Use professional formatting:
- Clean header with company info and logo placeholder
- Invoice number, date, due date
- Bill To / Ship To sections
- Line items table with description, quantity, rate, amount
- Subtotal, tax, total
- Payment terms and methods
- Footer with thank you note

Use <table> elements for the line items. Make it look like a real business invoice.
Calculate totals based on the provided information.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",
    DocumentType.REPORT: """You are a professional business report writer.
Generate a comprehensive, well-structured business report based on the following information.

The output MUST be valid HTML that can be rendered in a browser and converted to PDF.
Use professional formatting with clear headings, data tables, and organized sections.

Include these sections as appropriate:
1. Title Page
2. Executive Summary
3. Introduction / Background
4. Methodology (if applicable)
5. Findings / Analysis
6. Data & Metrics (use tables and lists)
7. Key Insights
8. Recommendations
9. Conclusion
10. Appendix (if needed)

Make the language clear, data-driven, and actionable.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",
    DocumentType.SOP: """You are a professional Standard Operating Procedure (SOP) writer.
Generate a clear, step-by-step SOP document based on the following information.

The output MUST be valid HTML that can be rendered in a browser and converted to PDF.
Use professional formatting with numbered steps, checklists, and clear sections.

Include these sections:
1. Document Header (title, version, effective date, department)
2. Purpose
3. Scope
4. Responsibilities
5. Definitions (if needed)
6. Procedure (numbered steps with sub-steps)
7. Safety / Compliance Notes
8. References
9. Revision History table

Use <ol> for numbered steps and <ul> for sub-items. Include a checklist format where appropriate.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",
    DocumentType.CONTRACT: """You are a professional contract/agreement writer.
Generate a professional service agreement or contract based on the following information.

The output MUST be valid HTML that can be rendered in a browser and converted to PDF.

Include these sections:
1. Agreement Header (parties, effective date)
2. Recitals / Background
3. Definitions
4. Scope of Services
5. Compensation & Payment Terms
6. Term & Termination
7. Confidentiality
8. Intellectual Property
9. Limitation of Liability
10. General Provisions
11. Signature Block

Use formal legal language but keep it readable. Include placeholder signature lines.
Add a disclaimer: "This is an AI-generated template. Consult a legal professional before use."
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",

    DocumentType.SOCIAL_MEDIA: """You are an expert Social Media Manager.
Create highly engaging social media posts based on the provided topic.

The output MUST be valid HTML that can be rendered in a browser.

Please generate 3 different posts for 3 different platforms:
1. **LinkedIn Post**: Professional, insightful, well-structured with line breaks, using 2-3 relevant hashtags. Include a hook and a call to action.
2. **Twitter/X Thread**: A punchy, fast-paced thread (2-3 tweets). Use engaging formatting and a clear hook.
3. **Facebook/Instagram Post**: Casual, highly engaging, conversational tone. Use emojis naturally and include 4-5 hashtags.

Format the output cleanly using <h3> headers for each platform, and <p> for the post content.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",

    DocumentType.EMAIL: """You are a master copywriter specializing in Email Outreach and Communication.
Write a highly effective, professional email based on the provided details.

The output MUST be valid HTML.

Follow these guidelines:
- Include a strong, curiosity-inducing Subject Line at the top (formatted as <h3>).
- Keep the tone professional but conversational.
- State the purpose clearly and quickly.
- End with a clear Call to Action (CTA).
- Include placeholder brackets like [Name] where necessary.

Format with <p> tags and use <br> for spacing if needed.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",

    DocumentType.BLOG: """You are a world-class SEO content writer.
Write a well-researched, highly engaging blog post based on the provided topic.

The output MUST be valid HTML that can be rendered in a browser.

Include:
- An engaging, SEO-optimized H1 Title.
- A strong introduction that hooks the reader.
- Well-structured body paragraphs with H2 and H3 subheadings.
- Bullet points or numbered lists where appropriate for readability.
- A conclusion with a clear call to action.

Make sure the content flows naturally and provides real value to the reader.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",

    DocumentType.PRODUCT_DESC: """You are an expert E-commerce Copywriter.
Write a compelling, high-converting product description based on the provided details.

The output MUST be valid HTML.

Include:
- A catchy, benefit-driven product Title (H2).
- A 2-3 sentence introductory hook that sells the feeling/benefit.
- A bulleted list of 5 key Features & Benefits (use <ul> and <li>).
- A short closing paragraph overcoming objections or emphasizing quality.

Make the tone persuasive and exciting.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",

    DocumentType.YOUTUBE: """You are a highly successful YouTube Strategist and Script Writer.
Write an engaging YouTube video script based on the provided concept.

The output MUST be valid HTML.

Structure the script as follows:
1. **Title Ideas**: Provide 3 high-CTR title variations (H3).
2. **The Hook** (0:00 - 0:30): The critical first 30 seconds to retain viewers.
3. **The Intro**: Setting up the value proposition.
4. **Main Content / Body**: Organized in clear points or chapters.
5. **The Outro**: Call to action (Subscribe, watch next video).

Use bold text to indicate [ON-SCREEN TEXT] or [VISUAL/B-ROLL IDEAS].
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",

    DocumentType.AD_COPY: """You are an elite Digital Marketer and Media Buyer.
Write high-converting ad copy for Facebook and Google Ads based on the provided product/service.

The output MUST be valid HTML.

Generate two distinct sections:
<h3>Facebook / Instagram Ads</h3>
Provide 2 different ad variations:
1. **Story/Emotion Based**: Focus on the problem and how the product solves it.
2. **Direct/Punchy**: Straight to the point, offer-focused.
(Include Primary Text, Headline, and Call-to-Action for each).

<h3>Google Search Ads</h3>
Provide 3 variations of:
- Headline 1, Headline 2, Headline 3
- Description 1, Description 2

Format neatly using <p>, <ul>, and <strong> tags.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT:
{user_input}

ADDITIONAL CONTEXT:
{additional_context}""",

    DocumentType.REWRITE: """You are an expert editor and communication specialist.
Rewrite and improve the provided text based on the instructions in the additional context.

The output MUST be valid HTML.

If no specific tone is requested in the additional context, default to making the text more professional, concise, and clear.
Fix any grammatical errors, improve the flow, and enhance the vocabulary.

Format the output cleanly. Use paragraphs (<p>) and lists if the structure demands it.
Do NOT include ```html or ``` markers. Return ONLY the raw HTML content.

USER INPUT (Text to rewrite):
{user_input}

ADDITIONAL CONTEXT (Tone / Instructions):
{additional_context}""",
}

# CSS styling injected into all generated documents for professional look
DOCUMENT_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.7;
        color: #1a1a2e;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px;
        background: #ffffff;
    }
    
    h1 {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 8px;
        border-bottom: 3px solid #6c63ff;
        padding-bottom: 12px;
    }
    
    h2 {
        font-size: 20px;
        font-weight: 600;
        color: #2d2d5e;
        margin-top: 32px;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #e8e8f0;
    }
    
    h3 {
        font-size: 16px;
        font-weight: 600;
        color: #3d3d7e;
        margin-top: 20px;
        margin-bottom: 8px;
    }
    
    p {
        margin-bottom: 12px;
        font-size: 14px;
    }
    
    ul, ol {
        margin: 12px 0;
        padding-left: 24px;
    }
    
    li {
        margin-bottom: 6px;
        font-size: 14px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 13px;
    }
    
    thead {
        background: #6c63ff;
        color: white;
    }
    
    th {
        padding: 10px 14px;
        text-align: left;
        font-weight: 600;
    }
    
    td {
        padding: 10px 14px;
        border-bottom: 1px solid #e8e8f0;
    }
    
    tbody tr:nth-child(even) {
        background: #f8f8fc;
    }
    
    strong { font-weight: 600; }
    
    .cover-page {
        text-align: center;
        padding: 60px 0;
        margin-bottom: 40px;
        border-bottom: 2px solid #6c63ff;
    }
    
    .signature-line {
        border-top: 1px solid #333;
        width: 250px;
        margin-top: 40px;
        padding-top: 8px;
    }
    
    .disclaimer {
        margin-top: 40px;
        padding: 12px;
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        font-size: 12px;
        color: #856404;
    }
</style>
"""


class AIService:
    """Service for generating documents using Google Gemini."""

    def __init__(self):
        settings = get_settings()
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            
            # Auto-discover a supported model for this specific API Key
            best_model = "gemini-1.5-flash"
            try:
                available = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        name = m.name.replace('models/', '')
                        available.append(name)
                
                if available:
                    flash_models = [m for m in available if 'flash' in m]
                    pro_models = [m for m in available if 'pro' in m]
                    
                    if flash_models:
                        best_model = flash_models[0]
                    elif pro_models:
                        best_model = pro_models[0]
                    else:
                        best_model = available[0]
                        
                print(f"[OK] Auto-selected AI model: {best_model}")
            except Exception as e:
                print(f"[ERROR] Failed to auto-detect models: {e}")
                
            self.model = genai.GenerativeModel(best_model)
        else:
            self.model = None

    async def generate_document(
        self,
        document_type: DocumentType,
        user_input: str,
        additional_context: str | None = None,
    ) -> str:
        """Generate a professional document using AI."""
        if not self.model:
            return self._generate_demo_document(document_type, user_input)

        prompt_template = PROMPTS.get(document_type, PROMPTS[DocumentType.REPORT])
        prompt = prompt_template.format(
            user_input=user_input,
            additional_context=additional_context or "No additional context provided.",
        )

        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8000,
            ),
        )

        html_content = response.text.strip()

        if html_content.startswith("```html"):
            html_content = html_content[7:]
        if html_content.startswith("```"):
            html_content = html_content[3:]
        if html_content.endswith("```"):
            html_content = html_content[:-3]

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {DOCUMENT_CSS}
</head>
<body>
{html_content.strip()}
</body>
</html>"""

        return full_html

    def _generate_demo_document(
        self, document_type: DocumentType, user_input: str
    ) -> str:
        """Generate a demo document when no API key is set."""
        title = document_type.value.title()
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    {DOCUMENT_CSS}
</head>
<body>
    <div class="cover-page">
        <h1>{title}</h1>
        <p><em>Generated by DocGen AI</em></p>
    </div>
    
    <h2>Demo Document</h2>
    <p>This is a demo document generated without an AI API key. 
    To generate real professional documents, add your Google Gemini API key to the <code>.env</code> file.</p>
    
    <h2>Your Input</h2>
    <p>{user_input}</p>
    
    <h2>How It Works</h2>
    <ol>
        <li>Add your free Gemini API key to <code>.env</code></li>
        <li>Restart the server</li>
        <li>The AI will generate a full professional {title.lower()} based on your input</li>
    </ol>
</body>
</html>"""


# Singleton instance
ai_service = AIService()
