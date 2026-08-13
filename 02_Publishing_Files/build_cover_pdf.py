import os
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage

desktop_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final"
images_dir = os.path.join(desktop_dir, "01_Final_Book_Assets")
output_pdf = os.path.join(desktop_dir, "02_Publishing_Files", "The_Jordan_Pride_Book_1_Print_Cover_Wrap.pdf")

# Full Cover Wrap Dimensions (17.25 x 11.25 inches with 0.125 bleed)
COVER_WIDTH = 17.25 * 72 # 1242 pt
COVER_HEIGHT = 11.25 * 72 # 810 pt

def create_cover_pdf():
    cover_img_path = os.path.join(images_dir, "Cover_Wrap.png")
    if not os.path.exists(cover_img_path):
        print(f"Error: Cover image not found at {cover_img_path}")
        return

    c = canvas.Canvas(output_pdf, pagesize=(COVER_WIDTH, COVER_HEIGHT))
    
    # Draw cover image filling full canvas
    c.drawImage(cover_img_path, 0, 0, width=COVER_WIDTH, height=COVER_HEIGHT)
    
    # Save PDF
    c.save()
    print(f"Successfully generated Full Cover Wrap PDF: {output_pdf}")

if __name__ == "__main__":
    create_cover_pdf()
