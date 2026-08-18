import json
import os

state_file = r"C:\Users\marti\JordanPrideBook_Series1_Final\02_Publishing_Files\production_state.json"
report_file = r"C:\Users\marti\JordanPrideBook_Series1_Final\02_Publishing_Files\Book1_Audit_Report.json"

print("🔍 Synchronizing production_state.json failures to Book1_Audit_Report.json...")

if not os.path.exists(state_file):
    print("❌ Error: production_state.json not found!")
    exit(1)
if not os.path.exists(report_file):
    print("❌ Error: Book1_Audit_Report.json not found!")
    exit(1)

with open(state_file, "r", encoding="utf-8") as f:
    state_data = json.load(f)

with open(report_file, "r", encoding="utf-8") as f:
    report_list = json.load(f)

report_dict = {item[0]: item[1] for item in report_list}

sync_count = 0
for fn, state in state_data.items():
    if state.get("status") == "FAIL":
        # Check if report has this as PASS or missing
        rep_status = report_dict.get(fn, {}).get("status")
        if rep_status != "FAIL":
            print(f"🔄 Syncing {fn} to FAIL based on production_state.json")
            report_dict[fn] = {
                "status": "FAIL",
                "issues": state.get("issues", []),
                "explanation": state.get("explanation", "")
            }
            sync_count += 1

if sync_count > 0:
    # Convert report_dict back to list of list [filename, dict] to match Book1_Audit_Report.json structure
    updated_report = []
    # Retain the ordering if possible or just dump list of items
    for item in report_list:
        fn = item[0]
        if fn in report_dict:
            updated_report.append([fn, report_dict[fn]])
        else:
            updated_report.append(item)
            
    # Add any missing keys
    existing_fns = {item[0] for item in updated_report}
    for fn, rep in report_dict.items():
        if fn not in existing_fns:
            updated_report.append([fn, rep])

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(updated_report, f, indent=2)
    print(f"✅ Successfully synchronized {sync_count} failed statuses.")
else:
    print("✓ Both databases are already perfectly in sync.")
