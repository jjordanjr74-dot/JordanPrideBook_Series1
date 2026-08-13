import os
from PIL import Image, ImageDraw, ImageOps

source_path = r"C:\Users\marti\AppData\Local\hermes\cache\images\img_f7b8c5c7eda4.jpg"
target_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final\01_Final_Book_Assets"
target_path = os.path.join(target_dir, "Page_01.png")

os.makedirs(target_dir, exist_ok=True)

if not os.path.exists(source_path):
    print("Error: Source title page image not found!")
    exit(1)

# Target dimensions based on ReportLab aspect ratio (7.2" x 9.3" -> 0.7742)
# If width is 1024, height must be 1024 / 0.7741935 = 1323
target_w = 1024
target_h = 1323

# Create pristine warm cream canvas (#FFFDF5)
cream_color = (255, 253, 245) # #FFFDF5
canvas_img = Image.new("RGB", (target_w, target_h), cream_color)

with Image.open(source_path) as img:
    # Scale down the original 1024x1024 illustration slightly to build a gorgeous safe border
    # 860x880 maintains near-square or we can do exact 880x880 square
    scaled_size = 880
    illustration = img.resize((scaled_size, scaled_size), Image.Resampling.LANCZOS)
    
    # Calculate centering coordinates
    paste_x = (target_w - scaled_size) // 2 # (1024 - 880) // 2 = 72
    paste_y = (target_h - scaled_size) // 2 # (1323 - 880) // 2 = 221
    
    # Paste illustration onto cream canvas
    canvas_img.paste(illustration, (paste_x, paste_y))
    
    # Draw an elegant pre-press accent rule (border) around the illustration
    draw = ImageDraw.Draw(canvas_img)
    accent_color = (140, 90, 43) # #8C5A2B (Warm Brown Accent)
    
    # Draw outer border line exactly 1px outside the illustration
    border_rect = [paste_x - 2, paste_y - 2, paste_x + scaled_size + 1, paste_y + scaled_size + 1]
    draw.rectangle(border_rect, outline=accent_color, width=2)

# Save as Page_01.png replacing the draft
canvas_img.save(target_path, "PNG")
print(f"✨ Success! Formatted Title Page saved to {target_path}")
print(f"Dimensions: {canvas_img.size}, Aspect Ratio: {canvas_img.size[0]/canvas_img.size[1]:.4f}")
