import os
import json
import base64
import time
import urllib.request
import urllib.error
import re
from PIL import Image as PILImage

# --- CONFIGURATION ---
API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
IMAGE_MODEL = "gemini-3.1-flash-image"
VISION_MODEL = "gemini-3.5-flash"

# OFFLINE-FIRST LOCAL STABLE DIFFUSION OPTIMIZATION
LOCAL_SD_MODE = os.environ.get("JORDAN_PRIDE_MODE", "local").lower() == "local"
SD_API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

ROOT_DIR = r"C:\Users\marti\JordanPrideBook_Series1_Final"
DESKTOP_DIR = ROOT_DIR
IMAGES_DIR = os.path.join(ROOT_DIR, "01_Final_Book_Assets")
BACKUP_DIR = os.path.join(ROOT_DIR, "01_Final_Book_Assets")
ANCHOR_PATH = r"C:\Users\marti\AppData\Local\hermes\cache\images\img_4f6728cd4318.jpg"
MANUSCRIPT_PATH = os.path.join(ROOT_DIR, "02_Publishing_Files", "The Jordan Pride - Book 1 Manuscript.md")
STATE_PATH = os.path.join(ROOT_DIR, "02_Publishing_Files", "production_state.json")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Load Master Anchor Image
FALLBACK_ANCHOR_PATH = r"C:\Users\marti\JordanPrideBook_Series1_Final\01_Final_Book_Assets\Page_12.png"
if os.path.exists(ANCHOR_PATH):
    print(f"🌟 Loading Master Anchor Image from {ANCHOR_PATH}")
    with open(ANCHOR_PATH, "rb") as f:
        ANCHOR_B64 = base64.b64encode(f.read()).decode("utf-8")
elif os.path.exists(FALLBACK_ANCHOR_PATH):
    print(f"🌟 Loading Fallback Master Anchor Image from {FALLBACK_ANCHOR_PATH}")
    ANCHOR_PATH = FALLBACK_ANCHOR_PATH
    with open(FALLBACK_ANCHOR_PATH, "rb") as f:
        ANCHOR_B64 = base64.b64encode(f.read()).decode("utf-8")
else:
    print(f"⚠️ Warning: Neither original nor fallback anchor image found!")
    ANCHOR_B64 = ""

# --- STEP 1: MANUSCRIPT PARSING & DYNAMIC PROMPT HARDENING ---
def load_character_bible():
    # Pre-defined locked character specifications from character_bible.md
    return {
        "Leo": {
            "name": "Leo Jordan",
            "desc": "Leo Jordan (6-year-old golden-furred anthropomorphic lion cub, tuft of reddish-brown hair on his head, big curious amber eyes, blue denim overalls over orange-and-white striped short-sleeve shirt, toy magnifying glass tucked in bib pocket, blue canvas sneakers with orange-striped socks).",
            "negative": "Leo is a boy cub and has absolutely NO ribbons, bows, flowers, or accessories in his hair or fur (simple messy reddish-brown head hair tuft only). Only Maya wears the purple ear bow ribbon."
        },
        "Maya": {
            "name": "Maya Jordan",
            "desc": "Maya Jordan (3-year-old cream-and-gold furred anthropomorphic lion cub, freckled snout, soft brown hair tuft, hazel eyes, bright purple ribbon ear bow behind her left ear, sunshine-yellow dress with crayon-filled pockets, pink sandals, clutching soft purple star plushie 'Glimmer').",
            "negative": ""
        },
        "Pop Pop": {
            "name": "Pop Pop",
            "desc": "Pop Pop Jordan (broad-shouldered grandfather anthropomorphic lion, silver-and-gold mane, kind amber eyes, red plaid flannel shirt with neatly rolled-up sleeves, dark khaki trousers, brass belt buckle with gold pocket watch chain, sturdy brown leather work boots).",
            "negative": ""
        },
        "Mom": {
            "name": "Mom",
            "desc": "Mom Jordan (petite, short anthropomorphic lioness with warm honey-toned fur, wearing comfortable teal tunic, leggings, and a small silver pendant shaped like a paw print).",
            "negative": ""
        },
        "Dad": {
            "name": "Dad",
            "desc": "Dad Jordan (tall, slim anthropomorphic lion with dark, thick mahogany mane, wearing navy blue mechanic's coveralls and retro high-top basketball sneakers).",
            "negative": ""
        }
    }

def detect_characters(scene_text):
    characters = []
    for char in ["Leo", "Maya", "Pop Pop", "Mom", "Dad"]:
        if re.search(r"\b" + char + r"\b", scene_text, re.IGNORECASE):
            characters.append(char)
    return characters

def build_hardened_prompt(page_num, page_title, scene_text, is_spread=True):
    # Programmatically sanitize raw scene text to neutralize AI triggers (like speech bubbles or human hands)
    sanitized_scene = scene_text
    sanitized_scene = re.sub(r'\bhands\b', 'paws', sanitized_scene, flags=re.IGNORECASE)
    sanitized_scene = re.sub(r'\bhand\b', 'paw', sanitized_scene, flags=re.IGNORECASE)
    sanitized_scene = re.sub(r'\bfingers\b', 'paw digits', sanitized_scene, flags=re.IGNORECASE)
    sanitized_scene = re.sub(r'\bfinger\b', 'paw digit', sanitized_scene, flags=re.IGNORECASE)
    # Strip all quotation marks to prevent the AI from generating comic-book speech bubbles
    sanitized_scene = sanitized_scene.replace('"', '').replace('“', '').replace('”', '').replace('`', '').replace("'", "")
    
    bible = load_character_bible()
    chars_present = detect_characters(sanitized_scene)
    
    # 1. Verbatim Style Prefix
    prompt = "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, warm golden savanna lighting. "
    
    if is_spread:
        prompt += f"Panoramic two-page spread (Pages {page_num} and {page_num+1}), clean composition keeping central gutter fold free of character faces and critical action. "
    else:
        prompt += f"Single-page storybook illustration (Page {page_num}), clear layout. "
    
    # 2. Scene Action & Environment Setup
    prompt += f"Scene Action: {sanitized_scene} "
    prompt += "Environment: A vibrant 'Big Family / Big Yard' setting with lush green grass, tall acacia trees, colorful blooming marigolds and red roses, sunny blue sky. "
    
    # 3. Add Character Descriptions
    for char in chars_present:
        prompt += f"Character Lock: {bible[char]['desc']} "
        if bible[char]['negative']:
            prompt += f"{bible[char]['negative']} "
            
    # 4. Strict Relative Size Constraint Matrix
    if "Leo" in chars_present and "Maya" in chars_present:
        prompt += (
            "CRITICAL SIZE & AGE PROPORTION RULE: Leo is a tall 6-year-old child cub. "
            "Maya is an extremely small, tiny 3-year-old toddler sister cub and MUST be significantly shorter and smaller than Leo, "
            "reaching only up to Leo's shoulder height or lower chest. Leo visibly towers over Maya. Maya is only half of Leo's size and height. "
            "Maya is NEVER equal in size or taller than Leo. "
        )
        
    # 5. Core Rules & Safe Zones
    prompt += (
        "CRITICAL RULE: 100% anthropomorphic animal universe. All figures must stand on two legs, wear clothes, and have animal paws instead of human hands. Zero humans, zero human-like skin, and zero human hands allowed. "
        "CRITICAL ANATOMY LOCK: Every hand must be a soft, furry animal paw with clear, simplified paw pads and soft claws, NOT smooth human skin, NOT human knuckles, and NOT human fingers. "
        "When a character is holding a prop (like a rag, cane, brush, or tool), their paw must naturally wrap around or grasp the object with a simplified 4-digit animal paw, NEVER showing human-like five-fingered hands or realistic human anatomy. "
    )
    
    if is_spread:
        prompt += "Layout constraints: central gutter of the spread must be clean and empty of any characters' faces or critical details. Provide open, soft low-contrast areas (like open sky or grass) on the left and right halves for text overlays. "
    else:
        prompt += "Layout constraints: leave generous open space above or below characters for text block. "
        
    # 6. Hardened Garden Marker Prop Lock
    if any(keyword in scene_text.lower() for keyword in ["marker", "post", "wood", "broken", "glue", "mended", "clamp", "splintered"]):
        prompt += (
            "CRITICAL PROP LOCK: The garden marker is a highly distinct, hand-carved oak post featuring a barber-pole style spiral twist groove winding top-to-bottom in natural oak finish. "
            "If the marker is broken, it must be depicted as two splintered pieces displaying this exact handcrafted spiral twisting groove pattern. "
            "The garden marker is NEVER a flat plank, NEVER a plastic drawing marker, and NEVER a plain post. "
        )
        
    prompt += "--v 6.0"
    if is_spread:
        prompt += " --ar 17:11"
    else:
        prompt += " --ar 8.5:11"
        
    return prompt

# --- STEP 2: IMAGE GENERATION (Stage 1 Execution) ---
def generate_image(prompt_text, aspect_ratio="17:11"): 
    if os.environ.get("JORDAN_PRIDE_MODE", "local").lower() == "local":
        w, h = (1360, 880) if "17:11" in prompt_text else (880, 1136)
        if "17.25:11.25" in prompt_text: w, h = 1380, 900
        
        payload = {
            "prompt": prompt_text,
            "negative_prompt": "3d render, photographic, extra limbs, deformed, blurry, low resolution, bad anatomy, human hands, human features",
            "steps": 25,
            "cfg_scale": 7.0,
            "width": w,
            "height": h,
            "sampler_name": "Euler a"
        }
        req = urllib.request.Request(
            SD_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            img_b64 = res["images"][0]
            return base64.b64decode(img_b64)

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL}:generateContent?key={API_KEY}"
    
    instruction = (
        "Generate a high-resolution, final publication-grade 2D digital storybook illustration with vibrant vector linework and soft cel shading. "
        "STRICT CHARACTER & STYLE CONTINUITY: You must match the visual style, fur tones, and character visual designs shown in the attached reference image. "
        f"Prompt instructions: {prompt_text}"
    )
    
    parts = [{"text": instruction}]
    if ANCHOR_B64:
        mime = "image/png" if ANCHOR_PATH.lower().endswith(".png") else "image/jpeg"
        parts.append({"inlineData": {"mimeType": mime, "data": ANCHOR_B64}})
        
    payload = {
        "contents": [{
            "parts": parts
        }]
    }
    
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    # Exponential backoff retry
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
    raise ValueError("Failed to generate image: No image found in response parts.")

# --- STEP 3: MULTIMODAL AUDIT (Stage 2 Execution) ---
def audit_image_file(image_path, title, prompt_text):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL}:generateContent?key={API_KEY}"
    
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
        endpoint,
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
                    if text_resp.startswith("```json"):
                        text_resp = text_resp[7:]
                    if text_resp.endswith("```"):
                        text_resp = text_resp[:-3]
                    text_resp = text_resp.strip()
                    return json.loads(text_resp)
        except Exception as e:
            if attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
            return {"status": "FAIL", "issues": [str(e)], "explanation": "Failed to parse API audit response."}

# --- STEP 4: STATE & FILE MANAGEMENT ---
def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=4)

def save_and_crop(fn, img_bytes, is_spread=True):
    filepath = os.path.join(IMAGES_DIR, fn)
    backup_path = os.path.join(BACKUP_DIR, fn)
    
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    with open(backup_path, "wb") as f:
        f.write(img_bytes)
        
    if is_spread:
        with PILImage.open(filepath) as im:
            w, h = im.size
            im.crop((0, 0, w // 2, h)).save(os.path.join(IMAGES_DIR, f"temp_left_{fn}"))
            im.crop((w // 2, 0, w, h)).save(os.path.join(IMAGES_DIR, f"temp_right_{fn}"))
    print(f"  ✓ Files saved and cropped for {fn}")

# --- CLOSED-LOOP AUTO-HEALING ORCHESTRATOR ---
def process_page(page_num, page_title, scene_text, is_spread=True):
    fn = f"Page_{page_num:02d}.png"
    state = load_state()
    
    if state.get(fn, {}).get("status") == "PASS":
        print(f"🎉 {fn} already passed audit. Skipping.")
        return True
        
    print(f"\n🚀 Processing {fn} ({page_title})...")
    
    # Generate dynamically hardened base prompt
    base_prompt = build_hardened_prompt(page_num, page_title, scene_text, is_spread)
    current_prompt = base_prompt
    history = []
    
    for iteration in range(1, 4):  # Up to 3 self-healing attempts
        print(f"  [Attempt {iteration}] Hardening prompt and generating image...")
        
        try:
            # Stage 1: Generate Image
            img_bytes = generate_image(current_prompt)
            save_and_crop(fn, img_bytes, is_spread)
            
            # Stage 2: Multimodal Audit
            filepath = os.path.join(IMAGES_DIR, fn)
            audit_result = audit_image_file(filepath, page_title, current_prompt)
            print(f"  Audit Status: {audit_result.get('status')}")
            
            # Save progress in state
            state[fn] = {
                "status": audit_result.get("status"),
                "issues": audit_result.get("issues", []),
                "explanation": audit_result.get("explanation"),
                "prompt_used": current_prompt,
                "timestamp": time.time(),
                "attempts": iteration
            }
            save_state(state)
            
            if audit_result.get("status") == "PASS":
                print(f"  ✨ PASS! {fn} is approved for publishing!")
                return True
                
            # Stage 3: Auto-Healing if FAIL
            issues_list = audit_result.get("issues", [])
            print(f"  ❌ FAIL. Identified issues: {issues_list}")
            
            history.append(issues_list)
            # Self-healing feedback addition
            healing_modifiers = ""
            for issue in issues_list:
                healing_modifiers += f"CORRECTION REQUIRED: {issue}. "
            
            # Rebuild a stricter prompt incorporating corrective actions
            current_prompt = f"{base_prompt} STRICT COMPLIANCE FIX: {healing_modifiers}"
            
        except Exception as e:
            print(f"  ⚠️ Error during iteration {iteration}: {e}")
            time.sleep(5)
            
    print(f"  ❌ Max healing attempts reached for {fn}. Manual review recommended.")
    return False

# --- RUN TEST CASE ---
if __name__ == "__main__":
    print("=== STARTING THE JORDAN PRIDE CLOSED-LOOP PRODUCTION ENGINE ===")
    test_title = "Spread 1 (Pages 4-5) - The Playful Leap & The Broken Marker"
    test_text = (
        "Leo Jordan leaps happily over green garden bushes. Maya watches from below. "
        "On the right, Pop Pop's wooden garden marker with a spiral twist pattern lies broken on the grass "
        "as Leo lands heavily."
    )
    success = process_page(4, test_title, test_text, is_spread=True)
    print(f"=== TEST RUN COMPLETE. SUCCESS: {success} ===")
