import os
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
    
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
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
    raise ValueError("Image-to-image repair failed.")

def audit_image(image_path, title, prompt_text):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL}:generateContent?key={API_KEY}"
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    audit_instruction = (
        "You are an Elite Executive Children's Book Editor. Audit this picture book page illustration.\n"
        "1. PROPORTION MATRIX: Leo is a tall 6yo brother. Maya is a tiny 3yo toddler (shoulder height or lower).\n"
        "2. ANTHROPOMORPHIC: All figures walk on two legs, wear clothes, and have 4-digit furry animal paws (NO 5-fingered human hands).\n"
        "3. NO TEXT: Zero text, letters, or speech bubbles.\n"
        f"Title: {title}\nPrompt: {prompt_text}\n"
        "Respond ONLY in valid JSON: {\"status\": \"PASS\" or \"FAIL\", \"issues\": [...], \"explanation\": \"...\"}"
    )

    payload = {"contents": [{"parts": [{"text": audit_instruction}, {"inlineData": {"mimeType": "image/png", "data": img_b64}}]}]}
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        text_out = res.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        # Clean JSON
        text_clean = text_out.strip()
        if text_clean.startswith("```json"):
            text_clean = text_clean[7:]
        if text_clean.endswith("```"):
            text_clean = text_clean[:-3]
        return json.loads(text_clean.strip())

if __name__ == "__main__":
    page_num = 18
    fn = f"Page_{page_num:02d}.png"
    img_path = os.path.join(IMAGES_DIR, fn)
    print(f"Testing targeted image-to-image repair on {fn}...")
    
    instruction = "Refine Dad's left paw resting on Leo's shoulder so it is a soft, furry 4-digit animal paw with paw pads, and remove any background tool board distortions."
    repaired_bytes = edit_image(img_path, instruction)
    
    # Save repaired image
    with open(img_path, "wb") as f:
        f.write(repaired_bytes)
        
    # Crop if spread
    with PILImage.open(img_path) as im:
        w, h = im.size
        im.crop((0, 0, w // 2, h)).save(os.path.join(IMAGES_DIR, f"temp_left_{fn}"))
        im.crop((w // 2, 0, w, h)).save(os.path.join(IMAGES_DIR, f"temp_right_{fn}"))
        
    print("Saved repaired image. Running audit...")
    audit = audit_image(img_path, f"Page {page_num}", instruction)
    print("Audit result:", audit)
    
    # Update state
    with open(STATE_PATH, "r") as f:
        state = json.load(f)
    state[fn] = {
        "status": audit.get("status"),
        "issues": audit.get("issues", []),
        "explanation": audit.get("explanation"),
        "timestamp": time.time()
    }
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=4)
