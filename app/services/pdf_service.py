"""DocGen AI - PDF generation service (lightweight, no system dependencies)"""
import io


class PDFService:
    """Service for PDF generation.
    
    Uses client-side browser print-to-PDF via window.print().
    The HTML is already professionally styled for print output.
    This avoids needing GTK/Pango system libraries on Windows.
    """

    def generate_printable_html(self, html_content: str) -> str:
        """Add print-optimized styles to HTML for browser print-to-PDF."""
        print_styles = """
        <style media="print">
            @page { margin: 1cm; size: A4; }
            body { font-size: 12pt; }
            .no-print { display: none !important; }
        </style>
        """
        # Inject print styles before </head>
        if "</head>" in html_content:
            return html_content.replace("</head>", f"{print_styles}</head>")
        return f"{print_styles}{html_content}"


# Singleton instance
pdf_service = PDFService()
