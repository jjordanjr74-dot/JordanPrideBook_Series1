import re
import json
import os

JORDAN_CORE_VALUES = [
    "Honesty", "Loyalty", "Empathy", "Community Service", "Helping Others",
    "Protecting the Weak", "Responsibility", "Accountability", "Integrity",
    "Initiative", "Supporting Family", "Politeness & Good Manners", "Respect",
    "Positive Attitude", "Love for Learning & Adventure", "Respect for Nature"
]

def load_character_bible():
    return {
        "Leo": {
            "name": "Leo Jordan",
            "desc": "Leo Jordan (6-year-old golden-yellow furred anthropomorphic boy lion cub, tuft of reddish-brown hair on his head, amber eyes, blue denim overalls with magnifying glass in pocket over orange-and-white striped short-sleeve shirt, blue canvas sneakers).",
            "negative": "Leo has NO hair bows or ribbons. ONLY Maya wears the purple ear bow ribbon."
        },
        "Maya": {
            "name": "Maya Jordan",
            "desc": "Maya Jordan (3-year-old cream-and-gold furred anthropomorphic girl lion cub, snout freckles, hazel eyes, bright purple ribbon ear bow behind her left ear, sunshine-yellow dress with crayon pockets, pink sandals, holding plush star 'Glimmer').",
            "negative": ""
        },
        "Pop Pop": {
            "name": "Pop Pop",
            "desc": "Pop Pop Jordan (broad-shouldered grandfather anthropomorphic lion, silver-and-gold mane, amber eyes, red plaid flannel shirt with rolled-up sleeves, dark khaki trousers, brown leather work boots, brass belt buckle with gold watch chain).",
            "negative": ""
        },
        "Great-Grampa": {
            "name": "Great-Grampa",
            "desc": "Great-Grampa Jordan (distinguished elderly anthropomorphic lion, graying mane, reading spectacles, worn trucker hat, noticeable bend in back when standing, cream cable-knit cardigan, beige shirt, khaki trousers, brown loafers).",
            "negative": ""
        },
        "GiGi": {
            "name": "GiGi",
            "desc": "GiGi Jordan (elegant grandmother anthropomorphic lioness, sleek golden fur, emerald eyes, wide-brimmed sunhat, silk scarf, coral tunic, cream linen pants, flat sandals, souvenir charm bracelet).",
            "negative": ""
        },
        "Mom": {
            "name": "Mom",
            "desc": "Mom Jordan (petite short anthropomorphic lioness, warm honey-toned fur, brown eyes, teal tunic blouse, charcoal leggings, tan flats, silver paw-print pendant).",
            "negative": ""
        },
        "Dad": {
            "name": "Dad",
            "desc": "Dad Jordan (tall slim anthropomorphic lion, dark mahogany mane, navy blue mechanic coveralls with grease smudge on cheek, basketball sneakers).",
            "negative": ""
        },
        "Tio": {
            "name": "Tio",
            "desc": "Tio Jordan (athletic muscular anthropomorphic male lion, short dark mane, big toothy smile, red short-sleeve athletic hoodie, grey sweatpants, sports watch, cross-training sneakers).",
            "negative": ""
        },
        "TiTi": {
            "name": "TiTi",
            "desc": "TiTi Jordan (graceful anthropomorphic lioness, braided head fur in earth-toned scarf wrap, olive-and-gold kaftan dress, linen pants, turquoise jewelry, leather flats).",
            "negative": ""
        },
        "Auntie Willow": {
            "name": "Auntie Willow",
            "desc": "Auntie Willow (gentle anthropomorphic white rabbit, pink-lined ears, reading glasses on beaded strap, lavender cardigan, white blouse, blue pleated skirt, grey flats).",
            "negative": ""
        },
        "Mama Ursula": {
            "name": "Mama Ursula / Mama Pearl",
            "desc": "Mama Ursula (cozy anthropomorphic brown bear, dark chocolate fur, hair bun, flour-dusted floral apron over denim shirt, dark trousers, brown boots).",
            "negative": ""
        }
    }

def sanitize_scene_text(scene_text):
    text = re.sub(r'\bhands?\b', 'paws', scene_text, flags=re.IGNORECASE)
    text = re.sub(r'\bfingers?\b', 'paw digits', text, flags=re.IGNORECASE)
    text = text.replace('"', '').replace('“', '').replace('”', '').replace('`', '').replace("'", "")
    return text

def compile_prompt(scene_text, page_num, target_engine="imagen", is_spread=True):
    sanitized = sanitize_scene_text(scene_text)
    bible = load_character_bible()
    
    chars = [c for c in bible.keys() if re.search(r"\b" + re.escape(c) + r"\b", sanitized, re.IGNORECASE)]
    
    style_prefix = "High-quality 2D digital storybook art illustration, vibrant vector linework, soft cel shading, warm golden savanna lighting. "
    
    if is_spread:
        layout = f"Panoramic two-page spread (Pages {page_num}-{page_num+1}), clean composition with empty gutter fold in center. "
        ar = "17:11"
    else:
        layout = f"Single-page storybook illustration (Page {page_num}), clean balanced layout with text margin. "
        ar = "3:4"
        
    char_prompts = " ".join([f"Character Lock: {bible[c]['desc']}" for c in chars])
    
    proportion_rule = ""
    if "Leo" in chars and "Maya" in chars:
        proportion_rule = "PROPORTION LOCK: Leo is tall 6yo brother. Maya is tiny 3yo toddler (reaches only to Leo's chest/hip). Leo visibly towers over Maya. "
        
    core_rules = "CRITICAL RULES: 100% anthropomorphic animals, clothed, bipedal. Every hand MUST be a 4-digit furry animal paw with soft paw pads, NO 5-fingered human hands, NO human skin, NO text, NO speech bubbles. "
    
    if target_engine.lower() == "midjourney":
        mj_prompt = f"{style_prefix}{layout}{sanitized} {char_prompts} {proportion_rule}{core_rules} --ar {ar} --v 6.1 --s 250 --style raw"
        mj_no = "--no text, letters, speech bubbles, 5 fingers, human hands, human skin, quadrupeds"
        return f"{mj_prompt} {mj_no}"
        
    elif target_engine.lower() in ["sd", "stable-diffusion"]:
        positive = f"{style_prefix}{layout}{sanitized} {char_prompts} {proportion_rule}{core_rules}"
        negative = "(human hands:1.5), (5 fingers:1.5), (speech bubble:1.4), text, letters, watermark, extra limbs, bad anatomy, human skin, quadruped"
        return {"prompt": positive, "negative_prompt": negative, "aspect_ratio": ar}
        
    else: # Imagen / Gemini default
        return f"{style_prefix}{layout}Scene: {sanitized}. {char_prompts} {proportion_rule}{core_rules} Aspect Ratio {ar}."

if __name__ == "__main__":
    test_scene = "Leo, Maya, Pop Pop, Great-Grampa, GiGi, Mom, Dad, Tio, TiTi, Auntie Willow, and Mama Ursula gather together."
    print("=== IMAGEN / GEMINI PROMPT ===")
    print(compile_prompt(test_scene, 1, "imagen"))
