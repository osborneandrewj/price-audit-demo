import pandas as pd
from sites_loader import load_approved_sites
from audit_runner import capture_task
from report_writer import save_audit_log
from tqdm import tqdm
from multiprocessing import Pool

# === Identifier Extraction Function ===
def extract_searchable_identifier(row):
    model = str(row.get("Model #", "")).strip()
    brand = str(row.get("Brand", "")).strip()
    notes = str(row.get("Notes", "")).strip().lower()

    if "discontinued" in notes or "custom" in notes:
        return None

    if not model or not brand:
        return None

    return f"{brand} {model}"

# === Main Execution ===
def main():
    products_df = pd.read_excel("input/price-audit-test-file.xlsx")
    approved_sites = load_approved_sites()
    tasks = []

    for idx, row in products_df.iterrows():
        identifier = extract_searchable_identifier(row)
        if not identifier:
            print(f"[SKIP] Row {idx+2}: {row.get('Notes', 'No reason')}")
            continue

        item_id = row["Item #"]
        print(f"\n🔍 Product: {identifier}")

        for domain in approved_sites:
            query = f"{identifier} site:{domain}"
            print("  🔗", query)
            tasks.append((query, item_id, domain))

    print(f"\n🚀 Starting audit with {len(tasks)} tasks using 2 parallel workers...\n")
    results = []
    with Pool(processes=2) as pool:
        for result in tqdm(pool.imap_unordered(capture_task, tasks), total=len(tasks), desc="Auditing"):
            results.append(result)

    save_audit_log(results)

if __name__ == "__main__":
    main()
