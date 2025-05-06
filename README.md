# Price Audit Web Scraper

## Overview

The **Price Audit Web Scraper** is a Python-based tool designed to automate price auditing for products across multiple vendor websites. It uses Bing to locate product pages, navigates to vendor sites, extracts price information, captures screenshots and HTML content, and generates a detailed audit log in Excel format. The tool processes product data from an Excel input file, supports parallel execution for efficiency, and includes robust error handling for navigation challenges such as popups, CAPTCHAs, and blocked pages.

## Key Features

- **Automated Web Scraping**: Performs Bing searches to find product pages on approved vendor websites.
- **Price Extraction**: Extracts prices using vendor-specific CSS selectors.
- **Parallel Processing**: Runs multiple audit tasks concurrently using multiprocessing.
- **Error Handling**: Manages navigation errors, popups, CAPTCHAs, and blocked pages.
- **Output Generation**: Saves screenshots, HTML files, and an Excel audit log with results.
- **Vendor-Specific Logic**: Custom handling for vendors like Home Depot, ToolNut, Grainger, Lowe's, Zoro, Whitecap, and Toolup.
- **Modular Design**: Easily extensible for new vendors or additional functionality.
- **Configurable Vendors**: Loads approved vendor domains from an Excel file.

## Prerequisites

- **Python**: Version 3.8 or higher
- **Dependencies**:
  - `pandas`: For reading/writing Excel files
  - `playwright`: For web scraping and browser automation
  - `tqdm`: For progress bars
- **Playwright Browsers**: Chromium browser (installed via Playwright)
- **Input Files**:
  - `price-audit-test-file.xlsx`: Product data
  - `approved_sites.xlsx`: List of approved vendor domains

## Installation

1. **Clone the Repository**:

```bash
git clone <repository-url>
cd price-audit-web-scraper
```

2. **Set Up a Virtual Environment** (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:

```bash
pip install pandas playwright tqdm
```

4. **Install Playwright Browsers**:

```bash
playwright install chromium
```

5. **Prepare Input Files**:

Place `price-audit-test-file.xlsx` and `approved_sites.xlsx` in the `input/` directory.

## Project Structure

```text
price-audit-web-scraper/
│
├── input/
│   ├── price-audit-test-file.xlsx  # Product data
│   └── approved_sites.xlsx         # Approved vendor domains
├── output/
│   ├── <product_id>_<date>/       # Screenshots and HTML files
│   └── audit_log.xlsx             # Audit results in Excel
├── main.py                        # Orchestrates the audit process
├── audit_runner.py                # Core scraping and navigation logic
├── sites_loader.py                # Loads approved vendor domains
├── report_writer.py               # Saves audit results to Excel
└── README.md                      # This file
```

## Input File Formats

### 1. Product Data (`price-audit-test-file.xlsx`)

Contains product information with the following columns:

- **Item #**: Unique product identifier (required)
- **Brand**: Product brand name (required)
- **Model #**: Product model number (required)
- **Notes**: Optional notes (products with "discontinued" or "custom" are skipped)

**Example:**

| Item # | Brand  | Model # | Notes        |
| ------ | ------ | ------- | ------------ |
| 12345  | DeWalt | DCD791  |              |
| 67890  | Makita | XPH12   | discontinued |

### 2. Approved Sites (`approved_sites.xlsx`)

Lists vendor domains with an enable/disable flag:

- **Domain**: Vendor domain (e.g., `homedepot.com`)
- **Enabled**: Boolean (True/False) to include/exclude the vendor

**Example:**

| Domain        | Enabled |
| ------------- | ------- |
| homedepot.com | True    |
| lowes.com     | True    |
| amazon.com    | False   |

Only domains with **Enabled = True** are used.

## Usage

1. **Run the Script**:

```bash
python main.py
```

2. **What Happens**:
   - Load product and vendor input files
   - Search Bing for product pages
   - Navigate to vendor sites
   - Extract price and capture data
   - Save results to output directory

## Example Audit Log

| Product ID | Vendor        | Search Query                     | Status  | Price | Screenshot Path                                | Timestamp           |
| ---------- | ------------- | -------------------------------- | ------- | ----- | ---------------------------------------------- | ------------------- |
| 12345      | homedepot.com | DeWalt DCD791 site:homedepot.com | Success | $199  | output/12345_2025-05-05/homedepot_10-30-00.png | 2025-05-05_10-30-00 |

## Configuration

- **Approved Sites**: Edit `input/approved_sites.xlsx`
- **Parallel Workers**: Set in `main.py`
- **Timeouts/Retries**: Controlled in `audit_runner.py`
- **Output Path**: Set in `report_writer.py`

## Extending the Project

To add support for a new vendor:

1. Add to `approved_sites.xlsx`
2. Update `audit_runner.py` to:
   - Handle vendor-specific popups or interactions
   - Extract pricing using new selectors

**Example**:

```python
# Add selector
price_selectors["newvendor.com"] = "span.product-price"

# Handle interaction
if "newvendor.com" in vendor_domain:
    page.locator("button.accept-cookies").click(timeout=5000)
```

## Troubleshooting

- **Debug Files**: Check screenshots and HTML in `output/`
- **Blocked Pages**: Watch for CAPTCHAs or anti-bot responses
- **Missing Prices**: Update CSS selectors for new HTML
- **Slow Pages**: Increase timeout settings in `audit_runner.py`

## Contributing

1. Fork the repository
2. Create a new branch (`feature/your-feature`)
3. Commit and push your changes
4. Submit a pull request

## License

MIT License (see `LICENSE`)

## Contact

For questions, open an issue or contact the maintainer.
