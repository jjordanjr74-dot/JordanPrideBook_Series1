import os
import base64
import urllib.request
import json
import time

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
    "High-quality 2D digital storybook art illustration, vibrant vector linework with soft cel shading, warm savanna lighting. Title page vignette. "
    "Centered, perfectly symmetrical character portrait on a flat warm cream background (#FFFDF5). "
    "In the absolute center of the frame stands Pop Pop Jordan (broad-shouldered grandfather lion, silver-and-gold mane, red plaid flannel shirt with rolled sleeves, dark khaki trousers, work boots, brass belt buckle, golden pocket watch chain). Pop Pop is positioned directly in the center, standing behind both children in a protective, symmetrical stance. "
    "Pop Pop Jordan's large right arm is extended to his right, resting a warm, thick cartoon animal paw on Leo's shoulder. His large left arm is extended to his left, resting a warm, thick cartoon animal paw on Maya's shoulder. "
    "Standing directly in front of Pop Pop Jordan's left side (on the left side of the frame) is Leo Jordan (6yo golden boy lion cub, unruly reddish-brown head hair tuft, amber eyes, blue denim overalls, orange-and-white striped t-shirt, blue canvas sneakers, NO hair ribbons) standing proudly with his right paw placed firmly over his heart. "
    "Leo's denim overalls feature exactly one large chest bib pocket on the front center of his chest. Inside this chest bib pocket, a small toy magnifying glass is fully tucked, with only its round handle peeking out at the top. The hip pockets and side loops are completely empty; there is absolutely no accessory hanging on Leo's hip. "
    "Standing directly in front of Pop Pop Jordan's right side (on the right side of the frame) is Maya Jordan (3yo cream-and-gold girl lion cub, snout freckles, hazel eyes, sunshine-yellow dress with two large deep front crayon pockets, bright purple ear bow ribbon behind her left ear, pink sandals, clutching soft purple star plushie Glimmer) waving happily. Maya is much smaller and shorter than Leo, reaching only to Leo's shoulder height. "
    "CRITICAL BRAND SAFETY & DESIGN RULES: Symmetrical centered composition. 100% anthropomorphic animal universe. Absolutely NO human hands, NO human fingers, NO human knuckles, NO human skin folds. All characters must have thick, rounded, fuzzy cartoon animal paws with soft pads that look like mittens. Leo has absolutely NO ribbons, bows, or flowers in his hair. Keep the upper 40% of the canvas completely clear warm cream space with absolutely no sunflower graphics or details, specifically reserved for title typography. Symmetrical composition."
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

print("🚀 Sending generation request to Google AI Studio for Page 1 (Super-Hardened)...")
req = urllib.request.Request(GENERATE_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})

with urllib.request.urlopen(req, timeout=120) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    parts = res["candidates"][0]["content"]["parts"]
    for part in parts:
        if "inlineData" in part:
            img_bytes = base64.b64decode(part["inlineData"]["data"])
            break

# Save file
fn = "Page_01.png"
filepath = os.path.join(images_dir, fn)
with open(filepath, "wb") as f:
    f.write(img_bytes)

if os.path.exists("D:/"):
    with open(os.path.join(backup_dir, fn), "wb") as f:
        f.write(img_bytes)

print(f"✅ Successfully generated and saved Page_01.png!")

# Perform Audit
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
    "Scene Title: Page 1: Title Page Vignette\n"
    f"Scene Prompt: {hardened_prompt}\n\n"
    "--- INSTRUCTIONS FOR RESPONSE ---\n"
    "Conduct a multi-pass, rigorous analysis. Be uncompromisingly honest. If you see even the most minute deficiency (such as a pattern anomaly, a slight height squashing, a hidden human hand, or a double ear), flag it as a FAIL. "
    "Respond ONLY in valid, parseable JSON format. Do not prepend or append markdown code block ticks. Use this schema:\n"
    "{\n"
    "  \"status\": \"PASS\" or \"FAIL\",\n"
    "  \"issues\": [\"list of specific, distinct visual errors, contradictions, or deficiencies found. Be highly specific and granular. If PASS, leave empty.\"],\n"
    "  \"explanation\": \"A comprehensive, professional, 30-year veteran level editorial critique explaining your observations, character by character, pixel-region by pixel-region, detail by detail. Outline exactly why the image passes or where the artist must focus to correct the flaws.\"\n"
    "}"
)

print("🔬 Running 30-year veteran audit on newly generated Page_01.png...")
with open(filepath, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

payload_audit = {
    "contents": [{
        "parts": [
            {"text": audit_instruction},
            {"inlineData": {"mimeType": "image/png", "data": img_b64}}
        ]
    }]
}

req_audit = urllib.request.Request(AUDIT_ENDPOINT, data=json.dumps(payload_audit).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req_audit, timeout=90) as resp:
    res_audit = json.loads(resp.read().decode("utf-8"))
    text_resp = res_audit["candidates"][0]["content"]["parts"][0]["text"].strip()
    if text_resp.startswith("```json"):
        text_resp = text_resp[7:]
    if text_resp.endswith("```"):
        text_resp = text_resp[:-3]
    report = json.loads(text_resp.strip())

print(f"📊 Audit Status: {report['status']}")
print(f"  Issues Found: {report.get('issues', [])}")
print(f"  Explanation: {report.get('explanation')}")

# Update databases
report_file = os.path.join(desktop_dir, "Book1_Audit_Report.json")
state_file = os.path.join(desktop_dir, "production_state.json")

if os.path.exists(report_file):
    with open(report_file, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    report_dict = {item[0]: item[1] for item in report_data}
    report_dict["Page_01.png"] = report
    new_report = [[k, v] for k, v in report_dict.items()]
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(new_report, f, indent=2)

if os.path.exists(state_file):
    with open(state_file, "r", encoding="utf-8") as f:
        state_data = json.load(f)
    existing = state_data.get("Page_01.png", {})
    state_data["Page_01.png"] = {
        "status": report["status"],
        "issues": report.get("issues", []),
        "explanation": report.get("explanation"),
        "prompt_used": hardened_prompt,
        "timestamp": time.time(),
        "attempts": existing.get("attempts", 1) + 1
    }
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=4)

print("🎉 Synchronization Complete!")
