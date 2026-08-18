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
backup_dir = os.path.join(desktop_dir, "01_Final_Book_Assets")
anchor_path = r"C:\Users\marti\AppData\Local\hermes\cache\images\img_4f6728cd4318.jpg"
fallback_anchor = os.path.join(images_dir, "Page_12.png")

os.makedirs(images_dir, exist_ok=True)

# Load Master Anchor Image dynamically
anchor_mime = "image/jpeg"
if os.path.exists(anchor_path):
    print(f"🌟 Loading Master Anchor Image from {anchor_path}")
    anchor_mime = "image/jpeg"
    with open(anchor_path, "rb") as f:
        anchor_b64 = base64.b64encode(f.read()).decode("utf-8")
elif os.path.exists(fallback_anchor):
    print(f"🌟 Loading Fallback Master Anchor Image from {fallback_anchor}")
    anchor_mime = "image/png"
    with open(fallback_anchor, "rb") as f:
        anchor_b64 = base64.b64encode(f.read()).decode("utf-8")
else:
    anchor_b64 = None
    print("⚠️ Master Anchor image not found! Reference conditioning will be skipped.")

# Super-hardened prompt addressing Spread 8-9 audit failures
hardened_prompt = (
    "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, warm morning light. "
    "Panoramic continuous two-page spread (Pages 8 and 9), clean composition keeping central gutter fold free of character faces and critical action. "
    "On the left page, Maya Jordan (3yo girl lion cub, yellow dress with crayon pockets, purple ear bow behind left ear, pink sandals) is sitting flat on the soft green lawn grass, clutching her soft purple star plushie Glimmer, looking up at her brother Leo Jordan (6yo golden boy lion cub, overalls, striped shirt) who is standing proudly next to her. Placing a gentle paw on Leo's leg with sisterly comfort. "
    "Pop Pop's hand-carved oak garden marker is a simple round wooden stake post snapped cleanly into two broken pieces, lying flat in the grass between them. It MUST feature the highly distinct, hand-carved barber-pole style spiral twisting vine groove running from top to bottom on the wood surface. There is absolutely no text, no lettering, no signs, and no words written or carved on the wood. "
    "On the right page, Pop Pop Jordan (broad-shouldered grandfather lion, silver-and-gold mane, red plaid flannel shirt with rolled sleeves, dark khaki trousers, work boots) walking down the garden gravel path. Pop Pop is holding his wooden walking cane, with his right paw gripping the cane shaft cleanly using thick, rounded, fuzzy cartoon paws. Pop Pop is looking down toward the grass in surprise. "
    "CRITICAL PROPORTION MATRIX: Leo is standing tall. Maya is sitting flat on the grass on the left. Because Maya is a tiny 3yo toddler sitting flat on the grass, she is extremely small and petite compared to her standing brother Leo. This creates an absolute visual scale contrast. "
    "CRITICAL BRAND SAFETY & ANATOMICAL RULES: Exactly 100% anthropomorphic animal universe. NO human hands, smooth fingers, or human knuckles. All paws must be rounded, soft, fuzzy cartoon animal paws. Leo has absolutely NO ribbons, bows, or flowers on his head. ONLY Maya wears the bright purple ear bow. "
    "CRITICAL TEXTSAFE CLEARANCE: The lower 25% of BOTH the left and right pages of this panoramic spread must be a completely identical, flat, uniform, solid warm cream-colored (#FFFDF5) background space with absolutely no grass blades, no rose bushes, and no details, specifically designed for highly readable text overlays."
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
            {"inlineData": {"mimeType": anchor_mime, "data": anchor_b64}}
        ]
    }]
}

def audit_image(image_path):
    if not os.path.exists(image_path):
        return {"status": "MISSING", "explanation": "File does not exist."}
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    audit_instruction = (
        "You are an Elite Executive Children's Book Editor and Publishing Director with 30 years of experience in high-end publishing. "
        "Your eye for detail is legendarily meticulous. You are auditing a double-page spread illustration for 'The Jordan Pride' children's picture book series "
        "against strict brand guidelines, narrative continuity, layout compliance, and visual perfection.\n\n"
        "--- CRITICAL BRAND AUDIT CRITERIA (NO EXCEPTIONS ALLOWED) ---\n"
        "1. PROPORTION MATRIX: Leo (6yo brother) must be a tall child cub. Maya (3yo sister) is a tiny toddler. "
        "Whenever both appear on the page, Maya MUST be dramatically smaller and shorter than Leo. Her head must only reach up to Leo's shoulder, waist, or hip height. "
        "Maya must never appear to be equal in height, equal in body mass, or taller than Leo.\n"
        "2. ACCESSIBLE ATTRIBUTES & HAIR LOCKS: Leo is a male cub. He has a simple, messy reddish-brown head hair tuft. "
        "Leo must have absolutely NO ribbons, bows, flowers, barrettes, or accessories in his hair or fur. "
        "Only Maya wears the bright purple ear bow ribbon. Verify that Leo does not have a bow and Maya does.\n"
        "3. 100% ANTHROPOMORPHIC UNIVERSE: Every character must be an upright, bipedal animal walking on two legs, wearing stylish clothing. "
        "There must be zero human beings, human faces, or human skin/hands. "
        "Hands must be animal paws with fur, claws, or paw pads—never human-like smooth five-fingered hands.\n"
        "4. ATTIRE RECOGNITION & PATTERN CONSISTENCY: \n"
        "   - Leo: blue denim overalls over an orange-and-white striped t-shirt. Stripes must be horizontal and clear, not plaid or scrambled.\n"
        "   - Maya: sunshine-yellow dress with deep front crayon pockets, pink sandals.\n"
        "   - Pop Pop: Red plaid/flannel long-sleeve shirt with rolled sleeves, dark khaki trousers, leather boots.\n"
        "5. PROP SPATIAL MECHANICS & LOGIC: \n"
        "   - Pop Pop's garden marker has a highly distinct, hand-carved barber-pole style spiral twist groove winding top-to-bottom. "
        "   - If the marker is broken, it must be shown lying flat in two pieces in the grass.\n"
        "6. ANATOMICAL INTEGRITY: Check for AI distortions, pupil alignment, misplaced tails, duplicate characters.\n"
        "7. PRINT COMPLIANCE & GUTTER SAFETY: The central vertical line of the spread must be clear of faces.\n"
        "8. TEXT OVERLAY SAFE ZONES: Ensure there is a low-contrast, uncluttered, simple open background space (like clear sky, soft grass) specifically reserved for readable text overlay on both the left and right sides.\n\n"
        f"Scene Prompt: {hardened_prompt}\n\n"
        "Respond ONLY in valid, parseable JSON format. Use this schema:\n"
        "{\n"
        "  \"status\": \"PASS\" or \"FAIL\",\n"
        "  \"issues\": [\"list of errors found\"],\n"
        "  \"explanation\": \"Microscopic veteran critique explaining your observations.\"\n"
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

    req = urllib.request.Request(
        AUDIT_ENDPOINT,
        data=json.dumps(payload_audit).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
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
        return {"status": "ERROR", "explanation": f"API error: {e}"}

def main():
    print("🚀 Sending generation request to Google AI Studio for Page 8 (Spread 8-9)...")
    req = urllib.request.Request(GENERATE_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})

    img_bytes = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                parts = res["candidates"][0]["content"]["parts"]
                for part in parts:
                    if "inlineData" in part:
                        img_bytes = base64.b64decode(part["inlineData"]["data"])
                        break
                if img_bytes:
                    break
        except urllib.error.HTTPError as e:
            if e.code in [503, 429] and attempt < 4:
                print(f"  ⚠️ Service error {e.code}, retrying in {2 ** (attempt + 1)} seconds...")
                time.sleep(2 ** (attempt + 1))
                continue
            raise e
        except Exception as e:
            if attempt < 4:
                print(f"  ⚠️ Error: {e}, retrying...")
                time.sleep(2)
                continue
            raise e

    if not img_bytes:
        raise ValueError("Failed to obtain image data from response candidates.")

    # Save file
    fn = "Page_08.png"
    filepath = os.path.join(images_dir, fn)
    with open(filepath, "wb") as f:
        f.write(img_bytes)

    print(f"✅ Successfully generated and saved Page_08.png!")

    # Perform Audit
    print("🔬 Running 30-year veteran audit on newly generated Page_08.png...")
    report = audit_image(filepath)
    print(f"📊 Audit Status: {report['status']}")
    print(f"  Issues Found: {report.get('issues', [])}")
    print(f"  Explanation: {report.get('explanation')}")

    # Update databases
    report_file = os.path.join(desktop_dir, "02_Publishing_Files", "Book1_Audit_Report.json")
    state_file = os.path.join(desktop_dir, "02_Publishing_Files", "production_state.json")

    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        report_dict = {item[0]: item[1] for item in report_data}
        report_dict["Page_08.png"] = report
        new_report = [[k, v] for k, v in report_dict.items()]
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(new_report, f, indent=2)

    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state_data = json.load(f)
        existing = state_data.get("Page_08.png", {})
        state_data["Page_08.png"] = {
            "status": report["status"],
            "issues": report.get("issues", []),
            "explanation": report.get("explanation"),
            "prompt_used": hardened_prompt,
            "timestamp": time.time(),
            "attempts": existing.get("attempts", 1) + 1
        }
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4)

    # Split spread
    if report["status"] == "PASS":
        with PILImage.open(filepath) as im:
            w, h = im.size
            im.crop((0, 0, w // 2, h)).save(os.path.join(images_dir, "temp_left_Page_08.png"))
            im.crop((w // 2, 0, w, h)).save(os.path.join(images_dir, "temp_right_Page_08.png"))
        print("💾 Saved and split Page_08.png")

    print("🎉 Synchronization Complete!")

if __name__ == "__main__":
    main()
