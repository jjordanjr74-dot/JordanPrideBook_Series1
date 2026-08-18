import os
import base64
import urllib.request
import urllib.error
import json
import time
from PIL import Image as PILImage

API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
AUDIT_MODEL = "gemini-3.5-flash"
GENERATE_MODEL = "gemini-3.1-flash-image"

AUDIT_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{AUDIT_MODEL}:generateContent?key={API_KEY}"
GENERATE_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GENERATE_MODEL}:generateContent?key={API_KEY}"

desktop_dir = r"C:\Users\marti\Desktop"
images_dir = os.path.join(desktop_dir, "The Jordan Pride - Book 1 Images")
backup_dir = r"D:\Jordan_Pride_Publishing_Library\Book_Assets"
report_file = os.path.join(desktop_dir, "Book1_Audit_Report.json")
state_file = os.path.join(desktop_dir, "production_state.json")
anchor_path = r"C:\Users\marti\AppData\Local\hermes\cache\images\img_4f6728cd4318.jpg"

os.makedirs(images_dir, exist_ok=True)
if os.path.exists("D:/"):
    os.makedirs(backup_dir, exist_ok=True)

# Load Master Anchor Image
if os.path.exists(anchor_path):
    with open(anchor_path, "rb") as f:
        anchor_b64 = base64.b64encode(f.read()).decode("utf-8")
else:
    anchor_b64 = ""
    print("⚠️ Master Anchor image not found!")

# Multi-modal Audit Image using 30-year veteran prompt
def audit_image(image_path, title, prompt_text):
    if not os.path.exists(image_path):
        return {"status": "FAIL", "issues": ["File missing on disk."]}
    
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

def update_databases(fn, res):
    # Book1_Audit_Report.json
    if os.path.exists(report_file):
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            
            report_dict = {item[0]: item[1] for item in report_data if isinstance(item, list) and len(item) == 2}
            report_dict[fn] = res
            new_report_data = [[k, v] for k, v in report_dict.items()]
            
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(new_report_data, f, indent=2)
            print(f"  ✓ Updated Book1_Audit_Report.json for {fn}")
        except Exception as e:
            print(f"  ⚠️ Error updating audit report: {e}")

    # production_state.json
    if os.path.exists(state_file) and fn.startswith("Page_") and fn != "Cover_Wrap.png":
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            
            existing = state_data.get(fn, {})
            state_data[fn] = {
                "status": res.get("status"),
                "issues": res.get("issues", []),
                "explanation": res.get("explanation", ""),
                "prompt_used": existing.get("prompt_used", ""),
                "timestamp": time.time(),
                "attempts": existing.get("attempts", 1) + 1
            }
            
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4)
            print(f"  ✓ Updated production_state.json for {fn}")
        except Exception as e:
            print(f"  ⚠️ Error updating production state: {e}")

# Target remaining 4 failed pages
targets = [
    {
        "filename": "Page_01.png",
        "title": "Page 1: Title Page Vignette",
        "issues": [
            "Pop Pop is off-center on the far right instead of in the center behind both children.",
            "Pop Pop's arms do not connect logically, with his left arm hanging straight down instead of resting on Maya's shoulder.",
            "Leo's toy magnifying glass is hanging at his hip instead of being inside his center chest bib pocket.",
            "The hands of both Leo and Pop Pop are too realistic and human-like instead of stylized round animal paws.",
            "Unrequested sunflowers/leaves are encroaching on the title text area."
        ],
        "hardened_prompt": (
            "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, warm savanna lighting. "
            "Title page vignette. Centered, perfectly symmetrical character portrait on a flat warm cream background (#FFFDF5). "
            "In the absolute center of the frame, Pop Pop Jordan (broad-shouldered grandfather lion, silver-and-gold mane, red plaid flannel shirt with rolled sleeves, dark khaki trousers, work boots, brass belt buckle, golden pocket watch chain) stands tall, proud, and perfectly centered behind both children. "
            "Pop Pop Jordan's large right paw rests gently on Leo's left shoulder, and his large left paw rests gently on Maya's right shoulder. Symmetrical protective posture. "
            "On Pop Pop's left side (the left side of the frame), Leo Jordan (6yo golden boy lion cub, unruly reddish-brown head hair tuft, amber eyes, blue denim overalls with a toy magnifying glass fully tucked inside his central bib pocket, orange-and-white striped t-shirt, blue canvas sneakers, NO hair ribbons) stands looking proud with his right paw placed firmly over his heart. "
            "On Pop Pop's right side (the right side of the frame), Maya Jordan (3yo cream-and-gold girl lion cub, snout freckles, hazel eyes, sunshine-yellow dress with front pockets, bright purple ear bow ribbon, pink sandals, clutching soft purple star plushie Glimmer) stands waving happily. Maya's head reaches only up to Leo's shoulder height. "
            "CRITICAL DESIGN RULES: 100% anthropomorphic animal universe. NO human hands, NO human fingers, NO human skin folds. All characters must have thick, rounded, fuzzy cartoon animal paws with soft pads. Leo has absolutely NO ribbons, bows, or accessories in his hair. Keep the upper 40% of the canvas completely clear warm cream space with absolutely no sunflower graphics or details, specifically reserved for title typography. Symmetrical composition."
        ),
        "is_spread": False
    },
    {
        "filename": "Page_04.png",
        "title": "Spread 1 (Pages 4-5): The Playful Leap & Broken Marker",
        "issues": [
            "The broken wooden marker on the right page is floating at a 45-degree angle instead of lying flat on the grass.",
            "Key background storytelling elements (red toy wagon, green garden hose, patio chairs, Pop Pop watering) are entirely missing.",
            "Leo's right hand exhibits minor anatomical rendering distortion, appearing slightly too human-like."
        ],
        "hardened_prompt": (
            "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, bright cheerful morning sunlight. "
            "Panoramic continuous two-page spread (Pages 4 and 5), clean composition keeping central gutter fold free of character faces and critical action. "
            "In the center of the left page, Leo Jordan (6yo golden boy lion cub, blue denim overalls over orange-and-white striped t-shirt, blue sneakers, NO hair ribbons) is in mid-air in a big, joyful leap over green garden bushes, with thick round cartoon paws (no human hands). "
            "Below him on the grass, tiny Maya Jordan (3yo girl lion cub, yellow dress, purple ear bow, pink sandals) sits clutching purple star plushie Glimmer. "
            "On the right page, Pop Pop's hand-carved oak garden marker is broken completely in half and lies flat on the grass, showing a clean wood splinter break. "
            "In the expansive garden background, Pop Pop Jordan in red plaid flannel shirt is watering flower beds in the distance with a green hose, next to a bright red wooden toy wagon overflowing with colorful balls, and two cozy green patio chairs on the lush green grass under a large acacia tree. "
            "CRITICAL DESIGN RULES: Pop Pop's broken wooden marker lies flat on the grass on the right page (not floating, not standing). No human hands or fingers allowed. Gutter vertical center line must be clean and free of figures. Leave open, low-contrast blue sky in the upper left and upper right for text overlays."
        ),
        "is_spread": True
    },
    {
        "filename": "Page_06.png",
        "title": "Spread 2 (Pages 6-7): The Shock & The Twisty Tummy",
        "issues": [
            "Aspect ratio is rendered at 1:1 instead of the required 17:11 panoramic layout.",
            "Maya's yellow dress lacks deep front crayon pockets.",
            "Identical duplication of the broken wooden garden marker across both pages.",
            "Split-frame panel layout instead of a seamless, continuous panoramic double-page spread."
        ],
        "hardened_prompt": (
            "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, dramatic warm afternoon lighting. "
            "Panoramic continuous two-page spread (Pages 6 and 7) with a seamless, single-frame layout (no panels, no split frames, no border dividers), clean composition keeping central gutter fold free of characters. "
            "On the left page, Leo Jordan (6yo golden boy lion cub, blue denim overalls, orange-striped t-shirt, blue sneakers, no ribbons) is scrambling backward on his hands and knees on the grass, wide amber eyes staring in shock. Next to him, Pop Pop's hand-carved oak garden marker is broken in half and lying flat on the grass. "
            "Maya Jordan (3yo girl lion cub, yellow dress with deep front pockets stuffed with crayons, purple ear bow, pink sandals) is rushing to Leo's side with a worried, sympathetic expression, placing a comforting paw on Leo's arm. "
            "On the right page, a medium close-up of Leo Jordan clutching his stomach with both paws, looking fearful with small comic swirl lines around his belly illustrating a 'twisty tummy', glancing nervously toward a pile of dry leaves. "
            "CRITICAL DESIGN RULES: Seamless panoramic layout --ar 17:11. Pop Pop's broken wooden marker is shown once on the left page (never duplicate it on the right page). Maya's yellow dress has two large visible pockets with crayons. Stylized round animal paws with pads; strictly prohibit human hands or fingers. Center gutter remains empty."
        ),
        "is_spread": True
    },
    {
        "filename": "Page_14.png",
        "title": "Spread 11 (Pages 24-25): Peaceful Heart & Cozy Dinner",
        "issues": [
            "Leo is missing from the family dinner scene on the right page.",
            "Adult characters (Mom, Dad, Pop Pop) have smooth, five-fingered human-like hands.",
            "Mom's tunic is olive green instead of teal, and she is missing her silver paw-print pendant.",
            "Pop Pop's shirt lacks the distinct red plaid/flannel pattern.",
            "Dad is wearing a light blue short-sleeved shirt instead of navy mechanic coveralls."
        ],
        "hardened_prompt": (
            "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, warm lighting. "
            "Panoramic continuous two-page spread (Pages 24 and 25), clean composition keeping central gutter fold free of character faces and critical action. "
            "On the left page, Leo Jordan (6yo golden boy cub in blue overalls) runs joyfully through the sunny garden grass with outstretched arms, surrounded by glowing sparkles. "
            "On the right page, cozy indoor evening scene around a long wooden dining table under a hanging lantern. Exactly five distinct characters sit at the table eating dinner together happily: "
            "Mom Jordan (petite lioness, warm honey fur, teal tunic blouse, silver paw-print pendant, black leggings) and Dad Jordan (tall lion, mahogany mane, navy mechanic coveralls) sit on one side. "
            "On the opposite side, Pop Pop Jordan (wearing a bright red plaid flannel long-sleeve shirt with rolled sleeves) sits on the wooden bench with tiny Maya Jordan (3yo toddler girl cub, cream fur, purple ear bow, yellow dress) sitting on Pop Pop's lap holding star Glimmer. "
            "Leo Jordan (6yo boy cub in blue overalls, striped t-shirt, simple messy hair tuft with NO ribbons) sits next to Pop Pop on the bench. "
            "CRITICAL DESIGN RULES: Exactly 5 characters present. Every character has thick, rounded, furry cartoon animal paws; under no circumstances should there be any human fingers or smooth five-fingered hands. Pop Pop's shirt must have distinct red-and-dark-gray checkered plaid pattern. Mom must wear a teal tunic with a silver paw pendant. Dad must wear navy coveralls. Sibling sizes are accurate, with Maya appearing extremely small on Pop Pop's lap."
        ),
        "is_spread": True
    }
]

def run_surgical_heal():
    print("==================================================")
    print("🔬 INITIALIZING VETERAN SURGICAL HEALING ENGINE 🔬")
    print("==================================================")
    
    for t in targets:
        fn = t["filename"]
        title = t["title"]
        prompt = t["hardened_prompt"]
        issues = t["issues"]
        
        print(f"\n🔬 Processing Surgical Heal for {fn} ({title})...")
        print(f"  Target Issues to Overcome: {issues}")
        
        current_prompt = prompt
        healed = False
        
        for attempt in range(1, 4):
            print(f"  [Attempt {attempt}/3] Generating conditioned image...")
            try:
                img_bytes = generate_conditioned_image(current_prompt)
                
                # Temporary save
                temp_path = os.path.join(images_dir, f"temp_audit_{fn}")
                with open(temp_path, "wb") as f:
                    f.write(img_bytes)
                
                print(f"  [Attempt {attempt}/3] Performing 30-year veteran audit on candidate...")
                audit_result = audit_image(temp_path, title, prompt)
                print(f"  Audit Status: {audit_result.get('status')}")
                
                if audit_result.get("status") == "PASS":
                    print(f"  ✨ SUCCESS! {fn} has passed the strict veteran audit!")
                    os.replace(temp_path, os.path.join(images_dir, fn))
                    save_and_split(fn, img_bytes, is_spread=t["is_spread"])
                    update_databases(fn, audit_result)
                    healed = True
                    break
                else:
                    new_issues = audit_result.get("issues", [])
                    print(f"  ❌ FAIL. Remaining/New Issues: {new_issues}")
                    # Compound hardening based on new audit feedback
                    print("  Hardening prompt further with new audit feedback...")
                    current_prompt = auto_harden_prompt(current_prompt, new_issues)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            except Exception as e:
                print(f"  ⚠️ Error during generation/audit: {e}")
                time.sleep(2)
                
        if not healed:
            print(f"  ❌ Max attempts reached for {fn}. It remains in FAIL state. Moving to next target.")
            
    print("\n==================================================")
    print("🎉 SURGICAL HEALING CYCLE COMPLETE!")
    print("==================================================")

if __name__ == "__main__":
    run_surgical_heal()
