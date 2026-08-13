import os
import json
import base64
import requests

src_dir = r"C:\Users\marti\Desktop\Master Reference Images and Pages for Book1"
api_url = "http://localhost:11434/api/generate"

# Core pages to run high-fidelity vision audits on
pages_to_audit = [
    ("title page.jpg", "Page 1: Title Page Vignette"),
    ("page4.jpg", "Page 4 & 5: Spread 1 (Leap)"),
    ("page12.jpg", "Page 12 & 13: Spread 5 (Embrace)"),
    ("page14.jpg", "Page 14 & 15: Spread 6 (Objects Lesson)"),
]

audit_results = {}

print("🔬 STARTING MICROPHONE PRE-PRESS AUDIT VIA OLLAMA QWEN2.5-VL...")

for filename, description in pages_to_audit:
    file_path = os.path.join(src_dir, filename)
    if not os.path.exists(file_path):
        print(f"Skipping {filename} (not found)")
        continue
        
    print(f"Auditing {description} ({filename})...")
    
    # Read and encode image to base64
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    prompt = (
        "You are an uncompromising 30-year veteran elite children's book publisher and pre-press QA auditor. "
        "Analyze this illustration against the strict 'JORDAN PRIDE SERIES STANDARD'. "
        "Perform a microscopic audit. Check for:\n"
        "1. Anatomy: Are there human fingers, human knuckles, or splayed hands? (Lions must have thick, rounded, smooth, fingerless mitten paws).\n"
        "2. Accessories: Does Leo have any hair bows? (Leo must have NO ribbons/bows/flowers; ONLY Maya wears the bright purple ear bow ribbon behind her left ear).\n"
        "3. Proportions: Is Leo (6yo) visibly much taller than Maya (3yo toddler cub)?\n"
        "4. Props/Environment: Does Pop Pop's garden marker feature the hand-carved barber-pole spiral twist groove?\n\n"
        "Provide your audit in this exact format:\n"
        "[AUDIT REPORT]\n"
        "Status: PASS or FAIL\n"
        "Issues Detected:\n"
        "- Issue 1\n"
        "- Issue 2\n"
        "Pre-Press Recommendation: (Be extremely direct and detailed like a veteran editor)."
    )
    
    payload = {
        "model": "qwen2.5vl:latest",
        "prompt": prompt,
        "images": [encoded_string],
        "stream": False
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=90)
        if response.status_code == 200:
            result = response.json().get("response", "")
            audit_results[filename] = result
            print(f"Finished audit for {filename}!")
            print(result)
            print("="*60)
        else:
            print(f"Failed to audit {filename}: {response.status_code}")
    except Exception as e:
        print(f"Error auditing {filename}: {e}")

# Save results
with open(os.path.join(src_dir, "Pre_Press_Ollama_Audit.json"), "w") as f:
    json.dump(audit_results, f, indent=4)

print("🔬 ALL OFFLINE VISION AUDITS COMPLETE!")
