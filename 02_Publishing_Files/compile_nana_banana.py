import os
from PIL import Image

src_dir = r"C:\Users\marti\Desktop\Master Reference Images and Pages for Book1"
dst_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final\01_Final_Book_Assets"

os.makedirs(dst_dir, exist_ok=True)

# Map pageX.jpg to Page_XX.png
for i in range(1, 18):
    src_file = os.path.join(src_dir, f"page{i}.jpg")
    dst_file = os.path.join(dst_dir, f"Page_{i:02d}.png")
    
    if os.path.exists(src_file):
        print(f"Converting {src_file} -> {dst_file}")
        try:
            with Image.open(src_file) as img:
                img.save(dst_file, "PNG")
        except Exception as e:
            print(f"Error converting page{i}.jpg: {e}")
    else:
        print(f"File not found: {src_file}")

# Map title page and copyright page if they exist
custom_maps = {
    "title page.jpg": "Page_01.png",
    "Copyright and dedication.jpg": "Page_02.png",
    "best title book1.jpg": "Page_03.png",
}

for src_name, dst_name in custom_maps.items():
    src_file = os.path.join(src_dir, src_name)
    dst_file = os.path.join(dst_dir, dst_name)
    if os.path.exists(src_file):
        print(f"Converting custom map {src_file} -> {dst_file}")
        try:
            with Image.open(src_file) as img:
                img.save(dst_file, "PNG")
        except Exception as e:
            print(f"Error converting {src_name}: {e}")

print("Restoration of Nana Banana master images complete!")
