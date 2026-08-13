import os
import base64
import urllib.request
import urllib.error
import json
import time
from PIL import Image as PILImage

API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
MODEL_NAME = "gemini-3.5-flash"
ENDPOINT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

desktop_dir = r"C:\Users\marti\Desktop"
images_dir = os.path.join(desktop_dir, "The Jordan Pride - Book 1 Images")
prompts_file = os.path.join(desktop_dir, "The Jordan Pride - Book 1 Art Prompts.md")

# Load Art Prompts to Map Pages
def load_prompts():
    if not os.path.exists(prompts_file):
        return {}
    with open(prompts_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    pages = {}
    lines = text.split("\n")
    current_title = ""
    current_prompt = ""
    idx = 1
    for line in lines:
        if line.startswith("#### ") or line.startswith("## 🖼️"):
            current_title = line.strip("#").strip()
        elif line.startswith("`High-quality 2D digital storybook art illustration"):
            current_prompt = line.strip("`").strip()
            pages[idx] = (current_title, current_prompt)
            idx += 1
    return pages

# Multi-modal Audit Call
def audit_image(image_path, title, prompt_text):
    if not os.path.exists(image_path):
        return {"status": "MISSING", "explanation": "Image file does not exist on disk."}
    
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

    req = urllib.request.Request(
        ENDPOINT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                candidates = res.get("candidates", [])
                if candidates:
                    text_resp = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    # Clean JSON wrapping if present
                    if text_resp.startswith("```json"):
                        text_resp = text_resp[7:]
                    if text_resp.endswith("```"):
                        text_resp = text_resp[:-3]
                    text_resp = text_resp.strip()
                    return json.loads(text_resp)
        except urllib.error.HTTPError as e:
            if e.code in [503, 429] and attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
            return {"status": "ERROR", "explanation": f"API error or parsing crash: {e}"}
        except Exception as e:
            return {"status": "ERROR", "explanation": f"API error or parsing crash: {e}"}
    return {"status": "UNKNOWN", "explanation": "No response candidates returned."}

def main():
    pages = load_prompts()
    print("📋 Starting Multi-Step Brand Audit on Book 1...\n")
    
    report_path = os.path.join(desktop_dir, "Book1_Audit_Report.json")
    results_dict = {}
    
    # Load existing progress
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                old_results = json.load(f)
                results_dict = {item[0]: item[1] for item in old_results if isinstance(item, list) and len(item) == 2}
            print(f"Loaded {len(results_dict)} existing audit records. Will skip passing/completed ones.")
        except Exception as e:
            print(f"Could not load existing audit report: {e}")
            results_dict = {}
            
    # Audit Page 1 to Page 20
    for idx in range(1, 21):
        fn = f"Page_{idx:02d}.png"
        img_path = os.path.join(images_dir, fn)
        title, prompt_text = pages.get(idx, (f"Page {idx}", "No prompt mapping found."))
        
        # Check if we already have a valid PASS/FAIL result
        if fn in results_dict and results_dict[fn].get("status") in ["PASS", "FAIL"]:
            print(f"⏭ Skipping {fn} ({title}) - already audited with status: {results_dict[fn]['status']}")
            continue
            
        print(f"🔍 Auditing {fn} ({title})...")
        report = audit_image(img_path, title, prompt_text)
        print(f"  Status: {report.get('status', 'FAIL')}")
        if report.get("issues"):
            print("  Issues Found:")
            for issue in report["issues"]:
                print(f"    - {issue}")
        else:
            print("  ✓ Meets all brand standards.")
        print("-" * 50)
        
        results_dict[fn] = report
        
        # Save incremental report
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(list(results_dict.items()), f, indent=2)
            
        time.sleep(2) # rate limit prevention

    # Audit Cover Wrap
    fn = "Cover_Wrap.png"
    img_path = os.path.join(images_dir, fn)
    if fn in results_dict and results_dict[fn].get("status") in ["PASS", "FAIL"]:
        print(f"⏭ Skipping {fn} - already audited with status: {results_dict[fn]['status']}")
    else:
        print("🔍 Auditing Cover_Wrap.png...")
        report = audit_image(img_path, "Full Cover Wrap", "The entire book wrap-around cover with front and back designs.")
        print(f"  Status: {report.get('status', 'FAIL')}")
        if report.get("issues"):
            print("  Issues Found:")
            for issue in report["issues"]:
                print(f"    - {issue}")
        else:
            print("  ✓ Meets all brand standards.")
        print("-" * 50)
        
        results_dict[fn] = report
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(list(results_dict.items()), f, indent=2)

    print("\n🎉 Brand Audit completed! Summary saved to Book1_Audit_Report.json")

if __name__ == "__main__":
    main()
