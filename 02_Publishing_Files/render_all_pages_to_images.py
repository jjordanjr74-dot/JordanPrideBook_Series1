import os
import fitz  # PyMuPDF

pdf_path = r"C:\Users\marti\Desktop\The_Jordan_Pride_Book_1_Print_Interior.pdf"
output_dir = r"C:\Users\marti\Desktop\The Jordan Pride - Book 1 Renders"
os.makedirs(output_dir, exist_ok=True)

def render_pages():
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    print(f"Total pages in PDF: {len(doc)}")
    
    # We want to render:
    # Page 1 (Index 0) - Title Page
    # Page 20 (Index 19) - Spread 9 Left (Healed)
    # Page 21 (Index 20) - Spread 9 Right (Healed)
    pages_to_render = [0, 19, 20]
    
    for p_idx in pages_to_render:
        if p_idx < len(doc):
            page = doc[p_idx]
            print(f"Rendering Page {p_idx+1}...")
            # 2x scale for high resolution
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            out_path = os.path.join(output_dir, f"Page_{p_idx+1}_Render.png")
            pix.save(out_path)
            print(f"  ✓ Saved to {out_path}")
        else:
            print(f"⚠️ Page index {p_idx} out of range!")

if __name__ == "__main__":
    render_pages()
