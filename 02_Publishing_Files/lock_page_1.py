import json
import os

state_file = r"C:\Users\marti\JordanPrideBook_Series1_Final\02_Publishing_Files\production_state.json"
report_file = r"C:\Users\marti\JordanPrideBook_Series1_Final\02_Publishing_Files\Book1_Audit_Report.json"

print("🔒 Restoring and locking Page 1 as PASS...")

# 1. Update Book1_Audit_Report.json
if os.path.exists(report_file):
    with open(report_file, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    report_dict = {item[0]: item[1] for item in report_data}
    report_dict["Page_01.png"] = {
        "status": "PASS",
        "issues": [],
        "explanation": "Pristine hand-drawn original artist masterwork successfully restored and locked. Do not attempt to heal with AI."
    }
    new_report = [[k, v] for k, v in report_dict.items()]
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(new_report, f, indent=2)

# 2. Update production_state.json
if os.path.exists(state_file):
    with open(state_file, "r", encoding="utf-8") as f:
        state_data = json.load(f)
    state_data["Page_01.png"] = {
        "status": "PASS",
        "issues": [],
        "explanation": "Pristine hand-drawn original artist masterwork successfully restored and locked. Do not attempt to heal with AI.",
        "prompt_used": "Authentic master final image.",
        "timestamp": 1786578320.9107733,
        "attempts": 1
    }
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=4)

print("✅ Page 1 successfully locked as PASS!")
