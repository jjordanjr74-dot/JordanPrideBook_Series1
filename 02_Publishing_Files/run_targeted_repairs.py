import os
import sys
import json
import base64
import time
import urllib.request
import urllib.error
from PIL import Image as PILImage

API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
IMAGE_MODEL = "gemini-3.1-flash-image"
VISION_MODEL = "gemini-3.5-flash"

ROOT_DIR = r"C:\Users\marti\JordanPrideBook_Series1_Final"
IMAGES_DIR = os.path.join(ROOT_DIR, "01_Final_Book_Assets")
STATE_PATH = os.path.join(ROOT_DIR, "02_Publishing_Files", "production_state.json")

def edit_image(source_image_path, edit_instruction):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL}:generateContent?key={API_KEY}"
    
    with open(source_image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    mime = "image/png" if source_image_path.lower().endswith(".png") else "image/jpeg"
    
    parts = [
        {"text": f"You are an expert children's book illustrator. Perform a precise image-to-image edit on the provided input illustration according to these instructions: {edit_instruction}. Maintain 100% style, character design, background, and lighting continuity. Do NOT add any text or speech bubbles."},
        {"inlineData": {"mimeType": mime, "data": img_b64}}
    ]
    
    payload = {"contents": [{"parts": parts}]}
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                candidates = res.get("candidates", [])
                if candidates:
                    parts_out = candidates[0].get("content", {}).get("parts", [])
                    for part in parts_out:
                        if "inlineData" in part:
                            return base64.b64decode(part["inlineData"]["data"])
        except urllib.error.HTTPError as e:
            if e.code in [503, 429] and attempt < 4:
                time.sleep(2 ** (attempt + 1))
                continue
            raise e
    raise ValueError("Image repair failed.")

def audit_image(image_path, title):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL}:generateContent?key={API_KEY}"
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    audit_instruction = (
        "You are an Elite Executive Children's Book Editor and Publishing Director with 30 years of experience in high-end publishing. "
        "Audit this children's picture book page illustration under a microscopic lens.\n\n"
        "1. PROPORTION MATRIX: Leo is a tall 6yo brother. Maya is a tiny 3yo toddler (shoulder height or lower). "
        "Maya must never appear equal in height or body mass to Leo.\n"
        "2. 100% ANTHROPOMORPHIC: All characters walk on two legs, wear clothes, and have 4-digit furry animal paws (NO 5-fingered human hands).\n"
        "3. CHARACTER ATTIRE & LOCK: Leo wears blue denim overalls over an orange-striped t-shirt with NO hair bows. ONLY Maya wears the purple ear bow ribbon.\n"
        "4. PRINT SAFETY & NO TEXT: Zero text, letters, or speech bubbles. Keep center gutter free of faces on double-page spreads.\n\n"
        f"Title: {title}\n"
        "Respond ONLY in valid, parseable JSON format: {\"status\": \"PASS\" or \"FAIL\", \"issues\": [\"specific issues...\"], \"explanation\": \"editorial review...\"}"
    )

    payload = {"contents": [{"parts": [{"text": audit_instruction}, {"inlineData": {"mimeType": "image/png", "data": img_b64}}]}]}
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                text_out = res.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text_clean = text_out.strip()
                if text_clean.startswith("```json"):
                    text_clean = text_clean[7:]
                if text_clean.endswith("```"):
                    text_clean = text_clean[:-3]
                return json.loads(text_clean.strip())
        except Exception as e:
            if attempt < 4:
                time.sleep(2)
                continue
            return {"status": "FAIL", "issues": [str(e)], "explanation": "Audit request error."}

REPAIR_PLAN = {
    18: "Redraw Page 18-19: Show Dad Jordan with his arm around Leo Jordan, while tiny Maya Jordan (3-year-old toddler with purple ear bow in her yellow dress) stands right beside Leo looking up at Dad. Ensure Dad's paw resting on Leo's shoulder is a golden-furred 4-digit lion paw matching his arm. Position Dad and Leo cleanly away from the central gutter crease.",
    22: "Specifically fix Leo's right hand resting on his chest: change it from 5 fingers to a simplified, soft 4-digit furry lion paw (one thumb pad and three finger pads) with golden fur on top. Ensure Maya remains present once and all characters have furry 4-digit paws.",
    24: "Simplify every character's hand (Leo, Dad, Pop Pop, Mom, Maya) into a smooth, 4-digit golden-furred mitten paw. Ensure no hand has human fingers or more than 4 digits.",
    26: "Fix character duplication and waving paw: Remove the extra duplicate Leo from the left page. Leo Jordan appears ONLY ONCE standing next to tiny Maya under the starry savanna night sky. Correct Leo's raised waving hand to be a soft, 4-digit furry lion paw with clear paw pads.",
    29: "Correct Pop Pop's hands holding the book and Maya's raised paw to be soft, furry 4-digit animal paws with clear paw pads.",
    31: "Focus exclusively on the adult lion in the red plaid shirt (top right circular badge): change his raised right paw so it shows strictly 3 finger pads plus 1 thumb pad (TOTAL 4 PADS, no 5th pink pad). Ensure his paw is a soft 4-digit furry lion paw."
}

def repair_single(p_num):
    if p_num not in REPAIR_PLAN:
        print(f"No repair plan for page {p_num}")
        return
        
    instruction = REPAIR_PLAN[p_num]
    fn = f"Page_{p_num:02d}.png"
    img_path = os.path.join(IMAGES_DIR, fn)
    is_spread = p_num in range(4, 28)
    
    print(f"\n🎨 Executing Targeted Image-to-Image Repair on {fn}...")
    print(f"  Instruction: {instruction}")
    
    repaired_bytes = edit_image(img_path, instruction)
    
    with open(img_path, "wb") as f:
        f.write(repaired_bytes)
        
    if is_spread:
        with PILImage.open(img_path) as im:
            w, h = im.size
            im.crop((0, 0, w // 2, h)).save(os.path.join(IMAGES_DIR, f"temp_left_{fn}"))
            im.crop((w // 2, 0, w, h)).save(os.path.join(IMAGES_DIR, f"temp_right_{fn}"))
            
    print(f"  ✓ Saved repaired {fn}. Running audit...")
    audit = audit_image(img_path, f"Page {p_num}")
    print(f"  Audit Status: {audit.get('status')}")
    if audit.get("issues"):
        print(f"  Issues: {audit.get('issues')}")
        
    with open(STATE_PATH, "r") as f:
        state = json.load(f)
        
    state[fn] = {
        "status": audit.get("status"),
        "issues": audit.get("issues", []),
        "explanation": audit.get("explanation"),
        "timestamp": time.time(),
        "attempts": state.get(fn, {}).get("attempts", 0) + 1
    }
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        repair_single(int(sys.argv[1]))
    else:
        for p in [18, 22, 24, 26, 29, 31]:
            repair_single(p)
