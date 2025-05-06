import pandas as pd
from pathlib import Path

def save_audit_log(records, output_path="output/audit_log.xlsx"):
    """Writes a list of audit results to an Excel file."""
    if not records:
        print("⚠️ No records to write.")
        return

    df = pd.DataFrame(records)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"✅ Audit log written to {output_path}")
