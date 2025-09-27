#!/usr/bin/env python3
"""
Create a test PDF for InvestiCAT processor testing.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    """Create a test PDF with investigative content."""
    pdf_path = "C:/Users/sheli/OneDrive/Desktop/test_investigation.pdf"
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "CORPORATE MERGER INVESTIGATION")
    
    # Content
    c.setFont("Helvetica", 12)
    y = height - 100
    
    content = [
        "TIMELINE OF EVENTS:",
        "",
        "January 15, 2024: MegaCorp Inc. announced acquisition of TechStart Ltd",
        "for $1.2 billion. The deal was negotiated by CEO Sarah Johnson and",
        "investment banker Michael Rodriguez from Goldman Sachs.",
        "",
        "February 28, 2024: Regulatory approval obtained from the Federal Trade",
        "Commission after extensive review. The approval meeting took place at",
        "FTC headquarters in Washington, D.C.",
        "",
        "March 10, 2024: Shareholders of both companies voted to approve the",
        "merger at respective annual meetings. MegaCorp meeting was held in",
        "San Francisco, California, while TechStart met in Austin, Texas.",
        "",
        "April 5, 2024: Transaction officially completed with signing ceremony",
        "at MegaCorp headquarters in Palo Alto, California. Key attendees included:",
        "- Sarah Johnson, CEO of MegaCorp Inc.",
        "- David Chen, Founder of TechStart Ltd",
        "- Lisa Martinez, CFO of MegaCorp",
        "- Robert Kim, Legal Counsel",
        "",
        "The deal creates a technology giant valued at over $15 billion,",
        "positioning the combined entity as a major player in the AI sector.",
    ]
    
    for line in content:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    return pdf_path

if __name__ == "__main__":
    try:
        path = create_test_pdf()
        print(f"✅ Test PDF created: {path}")
    except ImportError:
        print("❌ reportlab not installed. Install with: pip install reportlab")
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")