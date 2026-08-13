import os
import re
from reportlab.lib.pagesizes import letter # 8.5 x 11 inches = 612 x 792 points
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage

# Paths
desktop_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final"
images_dir = os.path.join(desktop_dir, "01_Final_Book_Assets")
output_pdf = os.path.join(desktop_dir, "02_Publishing_Files", "The_Jordan_Pride_Book_1_Print_Interior.pdf")

# Page Dimensions (8.5 x 11 inches)
PAGE_WIDTH, PAGE_HEIGHT = letter # 612 x 792 points

def create_interior_pdf():
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=36,  # 0.5 in
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'BookTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor('#4A2E10'),
        alignment=1, # Center
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'BookSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=16,
        leading=22,
        textColor=colors.HexColor('#8C5A2B'),
        alignment=1,
        spaceAfter=25
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=26,
        textColor=colors.HexColor('#4A2E10'),
        alignment=1,
        spaceAfter=15
    )

    body_style = ParagraphStyle(
        'StoryText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=20,
        textColor=colors.HexColor('#2C1D11'),
        alignment=0, # Left
        spaceAfter=10
    )

    creed_style = ParagraphStyle(
        'CreedText',
        parent=styles['Normal'],
        fontName='Helvetica-BoldOblique',
        fontSize=15,
        leading=22,
        textColor=colors.HexColor('#9E2A2B'),
        alignment=1,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#555555'),
        alignment=1
    )

    # Custom Front Matter Styles for Jordan Pride Standard
    half_title_style = ParagraphStyle(
        'HalfTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#4A2E10'),
        alignment=1,
        spaceAfter=15
    )

    book_honesty_style = ParagraphStyle(
        'BookHonesty',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#8C5A2B'),
        alignment=1,
        spaceBefore=15
    )

    page2_dedication_style = ParagraphStyle(
        'Page2Dedication',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4A2E10'),
        alignment=1, # Center
        spaceAfter=15
    )

    page2_pub_note_style = ParagraphStyle(
        'Page2PubNote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#666666'),
        alignment=1, # Center
        spaceAfter=20
    )

    page2_copyright_style = ParagraphStyle(
        'Page2Copyright',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#555555'),
        alignment=1 # Center
    )

    story = []

    def get_image_path(filename):
        path = os.path.join(images_dir, filename)
        return path if os.path.exists(path) else None

    # Helper to split or scale spread image for a page
    def create_page_image(image_filename, side='full'):
        img_path = get_image_path(image_filename)
        if not img_path:
            return None
        
        # If it's a spread (17x11) and we want left or right half
        if side in ['left', 'right']:
            crop_path = os.path.join(images_dir, f"temp_{side}_{image_filename}")
            try:
                with PILImage.open(img_path) as im:
                    w, h = im.size
                    if side == 'left':
                        box = (0, 0, w // 2, h)
                    else:
                        box = (w // 2, 0, w, h)
                    cropped = im.crop(box)
                    cropped.save(crop_path)
                    return crop_path
            except Exception as e:
                print(f"Error cropping image {image_filename}: {e}")
                return img_path
        return img_path

    # --- PAGE 1: HALF-TITLE PAGE (The Jordan Pride Family Values Series) ---
    img1 = get_image_path("Page_01.png")
    if img1:
        story.append(Image(img1, width=7.2*inch, height=9.3*inch))
    story.append(PageBreak())

    # --- PAGE 2: COPYRIGHT & IMPRINT PAGE ---
    img2 = get_image_path("Page_02.png")
    if img2:
        story.append(Image(img2, width=7.2*inch, height=5.06*inch))
        story.append(Spacer(1, 15))
        story.append(Paragraph("Dedicated to every brave young cub<br/>learning to walk in courage, honor, and truth.", page2_dedication_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Publisher Note:</b> The Jordan Pride series is dedicated to equipping families with foundational virtues through courageous storytelling, helping children discover that honesty, integrity, and family trust create true strength.", page2_pub_note_style))
        story.append(Spacer(1, 25))
        story.append(Paragraph("Copyright © 2026 Jay Jay. All Rights Reserved. Series TM.", page2_copyright_style))
    story.append(PageBreak())

    # --- PAGE 3: FULL TITLE PAGE & DEDICATION ---
    img3 = get_image_path("Page_03.png")
    if img3:
        story.append(Image(img3, width=7.2*inch, height=9.3*inch))
    story.append(PageBreak())

    # --- MAIN STORY MANUSCRIPT (PAGES 4–27 / SPREADS 1–12) ---
    story_pages = [
        # (Page_num, Image_file, Spread_side, [Text_lines])
        (4, "Page_04.png", "left", [
            "In the sunny heart of Pride Valley, Leo loved showing off how fast and high he could jump."
        ]),
        (5, "Page_04.png", "right", [
            "\"Watch this, Maya! I'm the strongest pouncer in the whole pride!\" Leo cheered as he took a huge leap.",
            "CRACK! He landed with a heavy thump right on Pop Pop's carved wooden garden marker!"
        ]),
        (6, "Page_05.png", "left", [
            "The smooth oak post snapped cleanly in two.",
            "Leo gasped and scrambled backward, his amber eyes wide in shock."
        ]),
        (7, "Page_05.png", "right", [
            "Maya rushed over, clutching Glimmer tight.",
            "\"Oh no, Leo! Pop Pop’s special flower marker!\" she whispered."
        ]),
        (8, "Page_06.png", "left", [
            "Leo's heart pounded like a drum.",
            "A cold, heavy feeling churned inside his belly—a twisty tummy!"
        ]),
        (9, "Page_06.png", "right", [
            "\"Maybe we can hide the pieces under the leaves,\" Leo panicked.",
            "Maya shook her head. \"Stories won't fix a twisty tummy.\""
        ]),
        (10, "Page_07.png", "left", [
            "Maya placed a comforting paw on his arm.",
            "\"Making a mistake is scary, Leo. But telling the truth is the bravest choice of all.\""
        ]),
        (11, "Page_07.png", "right", [
            "Just then, heavy footsteps crunched on the gravel path.",
            "Pop Pop stopped in his tracks, looking down at the broken marker in the grass."
        ]),
        (12, "Page_08.png", "left", [
            "Pop Pop looked at the splintered wood, then turned to the cubs.",
            "His amber eyes were calm and patient. \"What happened here, young cubs?\""
        ]),
        (13, "Page_08.png", "right", [
            "Leo felt his legs shake. He wanted to lie, but he remembered who he was.",
            "He placed his paw firmly over his heart."
        ]),
        (14, "Page_09.png", "left", [
            "\"It was me, Pop Pop,\" Leo confessed clearly. \"I was jumping and landed right on it. I'm so sorry.\""
        ]),
        (15, "Page_09.png", "right", [
            "Pop Pop smiled warmly and pulled Leo into a giant, cozy bear hug.",
            "\"Thank you for telling me the truth, Leo. That took real lion bravery.\""
        ]),
        (16, "Page_10.png", "left", [
            "Pop Pop held up the broken wooden pieces.",
            "\"A marker can always be glued, but family trust is much harder to fix. Today, you chose honor.\""
        ]),
        (17, "Page_10.png", "right", [
            "Maya cheered and jumped up and down!",
            "\"You were so brave, Leo! Telling the truth makes you the strongest cub in the pride!\""
        ]),
        (18, "Page_11.png", "left", [
            "Pop Pop brought them to his workbench.",
            "Together, they carefully applied wood glue, set the clamp, and fixed the broken marker."
        ]),
        (19, "Page_11.png", "right", [
            "Mom and Dad walked in and smiled.",
            "\"Honesty is our family's foundation,\" Dad said, placing a proud paw on Leo's shoulder."
        ]),
        (20, "Page_12.png", "left", [
            "Once the glue dried, they walked out to the garden.",
            "Leo proudly placed the handcrafted marker back beside Pop Pop's blooming marigolds."
        ]),
        (21, "Page_12.png", "right", [
            "Pop Pop gathered the cubs close under the shade of the grand, sprawling acacia tree."
        ]),
        (22, "Page_13.png", "left", [
            "\"Always remember our family way,\" Pop Pop said proudly, winking with gentle wisdom."
        ]),
        (23, "Page_13.png", "right", [
            "Leo and Maya stood up together, placed their paws firmly over their hearts, and recited the creed:"
        ]),
        (24, "Page_14.png", "left", [
            "\"ONLY weak lions lie. The Jordan Pride is Fearless and Strong. Therefore, we are always honest and true!\""
        ]),
        (25, "Page_14.png", "right", [
            "Leo smiled brightly. The twisty feeling in his stomach was completely gone, replaced by a warm sense of pride."
        ]),
        (26, "Page_15.png", "left", [
            "Whenever you make a mistake, remember Leo's story.",
            "Stand tall, take a deep breath, and let honesty show your true strength!"
        ]),
        (27, "Page_15.png", "right", [
            "Because when you tell the truth, family trust stays unbroken, and your heart stays bright and free!",
            "The Jordan Pride is always honest and true—and so are you!"
        ])
    ]

    for p_num, img_file, side, lines in story_pages:
        img_p = create_page_image(img_file, side)
        story.append(Paragraph(f"<b>PAGE {p_num}</b>", ParagraphStyle('PageNumHeader', parent=meta_style, alignment=2)))
        story.append(Spacer(1, 5))
        
        if img_p:
            story.append(Image(img_p, width=7*inch, height=4.5*inch))
            story.append(Spacer(1, 15))
        else:
            # Placeholder Box
            story.append(Table([
                [Paragraph(f"<b>[ Illustration Spread Image: {img_file} ({side.upper()} half) ]</b>", ParagraphStyle('PlaceH', parent=meta_style, textColor=colors.HexColor('#888888')))]
            ], colWidths=[7*inch], rowHeights=[4.2*inch], style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F5EE')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#D0C8B8'))
            ])))
            story.append(Spacer(1, 15))
            
        for l in lines:
            if "ONLY weak lions lie" in l:
                story.append(Paragraph(l, creed_style))
            else:
                story.append(Paragraph(l, body_style))
                
        story.append(PageBreak())

    # --- BACK MATTER (PAGES 28–32) ---
    
    # Page 28: Creed
    story.append(Paragraph("THE JORDAN PRIDE FAMILY CREED", heading_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("\"ONLY weak lions lie.<br/>The Jordan Pride is Fearless and Strong.<br/>Therefore, we are always honest and true.\"", creed_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>Core Family Pillars:</b>", ParagraphStyle('PillarsH', parent=body_style, fontName='Helvetica-Bold')))
    story.append(Paragraph("• <b>Truth Builds Trust:</b> Honesty is the foundation of every strong family.", body_style))
    story.append(Paragraph("• <b>Courage Over Fear:</b> Speaking the truth takes real lion bravery.", body_style))
    story.append(Paragraph("• <b>Taking Responsibility:</b> Fixing mistakes together makes us stronger.", body_style))
    story.append(Paragraph("• <b>Unconditional Family Love:</b> No matter what happens, family love protects us.", body_style))
    story.append(PageBreak())

    # Page 29: Discussion Corner
    story.append(Paragraph("DISCUSSION CORNER", heading_style))
    story.append(Paragraph("<i>Parent & Child Reflection Questions</i>", subtitle_style))
    story.append(Spacer(1, 10))
    questions = [
        ("1. The 'Twisty Tummy' Feeling:", "Have you ever felt a 'twisty tummy' after breaking something or making a mistake? What is that feeling trying to tell you?"),
        ("2. Bravery in Truth:", "Why did it take MORE bravery for Leo to tell Pop Pop the truth than to make up an excuse about the wind?"),
        ("3. Mending vs. Hiding:", "How did Pop Pop help Leo fix the wooden marker after Leo told the truth? What happens when we try to hide mistakes?"),
        ("4. Family Trust:", "Why is telling the truth so important inside a family? How does honesty make your family stronger?")
    ]
    for q_title, q_body in questions:
        story.append(Paragraph(f"<b>{q_title}</b>", ParagraphStyle('QT', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#4A2E10'))))
        story.append(Paragraph(q_body, body_style))
        story.append(Spacer(1, 8))
    story.append(PageBreak())

    # Page 30: Honor Code Checklist
    story.append(Paragraph("HONOR CODE CHECKLIST", heading_style))
    story.append(Spacer(1, 15))
    checklist = [
        "When I make an accidental mess or break something, I tell an adult right away.",
        "I place my paw over my heart, take a deep breath, and speak the truth.",
        "I choose honesty even when I am afraid of getting in trouble.",
        "I help fix my mistakes by offering to clean up, repair, or apologize.",
        "I remember that my family loves me and that honesty keeps our trust unbroken!"
    ]
    for item in checklist:
        story.append(Paragraph(f"[  ] {item}", ParagraphStyle('CL', parent=body_style, fontSize=13, leading=18, spaceAfter=12)))
    story.append(PageBreak())

    # Page 31: Character Roster
    story.append(Paragraph("MEET THE JORDAN PRIDE", heading_style))
    story.append(Spacer(1, 15))
    roster = [
        ("Leo Jordan", "6yo Boy Cub — Full of energy and heart. Learning that true bravery comes from honesty."),
        ("Maya Jordan", "3yo Girl Cub — Wise, caring little sister who helps Leo make the right choice."),
        ("Pop Pop Jordan", "Grandfather — Family anchor and master woodworker who leads with love and wisdom."),
        ("Mom & Dad Jordan", "Parents — Nurturing guides who teach integrity and support their cubs through every lesson.")
    ]
    for name, desc in roster:
        story.append(Paragraph(f"<b>{name}</b>", ParagraphStyle('RN', parent=body_style, fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#4A2E10'))))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 10))
    story.append(PageBreak())

    # Page 32: Teaser & Back Page
    story.append(Paragraph("COMING NEXT IN BOOK 2", heading_style))
    story.append(Paragraph("<b>The Jordan Pride — Book 2: The Great Community Fair</b>", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Learn about Politeness, Respect, and Good Manners as Leo and Maya explore the vibrant Pride Valley Fair!", body_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>About The Jordan Pride Series</b>", ParagraphStyle('AbH', parent=body_style, fontName='Helvetica-Bold', fontSize=14)))
    story.append(Paragraph("The Jordan Pride series equips young children with timeless character virtues through engaging, heartwarming stories. Designed for family read-alouds and early readers ages 3–7.", body_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Published by The Jordan Pride Family Publishing<br/>www.thejordanpride.com", meta_style))

    doc.build(story)
    print(f"Successfully generated 32-page interior PDF: {output_pdf}")

if __name__ == "__main__":
    create_interior_pdf()
