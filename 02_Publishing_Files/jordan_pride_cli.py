import os
import sys
import json
import subprocess
import re
from closed_loop_production import load_state, process_page, DESKTOP_DIR, MANUSCRIPT_PATH, STATE_PATH

def print_help():
    print("""
==================================================================
🦁 THE JORDAN PRIDE - UNIFIED BOOK PRODUCTION CLI v1.0 🦁
==================================================================
Usage:
  python jordan_pride_cli.py <command> [arguments]

Commands:
  status                   - Display the production and audit state of all pages.
  produce <page_num>       - Run the closed-loop generator & audit loop for a specific page/spread.
  batch-produce <s_page> <e_page> - Produce a range of pages/spreads sequentially (idempotent).
  compile                  - Sync assets, build final PDF, EPUB, Cover, and backup to D:\\.
  help                     - Show this help message.

Examples:
  python jordan_pride_cli.py status
  python jordan_pride_cli.py produce 4
  python jordan_pride_cli.py batch-produce 4 12
  python jordan_pride_cli.py compile
==================================================================
""")

def display_status():
    state = load_state()
    print("\n📊 --- PRODUCTION STATUS MATRIX ---")
    print(f"Tracking Database: {STATE_PATH}\n")
    print(f"{'Page / Spread':<15} | {'Audit Status':<12} | {'Attempts':<10} | {'Issues Found'}")
    print("-" * 75)
    
    # 32-page structure mapping
    # Single pages: 1, 2, 3, 28, 29, 30, 31, 32
    # Spreads: 4 (covers 4-5), 6 (covers 6-7), 8 (8-9), 10 (10-11), 12 (12-13), 14 (14-15), 16 (16-17), 18 (18-19), 20 (20-21), 22 (22-23), 24 (24-25), 26 (26-27)
    pages_to_check = [1, 2, 3] + list(range(4, 28, 2)) + [28, 29, 30, 31, 32]
    
    for p in pages_to_check:
        fn = f"Page_{p:02d}.png"
        page_info = state.get(fn, {})
        status = page_info.get("status", "PENDING")
        attempts = page_info.get("attempts", 0)
        issues = ", ".join(page_info.get("issues", [])) if page_info.get("issues") else "None"
        
        name_str = f"Page {p}" if p not in range(4, 28, 2) else f"Spread {p}-{p+1}"
        print(f"{name_str:<15} | {status:<12} | {attempts:<10} | {issues}")
    print("-" * 75)

def run_compilation():
    print("\n📦 --- EXECUTING BUILD & COMPILE PIPELINE ---")
    
    # Build a small inline script to do compilation
    compile_worker = os.path.join(DESKTOP_DIR, "02_Publishing_Files", "run_compilation_worker.py")
    code = """
import os
import shutil
import subprocess

root_dir = r"C:\\Users\\marti\\JordanPrideBook_Series1_Final"
publishing_dir = os.path.join(root_dir, "02_Publishing_Files")

# Check compile scripts and run them
pdf_script = os.path.join(publishing_dir, "build_pdf_layout.py")
if os.path.exists(pdf_script):
    print("\\n1. Compiling Book 1 Print Interior PDF...")
    res = subprocess.run(["python", pdf_script], capture_output=True, text=True, cwd=publishing_dir)
    print(f"  Exit code: {res.returncode}")
    print(f"  STDOUT: {res.stdout.strip()}")
    if res.stderr:
        print(f"  STDERR: {res.stderr.strip()}")

epub_script = os.path.join(publishing_dir, "build_fixed_layout_epub.py")
if os.path.exists(epub_script):
    print("\\n2. Compiling Book 1 eBook EPUB...")
    res = subprocess.run(["python", epub_script], capture_output=True, text=True, cwd=publishing_dir)
    print(f"  Exit code: {res.returncode}")
    print(f"  STDOUT: {res.stdout.strip()}")
    if res.stderr:
        print(f"  STDERR: {res.stderr.strip()}")

cover_script = os.path.join(publishing_dir, "build_cover_pdf.py")
if os.path.exists(cover_script):
    print("\\n3. Compiling Cover Wrap PDF...")
    res = subprocess.run(["python", cover_script], capture_output=True, text=True, cwd=publishing_dir)
    print(f"  Exit code: {res.returncode}")
    print(f"  STDOUT: {res.stdout.strip()}")
    if res.stderr:
        print(f"  STDERR: {res.stderr.strip()}")

print("\\n🎉 Compilation Finished successfully!")
"""
    with open(compile_worker, "w") as f:
        f.write(code)
    
    res = subprocess.run(["python", compile_worker], capture_output=False)
    if os.path.exists(compile_worker):
         os.remove(compile_worker)

# Manuscript scene extraction for automation
def get_art_prompt(page_num):
    prompts_path = os.path.join(DESKTOP_DIR, "01_Final_Book_Assets", "The Jordan Pride - Book 1 Art Prompts.md")
    if not os.path.exists(prompts_path):
        return None
        
    with open(prompts_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split content by markdown #### headings
    headings = re.split(r'(?=#### \*\*)', content)
    for h in headings:
        header_line = h.split('\n')[0]
        # Match Page or Pages containing the page number
        if re.search(rf'\bPage(s)?\s*(\d+\s*(&|and|-)?\s*)*{page_num}\b', header_line, re.IGNORECASE):
            # Extract content inside backticks `...`
            match_backtick = re.search(r'`([^`]+)`', h, re.DOTALL)
            if match_backtick:
                return match_backtick.group(1).strip()
    return None

def get_manuscript_scene(page_num):
    if not os.path.exists(MANUSCRIPT_PATH):
        return f"Scene description for Page {page_num}"
        
    with open(MANUSCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Search for headings like "### **Page 4 (Spread 1 - Left)**" or similar
    pattern = rf"### \*\*Page {page_num}.*?\*\*(.*?)(?=### \*\*Page|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
        # Clean lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return " ".join(lines)
    
    # Try alternate match if headers are shaped differently
    pattern_alt = rf"### \*\*Page {page_num}\b.*?\n(.*?)(?=### \*\*|\Z)"
    match_alt = re.search(pattern_alt, content, re.DOTALL | re.IGNORECASE)
    if match_alt:
        text = match_alt.group(1).strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return " ".join(lines)
        
    return f"Scene description for Page {page_num}"

def main():
    # Set production mode based on arguments
    mode = "local"
    if "--cloud" in sys.argv:
        mode = "cloud"
        sys.argv.remove("--cloud")
    os.environ["JORDAN_PRIDE_MODE"] = mode
    print(f"🌟 RUNNING IN {mode.upper()} GENERATION MODE 🌟\n")

    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    
    if cmd == "status":
        display_status()
        
    elif cmd == "compile":
        run_compilation()
        
    elif cmd == "produce":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify the page number (e.g. 4)")
            sys.exit(1)
        try:
            p_num = int(sys.argv[2])
        except ValueError:
            print("❌ Error: Page number must be an integer.")
            sys.exit(1)
            
        # Prioritize master-locked Art Prompt sheet over raw manuscript text!
        scene_text = get_art_prompt(p_num)
        is_from_art_sheet = True
        if not scene_text:
            scene_text = get_manuscript_scene(p_num)
            is_from_art_sheet = False
            
        is_spread = p_num in range(4, 28)
        
        if is_from_art_sheet:
            print(f"📖 Extracted Master-Locked Art Prompt for Page {p_num}:")
        else:
            print(f"📖 Extracted Scene Text from Manuscript for Page {p_num}:")
        print(f"  \"{scene_text}\"\n")
        
        process_page(p_num, f"Page {p_num} Production", scene_text, is_spread)
        
    elif cmd == "batch-produce":
        if len(sys.argv) < 4:
            print("❌ Error: Please specify start and end pages (e.g. 4 12)")
            sys.exit(1)
        try:
            start_p = int(sys.argv[2])
            end_p = int(sys.argv[3])
        except ValueError:
            print("❌ Error: Pages must be integers.")
            sys.exit(1)
            
        # Standard layout range loop
        # Spreads should increment by 2
        pages_to_run = []
        p = start_p
        while p <= end_p:
            pages_to_run.append(p)
            if p in range(4, 28):
                p += 2
            else:
                p += 1
                
        print(f"🔄 Starting Sequential Batch Production for pages: {pages_to_run}")
        for p_num in pages_to_run:
            scene_text = get_art_prompt(p_num)
            if not scene_text:
                scene_text = get_manuscript_scene(p_num)
            is_spread = p_num in range(4, 28)
            success = process_page(p_num, f"Page {p_num} Production", scene_text, is_spread)
            if not success:
                print(f"⚠️ Batch interrupted at page {p_num} due to failure.")
                sys.exit(1)
        print("\n🎉 Batch production completed successfully!")
        
    else:
        print_help()

if __name__ == "__main__":
    main()
