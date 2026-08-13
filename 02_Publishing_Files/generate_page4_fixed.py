import os
import base64
import urllib.request
import json
import time
from PIL import Image as PILImage

API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
AUDIT_MODEL = "gemini-3.5-flash"
GENERATE_MODEL = "gemini-2.5-flash-image"

AUDIT_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{AUDIT_MODEL}:generateContent?key={API_KEY}"
GENERATE_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GENERATE_MODEL}:generateContent?key={API_KEY}"

desktop_dir = r"C:\Users\marti\Desktop"
images_dir = os.path.join(desktop_dir, "The Jordan Pride - Book 1 Images")
backup_dir = r"D:\Jordan_Pride_Publishing_Library\Book_Assets"
anchor_path = r"C:\Users\marti\AppData\Local\hermes\cache\images\img_4f6728cd4318.jpg"

os.makedirs(images_dir, exist_ok=True)
if os.path.exists("D:/"):
    os.makedirs(backup_dir, exist_ok=True)

# Load Master Anchor Image
with open(anchor_path, "rb") as f:
    anchor_b64 = base64.b64encode(f.read()).decode("utf-8")

hardened_prompt = (
    "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, bright cheerful morning sunlight. "
    "Panoramic continuous two-page spread (Pages 4 and 5), clean composition keeping central gutter fold free of character faces and critical action. "
    "On the left page, Leo Jordan (6yo golden boy lion cub, blue denim overalls, orange-and-white horizontally striped t-shirt, blue sneakers, NO hair ribbons) is in mid-air in a big, joyful pounce leap over green garden bushes. "
    "Below him on the green grass, Maya Jordan (3yo girl lion cub, yellow dress, bright purple ear bow ribbon behind her left ear, pink sandals) sitting happily cheering him on holding purple star plushie Glimmer. "
    "On the far right page, Pop Pop's hand-carved oak garden marker is broken in half and lies flat on the grass. The marker post features a distinct hand-carved barber-pole style spiral twist groove winding top-to-bottom. "
    "In the background, an expansive yard with Pop Pop Jordan (red plaid flannel shirt) watering flower beds with a green hose in the distance, Auntie Willow's green patio chairs on the lawn, and a bright red toy wagon. "
    "CRITICAL BRAND SAFETY & TEXT LEGIBILITY RULES: Exactly 100% anthropomorphic animal universe. NO human hands or fingers. Paws must be rounded, soft cartoon animal paws. "
    "The garden marker post is broken in half and lies flat on the grass on the right page, and MUST feature the highly distinct, hand-carved barber-pole style spiral twisting groove running top-to-bottom (natural oak finish). "
    "TEXTSAFE CLEARANCE: In the lower 25% of both the left and right pages, the background must transition to a very soft, flat, low-contrast warm cream-toned grass clearing with minimal grass details, designed as an open text-safe zone for readable text overlay. "
    "Gutter fold must be clean and free of characters. --ar 17:11 --v 6.0"
)

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

def audit_image(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    audit_instruction = (
        "You are an Elite Executive Children's Book Editor and Publishing Director with 30 years of experience in high-end publishing. "
        "Your eye for detail is legendarily meticulous. You are auditing a draft illustration for 'The Jordan Pride' children's picture book series "
        "against strict brand guidelines, narrative continuity, layout compliance, and visual perfection.\n\n"
        "--- CRITICAL BRAND AUDIT CRITERIA (NO EXCEPTIONS ALLOWED) ---\n"
        "1. PROPORTION MATRIX: Leo must be a tall 6yo child cub, Maya is a tiny 3yo toddler. Maya reaches only up to Leo's shoulder height.\n"
        "2. ACCESSIBLE ATTRIBUTES & HAIR LOCKS: Leo has a simple reddish-brown head hair tuft and NO ribbons, bows, or flowers. Only Maya wears the purple ear bow.\n"
        "3. 100% ANTHROPOMORPHIC UNIVERSE: All characters must have thick, rounded cartoon animal paws with soft pads. Zero human fingers or knuckles allowed.\n"
        "4. ATTIRE RECOGNITION: Pop Pop must wear his red plaid flannel shirt with rolled sleeves.\n"
        "5. KEY PROP DESIGN: Pop Pop's garden marker must have a highly distinct, hand-carved barber-pole style spiral twist groove winding top-to-bottom (natural oak).\n"
        "6. PRINT COMPLIANCE & TEXT OVERLAY SAFE ZONES: Ensure there is a low-contrast, uncluttered, simple open background space (like clear sky, soft grass) in the lower 25% specifically reserved for text overlay.\n\n"
        "Scene Title: Pages 4 & 5 (Spread 1): The Playful Leap & Broken Marker\n"
        f"Scene Prompt: {hardened_prompt}\n\n"
        "Respond ONLY in valid, parseable JSON format. Use this schema:\n"
        "{\n"
        "  \"status\": \"PASS\" or \"FAIL\",\n"
        "  \"issues\": [\"list of specific, distinct visual errors, contradictions, or deficiencies found\"],\n"
        "  \"explanation\": \"A comprehensive, professional, 30-year veteran level editorial critique.\"\n"
        "}"
    )

    payload_audit = {
        "contents": [{
            "parts": [
                {"text": audit_instruction},
                {"inlineData": {"mimeType": "image/png", "data": img_b64}}
            ]
        }]
    }

    req = urllib.request.Request(AUDIT_ENDPOINT, data=json.dumps(payload_audit).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        text_resp = res["candidates"][0]["content"]["parts"][0]["text"].strip()
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
        return json.loads(text_resp.strip())

def main():
    print("🚀 Sending generation request to Google AI Studio for Page 4 (Spread 1)...")
    req = urllib.request.Request(GENERATE_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        parts = res["candidates"][0]["content"]["parts"]
        for part in parts:
            if "inlineData" in part:
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                break

    fn = "Page_04.png"
    filepath = os.path.join(images_dir, fn)
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    if os.path.exists("D:/"):
        with open(os.path.join(backup_dir, fn), "wb") as f:
            f.write(img_bytes)

    print(f"✅ Successfully generated Page_04.png!")
    
    # Audit
    print("🔬 Running 30-year veteran audit on candidate...")
    report = audit_image(filepath)
    print(f"📊 Audit Status: {report['status']}")
    print(f"  Issues Found: {report.get('issues', [])}")
    print(f"  Explanation: {report.get('explanation')}")
    
    if report["status"] == "PASS":
        # Split image
        with PILImage.open(filepath) as im:
            w, h = im.size
            im.crop((0, 0, w // 2, h)).save(os.path.join(images_dir, f"temp_left_{fn}"))
            im.crop((w // 2, 0, w, h)).save(os.path.join(images_dir, f"temp_right_{fn}"))
            
            if os.path.exists("D:/"):
                im.crop((0, 0, w // 2, h)).save(os.path.join(backup_dir, f"temp_left_{fn}"))
                im.crop((w // 2, 0, w, h)).save(os.path.join(backup_dir, f"temp_right_{fn}"))
        print("  💾 Saved and split Page_04.png successfully!")

    # Update databases
    report_file = os.path.join(desktop_dir, "Book1_Audit_Report.json")
    state_file = os.path.join(desktop_dir, "production_state.json")

    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        report_dict = {item[0]: item[1] for item in report_data}
        report_dict["Page_04.png"] = report
        new_report = [[k, v] for k, v in report_dict.items()]
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(new_report, f, indent=2)

    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state_data = json.load(f)
        existing = state_data.get("Page_04.png", {})
        state_data["Page_04.png"] = {
            "status": report["status"],
            "issues": report.get("issues", []),
            "explanation": report.get("explanation"),
            "prompt_used": hardened_prompt,
            "timestamp": time.time(),
            "attempts": existing.get("attempts", 1) + 1
        }
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4)

if __name__ == "__main__":
    main()
