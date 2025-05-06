**Price Audit Web Scraper**

**Overview**

**The **Price Audit Web Scraper** is a Python-based tool designed to automate price auditing for products across multiple vendor websites. It uses Bing to locate product pages, navigates to vendor sites, extracts price information, captures screenshots and HTML content, and generates a detailed audit log in Excel format. The tool processes product data from an Excel input file, supports parallel execution for efficiency, and includes robust error handling for navigation challenges such as popups, CAPTCHAs, and blocked pages.**

**Key Features**

* **Automated Web Scraping**: Performs Bing searches to find product pages on approved vendor websites.
* **Price Extraction**: Extracts prices using vendor-specific CSS selectors.
* **Parallel Processing**: Runs multiple audit tasks concurrently using multiprocessing.
* **Error Handling**: Manages navigation errors, popups, CAPTCHAs, and blocked pages.
* **Output Generation**: Saves screenshots, HTML files, and an Excel audit log with results.
* **Vendor-Specific Logic**: Custom handling for vendors like Home Depot, ToolNut, Grainger, Lowe's, Zoro, Whitecap, and Toolup.
* **Modular Design**: Easily extensible for new vendors or additional functionality.
* **Configurable Vendors**: Loads approved vendor domains from an Excel file.

**Prerequisites**

* **Python**: Version 3.8 or higher
* **Dependencies**:
  * **pandas**: For reading/writing Excel files
  * **playwright**: For web scraping and browser automation
  * **tqdm**: For progress bars
* **Playwright Browsers**: Chromium browser (installed via Playwright)
* **Input Files**:
  * **price-audit-test-file.xlsx**: Product data
  * **approved_sites.xlsx**: List of approved vendor domains

**Installation**

1. **Clone the Repository**:
   **bash**

   ```bash
   git clone <repository-url>
   cd price-audit-web-scraper
   ```
2. **Set Up a Virtual Environment** (recommended):
   **bash**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   **bash**

   ```bash
   pip install pandas playwright tqdm
   ```
4. **Install Playwright Browsers**:
   **bash**

   ```bash
   playwright install chromium
   ```
5. **Prepare Input Files**:

   * **Place **price-audit-test-file.xlsx** and **approved_sites.xlsx** in the **input/** directory.**

**Project Structure**

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

**Input File Formats**

**1. Product Data (**price-audit-test-file.xlsx**)**

**Contains product information with the following columns:**

* **Item #**: Unique product identifier (required)
* **Brand**: Product brand name (required)
* **Model #**: Product model number (required)
* **Notes**: Optional notes (products with "discontinued" or "custom" are skipped)

**Example:**

| **Item #** | **Brand**  | **Model #** | **Notes**        |
| ---------------- | ---------------- | ----------------- | ---------------------- |
| **12345**  | **DeWalt** | **DCD791**  |                        |
| **67890**  | **Makita** | **XPH12**   | **discontinued** |

**2. Approved Sites (**approved_sites.xlsx**)**

**Lists vendor domains with an enable/disable flag:**

* **Domain**: Vendor domain (e.g., "homedepot.com")
* **Enabled**: Boolean (True/False) to include/exclude the vendor

**Example:**

| **Domain**        | **Enabled** |
| ----------------------- | ----------------- |
| **homedepot.com** | **True**    |
| **lowes.com**     | **True**    |
| **amazon.com**    | **False**   |

**Only domains with **Enabled = True** are used.**

**Usage**

1. **Run the Script**:
   **bash**

   ```bash
   python main.py
   ```
2. **What Happens**:

   * **Load Inputs**: Reads **price-audit-test-file.xlsx** for products and **approved_sites.xlsx** for vendor domains.
   * **Process Products**: Extracts searchable identifiers (Brand + Model #). Skips products marked "discontinued" or "custom".
   * **Generate Tasks**: Creates Bing search queries for each product and enabled vendor (e.g., "DeWalt DCD791 site:homedepot.com").
   * **Execute Tasks**: Runs tasks in parallel (2 workers by default) using **audit_runner.py** to:
     * **Perform Bing searches**
     * **Navigate to vendor pages**
     * **Handle popups and vendor-specific interactions**
     * **Extract prices**
     * **Capture screenshots and HTML**
   * **Save Results**: Writes results to **output/audit_log.xlsx** and stores screenshots/HTML in **output/<product_id>_`<date>`/**.
3. **Output**:

   * **Audit Log** (**output/audit_log.xlsx**): An Excel file with columns including:
     * **Product ID**: Item # from input
     * **Vendor**: Vendor domain
     * **Search Query**: Bing search query
     * **Final URL**: Vendor page URL
     * **Screenshot**: Path to screenshot file
     * **HTML**: Path to HTML file
     * **Timestamp**: Task execution time
     * **Price**: Extracted price (if available)
     * **Status**: Success, Error, Blocked, etc.
     * **Debug Screenshot**/**Debug HTML**: Paths to debug files (if applicable)
   * **Screenshots and HTML**: Stored in `output/<product_id phúc

**Example audit log:**

| **Product ID** | **Vendor**        | **Search Query**                     | **Status**  | **Price** | **Screenshot**                                                | **HTML** | **Timestamp**           |
| -------------------- | ----------------------- | ------------------------------------------ | ----------------- | --------------- | ------------------------------------------------------------------- | -------------- | ----------------------------- |
| **12345**      | **homedepot.com** | **DeWalt DCD791 site:homedepot.com** | **Success** | **$199**  | **output/12345_2025-05-05/homedepot_2025-05-05_10-30-00.png** | **...**  | **2025-05-05_10-30-00** |

**Configuration**

* **Approved Sites**:
  * **Edit **input/approved_sites.xlsx** to add/remove vendors or toggle the **Enabled** column.**
  * **Supported vendors include: homedepot.com, toolnut.com, grainger.com, lowes.com, zoro.com, whitecap.com, toolup.com.**
* **Parallel Workers**: Adjust the **processes** parameter in **main.py** (default: 2) based on system resources.
* **Timeouts and Retries**: Modify navigation timeouts and retry logic in **audit_runner.py** (e.g., 45-second **goto** timeout, max 2 retries).
* **Output Path**: Change the audit log path in **report_writer.py** (default: **output/audit_log.xlsx**).

**Extending the Project**

**To add support for a new vendor:**

1. **Add the vendor to **input/approved_sites.xlsx** with **Enabled = True**.**
2. **Update **audit_runner.py**:**
   * **Add custom interactions in **handle_vendor_specific** (e.g., clicking buttons or scrolling).**
   * **Add a price selector in **extract_price** for the vendor's page structure.**
3. **Test the new vendor to ensure navigation, popup handling, and price extraction work correctly.**

**Example for a new vendor:**

**python**

```python
# In audit_runner.py, update extract_price
price_selectors ={
...
"newvendor.com":"span.product-price"
}

# In handle_vendor_specific
if"newvendor.com"in vendor_domain:
    page.locator("button.accept-cookies").click(timeout=5000)
```

**Troubleshooting**

* **Navigation Errors**: Check debug screenshots/HTML in **output/<product_id>_`<date>`/** for issues like redirects or missing elements.
* **CAPTCHAs or Blocks**: The script detects CAPTCHAs and blocked pages. Frequent blocks may require proxy rotation or user agent changes in **get_browser_context**.
* **Timeout Issues**: Increase timeouts in **audit_runner.py** (e.g., **goto** or **wait_for_selector**) for slow-loading pages.
* **Missing Prices**: Verify the price selector in **extract_price** matches the vendor's HTML structure.
* **Empty Audit Log**: Ensure **price-audit-test-file.xlsx** and **approved_sites.xlsx** are correctly formatted and contain valid data.
* **Missing Vendors**: Confirm that **approved_sites.xlsx** has **Enabled = True** for desired domains.

**Contributing**

**Contributions are welcome! To contribute:**

1. **Fork the repository.**
2. **Create a feature branch (**git checkout -b feature/`<feature-name>`**).**
3. **Commit changes (**git commit -m "Add `<feature>`"**).**
4. **Push to the branch (**git push origin feature/`<feature-name>`**).**
5. **Open a pull request.**

**License**

**This project is licensed under the MIT License. See the **LICENSE** file for details (or update with your preferred license).**

**Contact**

**For questions or support, please open an issue on the repository or contact the project maintainer.**
