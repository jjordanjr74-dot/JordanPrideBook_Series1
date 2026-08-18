import os
import base64
import urllib.request
import urllib.error
import json
import time

API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
MODEL_NAME = "gemini-3.5-flash"
ENDPOINT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

files_to_audit = [
    r"C:\Users\marti\Page_01_gemini_v2_review.png",
    r"C:\Users\marti\Page_01_review.png",
    r"C:\Users\marti\best_title_book1_review.jpg",
    r"C:\Users\marti\half_title_page_review.jpg"
]

def audit_image(image_path):
    if not os.path.exists(image_path):
        return {"status": "MISSING", "explanation": "File does not exist."}
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    audit_instruction = (
        "You are an Elite Executive Children's Book Editor and Publishing Director with 30 years of experience in high-end publishing. "
        "Your eye for detail is legendarily meticulous. You are auditing a title page illustration for 'The Jordan Pride' children's picture book series "
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
        "   - Leo's bib pocket must have the toy magnifying glass tucked in it.\n"
        "6. ANATOMICAL INTEGRITY: Check for AI distortions, pupil alignment, misplaced tails, duplicate characters.\n"
        "7. PRINT COMPLIANCE: Centered framing with generous open background space above the characters for title text.\n\n"
        "Respond ONLY in valid, parseable JSON format. Use this schema:\n"
        "{\n"
        "  \"status\": \"PASS\" or \"FAIL\",\n"
        "  \"issues\": [\"list of errors found\"],\n"
        "  \"explanation\": \"Microscopic veteran critique explaining your observations.\"\n"
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
    print("🚀 Microscopic Audit of Candidate Title Page Images...")
    for path in files_to_audit:
        fn = os.path.basename(path)
        print(f"\n🔍 Auditing {fn}...")
        report = audit_image(path)
        print(f"  Status: {report.get('status')}")
        if report.get("issues"):
            print("  Issues Found:")
            for issue in report["issues"]:
                print(f"    - {issue}")
        else:
            print("  ✓ PASS! Pristine asset matches the Jordan Pride Standard.")
        print("-" * 60)

if __name__ == "__main__":
    main()
