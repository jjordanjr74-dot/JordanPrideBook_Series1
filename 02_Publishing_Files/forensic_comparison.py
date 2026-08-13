import os
import base64
import urllib.request
import json

API_KEY = "AQ.Ab8RN6KOKkmFqHlyG1kpgwMJued42xwOvIkvmEagmgsSw5nhig"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY}"

root_dir = r"C:\Users\marti\JordanPrideBook_Series1_Final"
assets_dir = os.path.join(root_dir, "01_Final_Book_Assets")

img4_path = os.path.join(assets_dir, "Page_04.png")
img5_path = os.path.join(assets_dir, "Page_05.png")

if os.path.exists(img4_path) and os.path.exists(img5_path):
    with open(img4_path, "rb") as f:
        img4_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(img5_path, "rb") as f:
        img5_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    audit_instruction = (
        "You are an Elite Executive Children's Book Editor and Publishing Director with 30 years of experience in high-end publishing. "
        "Your eye for detail is legendarily meticulous. You are performing a microscopic forensic comparison of two consecutive double-page spreads: "
        "Spread 1 (Page_04.png) and Spread 2 (Page_05.png) for 'The Jordan Pride' children's book series.\n\n"
        "Analyze both images side-by-side. Perform an extremely rigorous audit checking for consistency and flow:\n\n"
        "1. BACKGROUND MATCHING: Compare the environment details across both spreads. Do the colors of the grass/lawn, the shape and texture of the trees (acacia canopy), "
        "the flower colors (yellow marigolds and red roses), the sky tone, and the background fences match in style and palette? Is there a natural spatial continuity?\n"
        "2. LEO'S DESIGN & STYLE CONSISTENCY: Compare Leo Jordan between the two spreads. Check his fur tone (golden-orange), muzzle color, unruly reddish-brown head hair tuft shape, "
        "and clothing details (blue denim overalls, horizontal orange-and-white stripes on his shirt, blue sneakers). Is his visual identity 100% consistent, or has he mutated?\n"
        "3. MAYA'S DESIGN & STYLE CONSISTENCY: Compare Maya Jordan. Check her cream fur tone, purple ear bow placement and color, yellow dress with crayon pockets, Glimmer plushie style, and pink sandals. Are they identical?\n"
        "4. FLOW & NARRATIVE CONTINUITY: Do the two scenes flow naturally into each other? Spread 1 shows Leo standing flexing on a stump on the left, and Pop Pop's marker standing intact on the right. "
        "Spread 2 shows the marker snapped in two on the grass, Leo scrambling backward on the left in shock, clutching his tummy, and Maya rushing to his side. "
        "Does the horizon angle, spatial layout, and environmental logic support this narrative flow?\n"
        "5. PROMPT & TEXT PARITY: Do both images align perfectly with the story text and art sheet prompts?\n\n"
        "Provide a highly structured, objective, and detailed critique. Highlight any microscopic discrepancies (even minor ones like button count, line weight shift, grass color tone shift, "
        "muzzle shape drift) so we can achieve absolute publishing perfection."
    )

    payload = {
        "contents": [{
            "parts": [
                {"text": audit_instruction},
                {"inlineData": {"mimeType": "image/png", "data": img4_b64}},
                {"inlineData": {"mimeType": "image/png", "data": img5_b64}}
            ]
        }]
    }

    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(res["candidates"][0]["content"]["parts"][0]["text"])
    except Exception as e:
        print(f"Error calling API: {e}")
else:
    print("Files not found!")
