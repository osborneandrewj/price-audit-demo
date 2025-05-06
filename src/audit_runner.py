import datetime
import random
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError, Error as PlaywrightError
from urllib.parse import quote


def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def clean_filename(s):
    return "".join(c for c in s if c.isalnum() or c in (' ', '-', '_')).rstrip()


def get_browser_context(p, vendor_domain, retry=False):
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0"
        if retry and "lowes.com" in vendor_domain
        else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    return p.chromium.launch(headless=True).new_context(
        user_agent=user_agent,
        viewport={"width": 1280, "height": 800},
        java_script_enabled=True,
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.bing.com/",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
        }
    )


def handle_toolnut_modal(page):
    try:
        page.wait_for_timeout(7000)
        close_btn = page.locator("[data-testid='closeIcon']")
        if close_btn.count() > 0 and close_btn.is_visible():
            close_btn.click(timeout=5000)
            print("✅ Closed ToolNut modal via [data-testid='closeIcon']")
            return
    except Exception as e:
        print(f"⚠️ Failed to close ToolNut modal: {e}")

    try:
        page.evaluate("""
            const selectors = ['[data-testid="closeIcon"]', '#dialogContainer', '#overlayContainer', '#swell-popup', '#swell-overlay'];
            selectors.forEach(sel => {
                const el = document.querySelector(sel);
                if (el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.opacity = '0';
                }
            });
            document.body.style.overflow = 'auto';
        """)
        print("✅ ToolNut modal forcibly hidden.")
    except Exception as e:
        print(f"❌ Failed to hide ToolNut modal: {e}")


def handle_general_modals(page):
    modal_selectors = [
        "div[class*='modal'], div[class*='popup'], div[class*='overlay'], div[id*='popup'], div[id*='modal']",
        "button:has-text('Continue'), button[class*='close'], button[aria-label='Close'], a[class*='close']",
        "button[class*='dismiss'], button[id*='close'], button[class*='btn-close']"
    ]
    for selector in modal_selectors:
        try:
            el = page.locator(selector)
            if el.count() > 0 and el.is_visible():
                el.click(timeout=5000)
                page.wait_for_timeout(1000)
                print(f"✅ Closed popup with selector: {selector}")
                return True
        except Exception as e:
            print(f"⚠️ Failed to click selector: {selector} — {str(e)}")
    return False


def handle_vendor_specific(page, vendor_domain):
    if "homedepot.com" in vendor_domain:
        try:
            page.wait_for_selector("h1[data-component='ProductTitle']", timeout=30000)
            page.wait_for_selector("div[data-testid='price-display']", timeout=30000)
            page.wait_for_selector("img[data-testid='main-product-image']", timeout=30000)
            for action in ["text='Product Details'", "text='Add to Cart'"]:
                try:
                    page.locator(action).click(timeout=5000)
                    page.wait_for_timeout(2000)
                except:
                    pass
        except TimeoutError:
            print("⚠️ Required elements not found on Home Depot page.")
    elif "grainger.com" in vendor_domain:
        try:
            page.locator("text='Accept Cookies'").click(timeout=5000)
            page.wait_for_timeout(2000)
        except:
            pass
        for action in ["text='Product Details'", "text='Add to Cart'"]:
            try:
                page.locator(action).click(timeout=5000)
                page.wait_for_timeout(2000)
            except:
                pass
    page.mouse.move(random.randint(100, 500), random.randint(100, 500))
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(3000)


def extract_price(page, vendor_domain):
    price_selectors = {
        "homedepot.com": "div[data-testid='price-display'] >> span",
        "toolnut.com": ".product-info-price span.price",
        "grainger.com": "div.price, span[data-testid='price']",
        "lowes.com": "div[class*='price'], span[class*='price']",
        "zoro.com": "span.price, div[class*='Price']",
        "whitecap.com": "span.TypographyStyle--11lquxl.blPZZG",
        "toolup.com": "span.price--main"
    }
    try:
        selector = price_selectors.get(vendor_domain.split('.')[0] + '.com')
        if selector:
            price_locator = page.locator(selector)
            price_locator.wait_for(timeout=5000)
            if price_locator.count() > 0:
                price = price_locator.first.text_content().strip()
                print(f"💲 Extracted price: {price}")
                return price
        print("❌ No price found with known selectors.")
    except Exception as e:
        print(f"⚠️ Error extracting price: {e}")
    return None


def save_debug_files(page, product_id, vendor_domain, output_dir, status, timestamp_str):
    date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{product_id}_{date_stamp}"
    out_path = Path(output_dir) / folder_name
    out_path.mkdir(parents=True, exist_ok=True)
    safe_vendor = clean_filename(vendor_domain)
    base_name = f"{safe_vendor}_{status}_{timestamp_str}"
    
    files = {}
    try:
        screenshot_path = out_path / f"{base_name}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        files["Debug Screenshot"] = str(screenshot_path)
    except:
        print(f"Failed to capture {status} screenshot")
    
    if status == "debug":
        try:
            html_path = out_path / f"{base_name}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page.content())
            files["Debug HTML"] = str(html_path)
        except:
            print(f"Failed to save {status} HTML")
    
    return files


def search_and_capture(search_query, product_id, vendor_domain, output_dir="output"):
    try:
        with sync_playwright() as p:
            max_retries = 2
            for attempt in range(max_retries):
                context = get_browser_context(p, vendor_domain, retry=attempt > 0)
                context.set_extra_http_headers({"Cookie": "acceptCookies=true; user_type=guest"})
                page = context.new_page()

                # Navigate to Bing search
                search_url = f"https://www.bing.com/search?q={quote(search_query)}"
                print(f"Navigating to search URL: {search_url}")
                try:
                    page.goto(search_url, timeout=15000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception as e:
                    context.close()
                    return {
                        "Product ID": product_id,
                        "Vendor": vendor_domain,
                        "Search Query": search_query,
                        "Status": f"Error navigating to search URL: {str(e)}",
                        "Timestamp": timestamp()
                    }

                # Find vendor link
                links = page.locator(f'.b_algo a[href*="{vendor_domain}"]').all()
                print(f"Found {len(links)} potential links containing '{vendor_domain}'")
                target_href = None
                for link in links:
                    href = link.get_attribute("href")
                    if (
                        href and href.startswith(("http", "https")) and
                        vendor_domain in href and
                        not any(x in href for x in ["bing.com", "/chat", "/copilotsearch"]) and
                        link.is_visible()
                    ):
                        target_href = href
                        break

                if not target_href:
                    context.close()
                    return {
                        "Product ID": product_id,
                        "Vendor": vendor_domain,
                        "Search Query": search_query,
                        "Status": "No Valid Vendor Link Found",
                        "Timestamp": timestamp()
                    }

                # Navigate to vendor page
                print(f"Navigating to vendor link: {target_href}")
                try:
                    page.wait_for_timeout(random.randint(1000, 3000))
                    page.goto(target_href, timeout=45000)
                    page.wait_for_load_state("domcontentloaded", timeout=45000)
                except TimeoutError:
                    print("Timeout waiting for DOM content, using fallback wait")
                    page.wait_for_timeout(15000)
                    if attempt == max_retries - 1:
                        context.close()
                        return {
                            "Product ID": product_id,
                            "Vendor": vendor_domain,
                            "Search Query": search_query,
                            "Status": "Timeout on Vendor Page Navigation",
                            "Timestamp": timestamp()
                        }
                except PlaywrightError as e:
                    if attempt == max_retries - 1 and "lowes.com" in vendor_domain and "ERR_HTTP2_PROTOCOL_ERROR" in str(e):
                        context.close()
                        return {
                            "Product ID": product_id,
                            "Vendor": vendor_domain,
                            "Search Query": search_query,
                            "Status": "Skipped due to HTTP/2 Error",
                            "Timestamp": timestamp()
                        }
                    if attempt == max_retries - 1:
                        context.close()
                        return {
                            "Product ID": product_id,
                            "Vendor": vendor_domain,
                            "Search Query": search_query,
                            "Status": f"Navigation Error: {str(e)}",
                            "Timestamp": timestamp()
                        }
                    print(f"Navigation error on attempt {attempt + 1}: {str(e)}, retrying...")
                    continue

                # Verify vendor page
                current_url = page.url
                print(f"Current URL: {current_url}")
                if vendor_domain not in current_url or "bing.com" in current_url:
                    files = save_debug_files(page, product_id, vendor_domain, output_dir, "failed", timestamp())
                    context.close()
                    return {
                        "Product ID": product_id,
                        "Vendor": vendor_domain,
                        "Search Query": search_query,
                        "Status": "Failed to Reach Vendor Page",
                        "Timestamp": timestamp(),
                        "Current URL": current_url,
                        **files
                    }

                # Check for blocks
                content = page.content()
                block_selectors = [
                    "form[action*='captcha']",
                    "text=/access denied/i",
                    "text=/blocked/i",
                    "text=/sorry, we're unable to complete your request/i",
                    "text=/error ref:/i"
                ]
                if any(page.locator(sel).count() > 0 for sel in block_selectors):
                    files = save_debug_files(page, product_id, vendor_domain, output_dir, "blocked", timestamp())
                    context.close()
                    return {
                        "Product ID": product_id,
                        "Vendor": vendor_domain,
                        "Search Query": search_query,
                        "Status": "Blocked by Vendor",
                        "Timestamp": timestamp(),
                        **files
                    }

                # Handle modals and vendor-specific actions
                if "toolnut.com" in vendor_domain:
                    handle_toolnut_modal(page)
                handle_general_modals(page)
                handle_vendor_specific(page, vendor_domain)

                # Extract price
                price_text = extract_price(page, vendor_domain)

                # Save output
                date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
                folder_name = f"{product_id}_{date_stamp}"
                out_path = Path(output_dir) / folder_name
                out_path.mkdir(parents=True, exist_ok=True)
                safe_vendor = clean_filename(vendor_domain)
                base_name = f"{safe_vendor}_{timestamp()}"
                
                screenshot_path = out_path / f"{base_name}.png"
                html_path = out_path / f"{base_name}.html"
                page.screenshot(path=str(screenshot_path), full_page=True)
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Debug for Home Depot
                debug_files = {}
                if "homedepot.com" in vendor_domain and "<h1" not in content.lower():
                    print("Page content might not be fully loaded, capturing debug files")
                    page.wait_for_timeout(10000)
                    debug_files = save_debug_files(page, product_id, vendor_domain, output_dir, "debug", timestamp())

                context.close()
                return {
                    "Product ID": product_id,
                    "Vendor": vendor_domain,
                    "Search Query": search_query,
                    "Final URL": current_url,
                    "Screenshot": str(screenshot_path),
                    "HTML": str(html_path),
                    "Timestamp": timestamp(),
                    "Price": price_text,
                    "Status": "Success",
                    **debug_files
                }

    except Exception as e:
        try:
            if 'page' in locals() and 'context' in locals():
                files = save_debug_files(page, product_id, vendor_domain, output_dir, "error", timestamp())
                context.close()
                return {
                    "Product ID": product_id,
                    "Vendor": vendor_domain,
                    "Search Query": search_query,
                    "Timestamp": timestamp(),
                    "Status": f"Error: {str(e)}",
                    **files
                }
        except:
            pass
        return {
            "Product ID": product_id,
            "Vendor": vendor_domain,
            "Search Query": search_query,
            "Timestamp": timestamp(),
            "Status": f"Error: {str(e)}"
        }


def capture_task(args):
    return search_and_capture(*args)


def run_parallel_captures(tasks, num_processes=2):
    from multiprocessing import Pool
    from tqdm import tqdm
    results = []
    with Pool(processes=num_processes) as pool:
        for result in tqdm(pool.imap_unordered(capture_task, tasks), total=len(tasks), desc="Auditing"):
            results.append(result)
    return results