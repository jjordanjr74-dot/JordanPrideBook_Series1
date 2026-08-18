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

desktop_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final"
images_dir = os.path.join(desktop_dir, "01_Final_Book_Assets")
fallback_anchor = os.path.join(images_dir, "Page_12.png")
state_path = os.path.join(desktop_dir, "02_Publishing_Files", "production_state.json")

os.makedirs(images_dir, exist_ok=True)

anchor_b64 = None
anchor_mime = "image/png"
if os.path.exists(fallback_anchor):
    print(f"🌟 Loading Master Anchor Image from {fallback_anchor}")
    with open(fallback_anchor, "rb") as f:
        anchor_b64 = base64.b64encode(f.read()).decode("utf-8")

hardened_prompt = (
    "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, warm cozy dining room lighting. "
    "Panoramic continuous two-page spread (Pages 24 and 25), clean composition keeping central gutter fold free of character faces and critical action. "
    "Scene Action: A warm family dinner inside the Jordan family home. On the left page, Leo Jordan (6yo golden boy lion cub, blue denim overalls over orange-and-white striped short-sleeve shirt, 4-digit furry paws) sits at the dining table holding a spoon with soft cartoon paws. "
    "On the right page, Dad Jordan, Mom Jordan, Pop Pop Jordan, and tiny Maya Jordan (3yo toddler girl cub in yellow dress with purple ear bow) sit together at the wooden dinner table. "
    "CRITICAL BRAND SAFETY & ANATOMICAL RULES: Exactly 100% anthropomorphic animal universe. Every character (Leo, Maya, Mom, Dad, Pop Pop) stands on two legs and has soft, 4-digit furry lion paws with rounded paw pads (STRICTLY 4 DIGITS, NO 5-fingered human hands, NO human skin texture). "
    "CRITICAL CAST LOCK: Exactly 5 characters total (Leo, Maya, Mom, Dad, Pop Pop). Do NOT add any extra characters or extra cubs. "
    "CRITICAL PROPORTION MATRIX: Leo is a tall 6yo brother. Maya is a tiny 3yo toddler cub. "
    "Leo has absolutely NO ribbons or bows in his hair. ONLY Maya wears the bright purple ear bow."
)

instruction = (
    "Generate a high-resolution, final publication-grade 2D digital storybook illustration with vibrant vector linework and soft cel shading. "
    "STRICT CHARACTER & ATTIRE CONTINUITY: Copy exactly the character visual identity, fur tone, and outfit designs shown in reference image. "
    f"Scene Action: {hardened_prompt}"
)

parts = [{"text": instruction}]
if anchor_b64:
    parts.append({"inlineData": {"mimeType": anchor_mime, "data": anchor_b64}})

payload = {"contents": [{"parts": parts}]}
req = urllib.request.Request(GENERATE_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})

print("🎨 Generating fresh Page_24.png candidate...")
for attempt in range(5):
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            candidates = res.get("candidates", [])
            if candidates:
                parts_out = candidates[0].get("content", {}).get("parts", [])
                for part in parts_out:
                    if "inlineData" in part:
                        img_bytes = base64.b64decode(part["inlineData"]["data"])
                        img_path = os.path.join(images_dir, "Page_24.png")
                        with open(img_path, "wb") as f:
                            f.write(img_bytes)
                        print("  ✓ Saved fresh Page_24.png. Running audit...")
                        
                        # Audit
                        audit_payload = {"contents": [{"parts": [
                            {"text": f"You are an Elite Executive Children's Book Editor. Audit this picture book page illustration under a microscopic lens.\n1. PROPORTION MATRIX: Leo is tall 6yo brother, Maya is tiny 3yo toddler.\n2. 100% ANTHROPOMORPHIC: All figures walk on two legs, wear clothes, and have 4-digit furry animal paws (NO 5-fingered human hands).\n3. NO EXTRA CHARACTERS: Exactly 5 characters (Leo, Maya, Mom, Dad, Pop Pop).\nTitle: Page 24\nRespond ONLY in valid JSON: {{\"status\": \"PASS\" or \"FAIL\", \"issues\": [...], \"explanation\": \"...\"}}"},
                            {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(img_bytes).decode("utf-8")}}
                        ]}]}
                        audit_req = urllib.request.Request(AUDIT_ENDPOINT, data=json.dumps(audit_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(audit_req, timeout=60) as a_resp:
                            a_res = json.loads(a_resp.read().decode("utf-8"))
                            text_out = a_res.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            if text_out.startswith("```json"): text_out = text_out[7:]
                            if text_out.endswith("```"): text_out = text_out[:-3]
                            audit_data = json.loads(text_out.strip())
                            print(f"  Audit Status: {audit_data.get('status')}")
                            if audit_data.get("issues"):
                                print(f"  Issues: {audit_data.get('issues')}")
                            
                            with open(state_path, "r") as sf:
                                state = json.load(sf)
                            state["Page_24.png"] = {
                                "status": audit_data.get("status"),
                                "issues": audit_data.get("issues", []),
                                "explanation": audit_data.get("explanation"),
                                "timestamp": time.time(),
                                "attempts": state.get("Page_24.png", {}).get("attempts", 0) + 1
                            }
                            with open(state_path, "w") as sf:
                                json.dump(state, sf, indent=4)
                        break
    except Exception as e:
        if attempt < 4:
            time.sleep(2)
            continue
        print(f"Generation error: {e}")
