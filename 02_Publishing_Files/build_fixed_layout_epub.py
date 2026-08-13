import os
import zipfile
import shutil
from PIL import Image as PILImage

desktop_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final"
images_dir = os.path.join(desktop_dir, "01_Final_Book_Assets")
out_epub_path = os.path.join(desktop_dir, "02_Publishing_Files", "The_Jordan_Pride_Book_1_eBook_FixedLayout.epub")
backup_dir = os.path.join(desktop_dir, "02_Publishing_Files")
os.makedirs(backup_dir, exist_ok=True)

# Page width/height in px for fixed-layout viewport (8.5 x 11 ratio)
VIEWPORT_W = 850
VIEWPORT_H = 1100

def create_epub3_fixed_layout():
    build_dir = os.path.join(desktop_dir, "epub_build_temp")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        
    os.makedirs(os.path.join(build_dir, "META-INF"))
    os.makedirs(os.path.join(build_dir, "OEBPS", "Text"))
    os.makedirs(os.path.join(build_dir, "OEBPS", "Images"))
    os.makedirs(os.path.join(build_dir, "OEBPS", "Styles"))

    # 1. mimetype (MUST be uncompressed)
    with open(os.path.join(build_dir, "mimetype"), "w", encoding="utf-8") as f:
        f.write("application/epub+zip")

    # 2. META-INF/container.xml
    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
    with open(os.path.join(build_dir, "META-INF", "container.xml"), "w", encoding="utf-8") as f:
        f.write(container_xml)

    # 3. META-INF/com.apple.ibooks.display-options.xml (Apple Books Fixed-Layout)
    apple_opts = """<?xml version="1.0" encoding="UTF-8"?>
<display_options>
    <platform name="*">
        <option name="fixed-layout">true</option>
        <option name="open-to-spread">false</option>
        <option name="specified-fonts">true</option>
    </platform>
</display_options>"""
    with open(os.path.join(build_dir, "META-INF", "com.apple.ibooks.display-options.xml"), "w", encoding="utf-8") as f:
        f.write(apple_opts)

    # 4. CSS
    css_content = f"""@page {{
    margin: 0;
    padding: 0;
}}
html, body {{
    margin: 0;
    padding: 0;
    width: {VIEWPORT_W}px;
    height: {VIEWPORT_H}px;
    background-color: #FFFDF5;
}}
.page-container {{
    position: relative;
    width: {VIEWPORT_W}px;
    height: {VIEWPORT_H}px;
    overflow: hidden;
}}
.page-img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
}}
.story-text {{
    position: absolute;
    bottom: 40px;
    left: 40px;
    right: 40px;
    background: rgba(255, 253, 245, 0.92);
    padding: 20px 25px;
    border-radius: 12px;
    border: 2px solid #8C5A2B;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 22px;
    line-height: 1.4;
    color: #2C1D11;
    text-align: left;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}
.text-creed {{
    font-weight: bold;
    color: #9E2A2B;
    font-style: italic;
    text-align: center;
}}
"""
    with open(os.path.join(build_dir, "OEBPS", "Styles", "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

    # Copy images to OEBPS/Images
    img_files = {}
    
    # 1. Copy single pages
    single_pages = [1, 2, 3, 16, 17, 18, 19, 20]
    for i in single_pages:
        filename = f"Page_{i:02d}.png"
        src = os.path.join(images_dir, filename)
        if os.path.exists(src):
            dst = os.path.join(build_dir, "OEBPS", "Images", filename)
            shutil.copyfile(src, dst)
            img_files[filename] = f"Images/{filename}"
            
    # 2. Copy spread halves
    for i in range(4, 16):
        for side in ['left', 'right']:
            filename = f"temp_{side}_Page_{i:02d}.png"
            src = os.path.join(images_dir, filename)
            if os.path.exists(src):
                dst = os.path.join(build_dir, "OEBPS", "Images", filename)
                shutil.copyfile(src, dst)
                img_files[filename] = f"Images/{filename}"

    # Also copy Cover_Wrap
    cover_src = os.path.join(images_dir, "Cover_Wrap.png")
    if os.path.exists(cover_src):
        shutil.copyfile(cover_src, os.path.join(build_dir, "OEBPS", "Images", "Cover_Wrap.png"))

    # Define 32 Pages XHTML
    manifest_items = []
    spine_items = []

    # Manifest items for static files
    manifest_items.append('<item id="css" href="Styles/style.css" media-type="text/css"/>')
    manifest_items.append('<item id="nav" href="toc.xhtml" media-type="application/xhtml+xml" properties="nav"/>')

    for fn in os.listdir(os.path.join(build_dir, "OEBPS", "Images")):
        m_id = f"img_{fn.replace('.', '_')}"
        manifest_items.append(f'<item id="{m_id}" href="Images/{fn}" media-type="image/png"/>')

    # Page definition mapping
        page_content_map = [
        # (Page_Num, Image_File, Title, [Text_Paragraphs])
        (1, "Page_01.png", "Half-Title Page", []),
        (2, "Page_02.png", "Copyright Page", []),
        (3, "Page_03.png", "Full Title Page", []),
        (4, "temp_left_Page_04.png", "Page 4", ["In the sunny heart of Pride Valley, Leo loved showing off how fast and high he could jump."]),
        (5, "temp_right_Page_04.png", "Page 5", ['"Watch this, Maya! I\'m the strongest pouncer in the whole pride!" Leo cheered as he took a huge leap.<br/><br/>CRACK! He landed with a heavy thump right on Pop Pop\'s carved wooden garden marker!']),
        (6, "temp_left_Page_05.png", "Page 6", ["The smooth oak post snapped cleanly in two.<br/><br/>Leo gasped and scrambled backward, his amber eyes wide in shock."]),
        (7, "temp_right_Page_05.png", "Page 7", ['Maya rushed over, clutching Glimmer tight.<br/><br/>"Oh no, Leo! Pop Pop’s special flower marker!" she whispered.']),
        (8, "temp_left_Page_06.png", "Page 8", ["Leo's heart pounded like a drum.<br/><br/>A cold, heavy feeling churned inside his belly—a twisty tummy!"]),
        (9, "temp_right_Page_06.png", "Page 9", ['"Maybe we can hide the pieces under the leaves," Leo panicked.<br/><br/>Maya shook her head. "Stories won\'t fix a twisty tummy."']),
        (10, "temp_left_Page_07.png", "Page 10", ['Maya placed a comforting paw on his arm.<br/><br/>"Making a mistake is scary, Leo. But telling the truth is the bravest choice of all."']),
        (11, "temp_right_Page_07.png", "Page 11", ["Just then, heavy footsteps crunched on the gravel path.<br/><br/>Pop Pop stopped in his tracks, looking down at the broken marker in the grass."]),
        (12, "temp_left_Page_08.png", "Page 12", ['Pop Pop looked at the splintered wood, then turned to the cubs.<br/><br/>His amber eyes were calm and patient. "What happened here, young cubs?"']),
        (13, "temp_right_Page_08.png", "Page 13", ["Leo felt his legs shake. He wanted to lie, but he remembered who he was.<br/><br/>He placed his paw firmly over his heart."]),
        (14, "temp_left_Page_09.png", "Page 14", ['"It was me, Pop Pop," Leo confessed clearly. "I was jumping and landed right on it. I\'m so sorry."']),
        (15, "temp_right_Page_09.png", "Page 15", ['Pop Pop smiled warmly and pulled Leo into a giant, cozy bear hug.<br/><br/>"Thank you for telling me the truth, Leo. That took real lion bravery."']),
        (16, "temp_left_Page_10.png", "Page 16", ['Pop Pop held up the broken wooden pieces.<br/><br/>"A marker can always be glued, but family trust is much harder to fix. Today, you chose honor."']),
        (17, "temp_right_Page_10.png", "Page 17", ['Maya cheered and jumped up and down!<br/><br/>"You were so brave, Leo! Telling the truth makes you the strongest cub in the pride!"']),
        (18, "temp_left_Page_11.png", "Page 18", ["Pop Pop brought them to his workbench.<br/><br/>Together, they carefully applied wood glue, set the clamp, and fixed the broken marker."]),
        (19, "temp_right_Page_11.png", "Page 19", ['Mom and Dad walked in and smiled.<br/><br/>"Honesty is our family\'s foundation," Dad said, placing a proud paw on Leo\'s shoulder.']),
        (20, "temp_left_Page_12.png", "Page 20", ["Once the glue dried, they walked out to the garden.<br/><br/>Leo proudly placed the handcrafted marker back beside Pop Pop's blooming marigolds."]),
        (21, "temp_right_Page_12.png", "Page 21", ["Pop Pop gathered the cubs close under the shade of the grand, sprawling acacia tree."]),
        (22, "temp_left_Page_13.png", "Page 22", ['"Always remember our family way," Pop Pop said proudly, winking with gentle wisdom.']),
        (23, "temp_right_Page_13.png", "Page 23", ["Leo and Maya stood up together, placed their paws firmly over their hearts, and recited the creed:"]),
        (24, "temp_left_Page_14.png", "Page 24", ['<span class="text-creed">"ONLY weak lions lie. The Jordan Pride is Fearless and Strong. Therefore, we are always honest and true!"</span>']),
        (25, "temp_right_Page_14.png", "Page 25", ["Leo smiled brightly. The twisty feeling in his stomach was completely gone, replaced by a warm sense of pride."]),
        (26, "temp_left_Page_15.png", "Page 26", ["Whenever you make a mistake, remember Leo's story.<br/><br/>Stand tall, take a deep breath, and let honesty show your true strength!"]),
        (27, "temp_right_Page_15.png", "Page 27", ["Because when you tell the truth, family trust stays unbroken, and your heart stays bright and free!<br/><br/>The Jordan Pride is always honest and true—and so are you!"]),
        (28, "Page_16.png", "Family Value Creed Page", ['<b>THE JORDAN PRIDE FAMILY CREED</b><br/><br/><span class="text-creed">"ONLY weak lions lie.<br/>The Jordan Pride is Fearless and Strong.<br/>Therefore, we are always honest and true."</span>']),
        (29, "Page_17.png", "Discussion Corner", ["<b>DISCUSSION CORNER (Parent & Child Reflection)</b><br/><br/>1. Have you ever felt a 'twisty tummy' after breaking something or making a mistake?<br/>2. Why did it take MORE bravery for Leo to tell Pop Pop the truth than to make up an excuse?<br/>3. How did Pop Pop help Leo fix the wooden marker after Leo told the truth?"]),
        (30, "Page_18.png", "Honor Code Checklist", ["<b>HONOR CODE CHECKLIST</b><br/><br/>[  ] When I make an accidental mess, I tell an adult right away.<br/>[  ] I place my paw over my heart, take a deep breath, and speak the truth.<br/>[  ] I choose honesty even when I am afraid of getting in trouble."]),
        (31, "Page_19.png", "Meet The Jordan Pride", ["<b>MEET THE JORDAN PRIDE</b><br/><br/>• <b>Leo Jordan:</b> 6yo Boy Cub (Honesty & Courage)<br/>• <b>Maya Jordan:</b> 3yo Girl Cub (Sisterly Wisdom)<br/>• <b>Pop Pop Jordan:</b> Grandfather (Family Anchor)<br/>• <b>Mom & Dad Jordan:</b> Loving Parents"]),
        (32, "Page_20.png", "Teaser & Back Page", ["<b>COMING NEXT IN BOOK 2</b><br/><br/><i>The Jordan Pride — Book 2: The Great Community Fair</i><br/>Learn about Politeness, Respect, and Good Manners as Leo and Maya explore the vibrant Pride Valley Fair!"])
    ]

    for p_num, img_fn, p_title, text_lines in page_content_map:
        page_id = f"page_{p_num:02d}"
        xhtml_fn = f"{page_id}.xhtml"
        
        manifest_items.append(f'<item id="{page_id}" href="Text/{xhtml_fn}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="{page_id}"/>')

        text_block = "<br/><br/>".join(text_lines)
        xhtml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">
<head>
    <meta charset="utf-8"/>
    <title>{p_title}</title>
    <meta name="viewport" content="width={VIEWPORT_W}, height={VIEWPORT_H}"/>
    <link rel="stylesheet" type="text/css" href="../Styles/style.css"/>
</head>
<body>
    <div class="page-container">
        <img class="page-img" src="../Images/{img_fn}" alt="{p_title}"/>
        <div class="story-text">
            {text_block}
        </div>
    </div>
</body>
</html>"""
        with open(os.path.join(build_dir, "OEBPS", "Text", xhtml_fn), "w", encoding="utf-8") as f:
            f.write(xhtml_content)

    # 5. OEBPS/toc.xhtml (EPUB 3 Nav)
    toc_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">
<head>
    <meta charset="utf-8"/>
    <title>Table of Contents</title>
</head>
<body>
    <nav epub:type="toc" id="toc">
        <h1>Table of Contents</h1>
        <ol>
            <li><a href="Text/page_01.xhtml">Title Page</a></li>
            <li><a href="Text/page_02.xhtml">Copyright Page</a></li>
            <li><a href="Text/page_03.xhtml">Dedication</a></li>
            <li><a href="Text/page_04.xhtml">The Jordan Pride: Leo and the Broken Marker</a></li>
            <li><a href="Text/page_28.xhtml">Family Value Creed</a></li>
            <li><a href="Text/page_29.xhtml">Discussion Corner</a></li>
            <li><a href="Text/page_30.xhtml">Honor Code Checklist</a></li>
            <li><a href="Text/page_31.xhtml">Character Roster</a></li>
            <li><a href="Text/page_32.xhtml">Teaser & Back Page</a></li>
        </ol>
    </nav>
</body>
</html>"""
    with open(os.path.join(build_dir, "OEBPS", "toc.xhtml"), "w", encoding="utf-8") as f:
        f.write(toc_xhtml)

    # 6. OEBPS/package.opf
    manifest_str = "\n        ".join(manifest_items)
    spine_str = "\n        ".join(spine_items)

    package_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="pub-id" version="3.0" prefix="rendition: http://www.idpf.org/vocab/rend/0.1/#">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:identifier id="pub-id">urn:uuid:35d48c28-029a-abf1-de28-47ce564b82be</dc:identifier>
        <dc:title>The Jordan Pride — Book 1: Leo and the Broken Marker</dc:title>
        <dc:creator>The Jordan Pride Family Publishing</dc:creator>
        <dc:language>en</dc:language>
        <dc:publisher>The Jordan Pride Family Publishing</dc:publisher>
        <dc:rights>Copyright © 2026 The Jordan Pride Series. All rights reserved.</dc:rights>
        <meta property="dcterms:modified">2026-08-08T12:00:00Z</meta>
        <!-- EPUB 3 Fixed Layout Metadata -->
        <meta property="rendition:layout">pre-paginated</meta>
        <meta property="rendition:orientation">portrait</meta>
        <meta property="rendition:spread">auto</meta>
        <meta name="cover" content="img_Page_01_png"/>
    </metadata>
    <manifest>
        {manifest_str}
    </manifest>
    <spine page-progression-direction="ltr">
        {spine_str}
    </spine>
</package>"""

    with open(os.path.join(build_dir, "OEBPS", "package.opf"), "w", encoding="utf-8") as f:
        f.write(package_opf)

    # Zip into .epub archive (mimetype FIRST uncompressed)
    with zipfile.ZipFile(out_epub_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. mimetype (Stored, not compressed)
        zf.write(os.path.join(build_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        
        # 2. Add rest of build_dir
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file == "mimetype":
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, build_dir)
                zf.write(full_path, rel_path)

    # Backup to external drive
    backup_epub = os.path.join(backup_dir, "The_Jordan_Pride_Book_1_eBook_FixedLayout.epub")
    if os.path.abspath(out_epub_path) != os.path.abspath(backup_epub):
        shutil.copyfile(out_epub_path, backup_epub)

    print(f"🎉 Universal EPUB 3 Fixed-Layout eBook built successfully!")
    print(f"  • Primary Output: {out_epub_path}")
    print(f"  • External Backup: {backup_epub}")

if __name__ == "__main__":
    create_epub3_fixed_layout()
