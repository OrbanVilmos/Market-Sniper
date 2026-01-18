import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

products = {
    "iphone 15 pro max": {"market_value": 3000, "min_profit": 300},
    "iphone 15 pro":     {"market_value": 2600, "min_profit": 300},
    "iphone 15 plus":    {"market_value": 2200, "min_profit": 200},
    "iphone 15":         {"market_value": 1800, "min_profit": 200},
    "iphone 14 pro max": {"market_value": 2200, "min_profit": 200},
    "iphone 14 pro":     {"market_value": 1900, "min_profit": 200},
    "iphone 14":         {"market_value": 1500, "min_profit": 200},
    "iphone 13 mini":    {"market_value": 900, "min_profit": 200},
    "iphone 13":         {"market_value": 1000, "min_profit": 200},
    "iphone 12":         {"market_value": 650, "min_profit": 200}
}

problems = ["icloud blocat", "display", "piese", "recarosare", "nefunctional"]

def clean_price(price_string):
    numeric_filter = filter(str.isdigit, price_string)
    numeric_string = "".join(numeric_filter)
    return int(numeric_string) if numeric_string else 0

def get_sub_model_type(title):
    t = title.lower()
    if "pro max" in t: return "Pro Max"
    if "pro" in t:     return "Pro"
    if "plus" in t:    return "Plus"
    if "mini" in t:    return "Mini"
    return "Normal"

def run_sniper():
    print("---  iPhone Sniper Pro ---")
    user_search = input("Model name: ").strip().lower()
    
    if user_search in products:
        m_val = products[user_search]["market_value"]
        min_price = int(m_val / 2)
        max_price = m_val
    else:
        matching_vals = [v["market_value"] for k, v in products.items() if user_search in k]
        if not matching_vals:
            print("Model not found in database.")
            return
        min_price = int(min(matching_vals) / 2)
        max_price = max(matching_vals)
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    deals_found = []

    try:
        for page_num in range(1, 4):
            search_query = user_search.replace(" ", "-")
            url = (f"https://www.olx.ro/oferte/q-{search_query}/?"
                   f"search%5Bfilter_float_price%3Afrom%5D={min_price}&"
                   f"search%5Bfilter_float_price%3Ato%5D={max_price}&"
                   f"search%5Border%5D=created_at%3Adesc&page={page_num}")
            
            driver.get(url)
            
            if page_num == 1:
                print(f"\nScanning OLX for: {user_search.upper()} (Price: {min_price}-{max_price} RON)...")
                print("'DE ACORD' (Cookies)")
                time.sleep(5)
            else:
                print(f"Scanning Page {page_num}...")
                time.sleep(2)

            wait = WebDriverWait(driver, 15)
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cy="l-card"]')))
            except:
                print(f"No more listings found or page failed to load at page {page_num}.")
                break

            all_ads = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="l-card"]')
            
            for ad in all_ads:
                try:
                    full_card_text = ad.get_attribute('innerText')
                    lines = [line.strip() for line in full_card_text.split('\n') if line.strip()]
                    title = lines[0].lower()
                    
                    if user_search not in title:
                        continue
                    if any(flag in title for flag in problems):
                        continue

                    model_category = get_sub_model_type(title)
                    price_raw = next((line for line in lines if "lei" in line.lower()), "0")
                    current_price = clean_price(price_raw)
                    if current_price < 200: continue

                    matched_model = next((m for m in products if m in title), None)
                    
                    if matched_model:
                        data = products[matched_model]
                        target_buy = data["market_value"] - data["min_profit"]
                        
                        if "spate spart" in title or "capac spart" in title:
                            target_buy -= 200
                        elif "ecran spart" in title or "display spart" in title:
                            target_buy -= 500

                        if current_price <= target_buy:
                            link = ad.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            deals_found.append({
                                "title": title.upper(),
                                "type": model_category,
                                "price": current_price,
                                "profit": data["market_value"] - current_price,
                                "link": link
                            })
                except:
                    continue

        print("\n" + "="*40)
        print(f"PROFITABLE DEALS FOR: {user_search.upper()}")
        print("="*40)
        
        if not deals_found:
            print("No deals.")
        else:
            for deal in deals_found:
                print(f"{deal['title']}")
                print(f"   [Type: {deal['type']}]")
                print(f"   BUY: {deal['price']} RON | PROFIT: {deal['profit']} RON")
                print(f"   LINK: {deal['link']}")
                print("-" * 20)

    finally:
        print("\nSession complete.")
        driver.quit()

if __name__ == "__main__":
    run_sniper()