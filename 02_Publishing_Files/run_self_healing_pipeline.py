#!/usr/bin/env python3
import os
import base64
import urllib.request
import urllib.error
import json
import time
from pathlib import Path
from PIL import Image as PILImage
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
AUDIT_MODEL = "gemini-3.5-flash"
GENERATE_MODEL = "gemini-2.5-flash-image"

AUDIT_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{AUDIT_MODEL}:generateContent?key={API_KEY}"
GENERATE_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GENERATE_MODEL}:generateContent?key={API_KEY}"

desktop_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final"
images_dir = os.path.join(desktop_dir, "01_Final_Book_Assets")
backup_dir = os.path.join(desktop_dir, "01_Final_Book_Assets")
prompts_file = os.path.join(desktop_dir, "01_Final_Book_Assets", "The Jordan Pride - Book 1 Art Prompts.md")
report_file = os.path.join(desktop_dir, "02_Publishing_Files", "Book1_Audit_Report.json")
anchor_path = r"C:\Users\marti\AppData\Local\hermes\cache\images\img_4f6728cd4318.jpg"

# Ensure directories exist
os.makedirs(images_dir, exist_ok=True)
if os.path.exists("D:/"):
    os.makedirs(backup_dir, exist_ok=True)

# Load Master Anchor Image
if os.path.exists(anchor_path):
    with open(anchor_path, "rb") as f:
        anchor_b64 = base64.b64encode(f.read()).decode("utf-8")
else:
    anchor_b64 = None
    print("⚠️ Master Anchor image not found! Reference conditioning will be skipped.")

# Load Art Prompts from markdown
def load_prompts():
    if not os.path.exists(prompts_file):
        return {}
    with open(prompts_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    pages = {}
    lines = text.split("\n")
    current_title = ""
    idx = 1
    for line in lines:
        if line.startswith("#### ") or line.startswith("## 🖼️"):
            current_title = line.strip("#").strip()
        elif line.startswith("`High-quality 2D digital storybook art illustration"):
            current_prompt = line.strip("`").strip()
            pages[idx] = (current_title, current_prompt)
            idx += 1
    return pages

# Multi-modal Audit Image
def audit_image(image_path, title, prompt_text):
    if not os.path.exists(image_path):
        return {"status": "FAIL", "issues": ["File missing on disk."], "explanation": "Image does not exist."}
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    audit_instruction = (
        "You are an Elite Executive Children's Book Editor and Publishing Director with 30 years of experience in high-end publishing. "
        "Your eye for detail is legendarily meticulous. You are auditing a draft illustration for 'The Jordan Pride' children's picture book series "
        "against strict brand guidelines, narrative continuity, layout compliance, and visual perfection. "
        "Analyze the attached image under a microscopic lens. Check every square pixel, every background detail, every limb, clothing seam, and prop alignment.\n\n"
        "--- CRITICAL BRAND AUDIT CRITERIA (NO EXCEPTIONS ALLOWED) ---\n"
        "1. PROPORTION MATRIX: Leo (6yo brother) must be a tall child cub. Maya (3yo sister) is a tiny toddler. "
        "Whenever both appear on the page, Maya MUST be dramatically smaller and shorter than Leo. Her head must only reach up to Leo's shoulder, waist, or hip height. "
        "Maya must never appear to be equal in height, equal in body mass, or taller than Leo. This is the #1 visual priority check.\n"
        "2. ACCESSIBLE ATTRIBUTES & HAIR LOCKS: Leo is a male cub. He has a simple, messy reddish-brown head hair tuft. "
        "Leo must have absolutely NO ribbons, bows, flowers, barrettes, or accessories in his hair or fur. "
        "Only Maya wears the bright purple ear bow ribbon. Verify that Leo does not have a bow and Maya does.\n"
        "3. 100% ANTHROPOMORPHIC UNIVERSE: Every single character, main cast, extra, neighbor, or passerby in the background "
        "must be an upright, bipedal animal walking on two legs, wearing stylish clothing. There must be zero human beings, human faces, or human skin/hands. "
        "Hands must be animal paws with fur, claws, or paw pads—never human-like smooth five-fingered hands or realistic human anatomy.\n"
        "4. ATTIRE RECOGNITION & PATTERN CONSISTENCY: \n"
        "   - Leo: blue denim overalls over an orange-and-white striped t-shirt. Stripes must be horizontal and clear, not plaid or scrambled.\n"
        "   - Maya: sunshine-yellow dress with deep front crayon pockets, pink sandals.\n"
        "   - Pop Pop: Red plaid/flannel long-sleeve shirt with rolled sleeves, dark khaki trousers, leather boots.\n"
        "   - Mom: Teal tunic, silver paw-print pendant.\n"
        "   - Dad: Navy blue mechanic coveralls.\n"
        "5. PROP SPATIAL MECHANICS & LOGIC: \n"
        "   - Pop Pop's garden marker has a highly distinct, hand-carved barber-pole style spiral twist groove winding top-to-bottom. It is natural oak. "
        "   - If the marker is broken, it cannot logically stand upright. If they are in the workshop repairing it, it must lie flat on the wooden workbench side-by-side, never stand vertically.\n"
        "6. ANATOMICAL INTEGRITY: Look closely at characters' faces, limbs, and tails. Check for: "
        "   - AI distortion: floating ears, double noses, misplaced tails, extra limbs/fingers/claws.\n"
        "   - Eye focus: are both eyes pointing in a natural, logical direction? Is there any pupil misalignment?\n"
        "   - Character doubling/cloning: is there exactly one Leo and one Maya? Verify characters have not been cloned (e.g. rendering two Mayas).\n"
        "7. PRINT COMPLIANCE & GUTTER SAFETY: For panoramic double-page spreads, the central vertical line (center spine fold) must be completely clear of: "
        "   - Character faces, text blocks, title logos, or critical storytelling action.\n"
        "8. TEXT OVERLAY SAFE ZONES: Ensure there is a low-contrast, uncluttered, simple open background space (like clear sky, soft grass, empty wall) specifically reserved for readable text overlay on both the left and right sides.\n\n"
        f"Scene Title: {title}\n"
        f"Scene Prompt: {prompt_text}\n\n"
        "--- INSTRUCTIONS FOR RESPONSE ---\n"
        "Conduct a multi-pass, rigorous analysis. Be uncompromisingly honest. If you see even the most minute deficiency (such as a pattern anomaly, a slight height squashing, a hidden human hand, or a double ear), flag it as a FAIL. "
        "Respond ONLY in valid, parseable JSON format. Do not prepend or append markdown code block ticks. Use this schema:\n"
        "{\n"
        "  \"status\": \"PASS\" or \"FAIL\",\n"
        "  \"issues\": [\"list of specific, distinct visual errors, contradictions, or deficiencies found. Be highly specific and granular. If PASS, leave empty.\"],\n"
        "  \"explanation\": \"A comprehensive, professional, 30-year veteran level editorial critique explaining your observations, character by character, pixel-region by pixel-region, detail by detail. Outline exactly why the image passes or where the artist must focus to correct the flaws.\"\n"
        "}"
    )

    payload = {
        "contents": [{
            "parts": [
                {"text": audit_instruction},
                {"inlineData": {"mimeType": "image/png", "data": img_b64}}
            ]
        }]
    }

    req = urllib.request.Request(AUDIT_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                candidates = res.get("candidates", [])
                if candidates:
                    text_resp = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if text_resp.startswith("```json"):
                        text_resp = text_resp[7:]
                    if text_resp.endswith("```"):
                        text_resp = text_resp[:-3]
                    return json.loads(text_resp.strip())
        except urllib.error.HTTPError as e:
            if e.code in [503, 429] and attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
            raise e
    return {"status": "FAIL", "issues": ["API Error during audit"], "explanation": "Unable to communicate with the model."}

# Auto-Harden Prompt using failed issues
def auto_harden_prompt(original_prompt, failed_issues):
    issues_bullet = "\n".join([f"- {iss}" for iss in failed_issues])
    hardening_instruction = (
        f"You are an Elite AI Prompt Engineer. Your task is to rewrite the image prompt below to fix specific visual errors "
        f"reported by a multi-modal audit.\n\n"
        f"Original Prompt: {original_prompt}\n\n"
        f"Visual Audit Errors Found:\n{issues_bullet}\n\n"
        f"Generate a hardened, optimized scene prompt. You MUST inject strong negative and positive reinforcement instructions "
        f"to force the generator to correct these specific errors. Keep the style prefix and standard structure exactly. "
        f"Make the corrections highly explicit and non-negotiable. "
        f"Respond ONLY with the complete hardened prompt string inside double quotes."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": hardening_instruction}]
        }]
    }
    
    req = urllib.request.Request(AUDIT_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                candidates = res.get("candidates", [])
                if candidates:
                    text_resp = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    return text_resp.strip('"').strip()
        except urllib.error.HTTPError as e:
            if e.code in [503, 429] and attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
    return original_prompt

# Generate Image with Reference Conditioning
def generate_conditioned_image(hardened_prompt):
    instruction = (
        "Generate a high-resolution, final publication-grade 2D digital storybook illustration with vibrant vector linework and soft cel shading. "
        "STRICT CHARACTER & ATTIRE CONTINUITY: Copy exactly the character visual identity, fur tone, and outfit designs shown in reference image. "
        f"Scene Action: {hardened_prompt}"
    )
    
    payload = {
        "contents": [{
            "parts": [
                {"text": instruction},
                {"inlineData": {"mimeType": "image/jpeg", "data": anchor_b64}}
            ]
        }]
    }
    
    req = urllib.request.Request(GENERATE_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                candidates = res.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        if "inlineData" in part:
                            b64_data = part["inlineData"]["data"]
                            return base64.b64decode(b64_data)
        except urllib.error.HTTPError as e:
            if e.code in [503, 429] and attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
            raise e
    raise ValueError("Failed to generate image from Google AI Studio.")

# Save and perform automatic left/right splits for physical layout spreads
def save_and_split(fn, img_bytes, is_spread=True):
    filepath = os.path.join(images_dir, fn)
    with open(filepath, "wb") as f:
        f.write(img_bytes)
        
    if os.path.exists("D:/"):
        backup_path = os.path.join(backup_dir, fn)
        with open(backup_path, "wb") as f:
            f.write(img_bytes)
            
    if is_spread:
        with PILImage.open(filepath) as im:
            w, h = im.size
            im.crop((0, 0, w // 2, h)).save(os.path.join(images_dir, f"temp_left_{fn}"))
            im.crop((w // 2, 0, w, h)).save(os.path.join(images_dir, f"temp_right_{fn}"))
    print(f"  💾 Saved and split {fn}")

# Healing process for a single failed page
def heal_page(page_name, failed_issues, original_prompt, title, max_attempts=3):
    print(f"\n⚡ Starting HEAL process for {page_name}...")
    is_spread = "Cover_Wrap" not in page_name and "Page_01" not in page_name and "Page_02" not in page_name and "Page_03" not in page_name
    
    current_prompt = original_prompt
    for attempt in range(1, max_attempts + 1):
        print(f"  [{page_name}] Attempt {attempt}/{max_attempts}: Hardening prompt based on audit issues...")
        hardened = auto_harden_prompt(current_prompt, failed_issues)
        print(f"  [{page_name}] Hardened Prompt: {hardened[:120]}...")
        
        try:
            print(f"  [{page_name}] Generating image candidate...")
            img_bytes = generate_conditioned_image(hardened)
            
            # Temporary save to audit
            temp_path = os.path.join(images_dir, f"temp_audit_{page_name}")
            with open(temp_path, "wb") as f:
                f.write(img_bytes)
                
            print(f"  [{page_name}] Auditing new image...")
            audit_result = audit_image(temp_path, title, original_prompt)
            print(f"  [{page_name}] Audit Result: {audit_result.get('status')}")
            
            if audit_result.get("status") == "PASS":
                # Promote to final
                os.replace(temp_path, os.path.join(images_dir, page_name))
                save_and_split(page_name, img_bytes, is_spread=is_spread)
                return {"status": "PASS", "issues": [], "explanation": audit_result.get("explanation")}
            else:
                print(f"  [{page_name}] Attempt failed. Issues: {audit_result.get('issues')}")
                failed_issues = audit_result.get("issues")
                current_prompt = hardened # Compound hardening
                # Clean up temp
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception as e:
            print(f"  [{page_name}] Error during generation: {e}")
            time.sleep(2)
            
    return {"status": "FAIL", "issues": failed_issues, "explanation": "Maximum healing attempts reached without passing audit."}

# Main pipeline execution
def main():
    print("==================================================")
    print("🛡️  THE JORDAN PRIDE - SELF-HEALING PUBLISHING PIPELINE 🛡️")
    print("==================================================")
    
    # 1. Load data
    prompts = load_prompts()
    if not prompts:
        print("❌ Error: Could not load prompts from markdown sheet.")
        return
    print(f"Loaded {len(prompts)} page prompts from markdown.")
    
    if not os.path.exists(report_file):
        print("❌ Error: Book1_Audit_Report.json not found in Publishing Files.")
        return
        
    with open(report_file, "r", encoding="utf-8") as f:
        audit_report = json.load(f)
    print(f"Loaded audit report containing {len(audit_report)} audited pages.")

    # Convert audit report to dictionary for easy access
    report_dict = {item[0]: item[1] for item in audit_report}
    
    failed_items = []
    for fn, rep in report_dict.items():
        if rep.get("status") == "FAIL":
            # Extract page index from filename (e.g., 'Page_04.png' -> 4)
            try:
                if fn.startswith("Page_"):
                    p_idx = int(fn.split("_")[1].split(".")[0])
                    if p_idx in prompts:
                        failed_items.append((fn, prompts[p_idx][0], prompts[p_idx][1], rep.get("issues")))
                elif fn == "Cover_Wrap.png" and 21 in prompts:
                    failed_items.append((fn, prompts[21][0], prompts[21][1], rep.get("issues")))
            except Exception as e:
                print(f"Error parsing page {fn}: {e}")
                
    if not failed_items:
        print("🎉 Excellent! All audited pages are currently PASS. No healing needed.")
        return
        
    print(f"\n🔍 Found {len(failed_items)} failing pages that require automatic healing.")
    print("\nStarting Parallel Self-Healing execution...")
    
    # Run healing in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(heal_page, fn, issues, prompt_text, title): fn
            for fn, title, prompt_text, issues in failed_items
        }
        
        for future in as_completed(futures):
            fn = futures[future]
            try:
                res = future.result()
                results[fn] = res
                print(f"🏆 Healing process complete for {fn}: {res['status']}")
            except Exception as e:
                print(f"❌ Healing process crashed for {fn}: {e}")
                
    # Update the audit report on disk
    updated_report = []
    for item in audit_report:
        fn = item[0]
        if fn in results:
            updated_report.append([fn, results[fn]])
        else:
            updated_report.append(item)
            
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(updated_report, f, indent=2)
    print("\n✅ Publishing_Files/Book1_Audit_Report.json successfully updated!")
    
    # Synchronize with production_state.json
    state_file = os.path.join(desktop_dir, "02_Publishing_Files", "production_state.json")
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            
            for fn, res in results.items():
                if fn.startswith("Page_") and fn != "Cover_Wrap.png":
                    existing = state_data.get(fn, {})
                    state_data[fn] = {
                        "status": res.get("status"),
                        "issues": res.get("issues", []),
                        "explanation": res.get("explanation", ""),
                        "prompt_used": existing.get("prompt_used", ""),
                        "timestamp": time.time(),
                        "attempts": existing.get("attempts", 1) + 1
                    }
                    print(f"🔄 Synced production_state.json status for {fn} -> {res.get('status')}")
            
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4)
            print("✅ Publishing_Files/production_state.json successfully synchronized!")
        except Exception as e:
            print(f"⚠️ Warning: Could not sync production_state.json: {e}")
    print("==================================================")

if __name__ == "__main__":
    main()
