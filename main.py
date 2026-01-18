import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Expanded products with sub-model support
products = {
    "iphone 15 pro max": {"market_value": 3000, "min_profit": 500},
    "iphone 15 pro":     {"market_value": 2600, "min_profit": 450},
    "iphone 15 plus":    {"market_value": 2200, "min_profit": 400},
    "iphone 15":         {"market_value": 2000, "min_profit": 350},
    "iphone 14 pro max": {"market_value": 2200, "min_profit": 400},
    "iphone 14 pro":     {"market_value": 1900, "min_profit": 350},
    "iphone 14":         {"market_value": 1500, "min_profit": 300},
    "iphone 13 mini":    {"market_value": 900, "min_profit": 200},
    "iphone 13":         {"market_value": 1000, "min_profit": 250},
    "iphone 12":         {"market_value": 650, "min_profit": 200}
}

problems = ["icloud", "piese", "recarosare", "blocat", "nefunctional"]

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
    print("Options: 15 Pro Max, 15 Pro, 15 Plus, 15, 14, 13 mini, etc.")
    user_search = input("Which specific model are you looking for? ").strip().lower()

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        search_query = user_search.replace(" ", "-")
        url = f"https://www.olx.ro/oferte/q-{search_query}/?search%5Border%5D=created_at%3Adesc"
        driver.get(url)
        
        print(f"\nScanning OLX for: {user_search.upper()}...")
        print("'DE ACORD' (Cookies)")
        time.sleep(5) 

        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cy="l-card"]')))

        all_ads = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="l-card"]')
        
        deals_found = []

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
                    
                    condition_note = "PERFECT"
                    if "spate spart" in title or "capac spart" in title:
                        target_buy -= 200
                        condition_note = "SPATE SPART"
                    elif "ecran spart" in title or "display spart" in title:
                        target_buy -= 500
                        condition_note = "ECRAN SPART"

                    if current_price <= target_buy:
                        profit = data["market_value"] - current_price
                        link = ad.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        deals_found.append({
                            "title": title.upper(),
                            "type": model_category,
                            "price": current_price,
                            "profit": profit,
                            "note": condition_note,
                            "link": link
                        })

            except Exception:
                continue

        print("\n" + "="*40)
        print(f"PROFITABLE DEALS FOR: {user_search.upper()}")
        print("="*40)
        
        if not deals_found:
            print("No deals.")
        else:
            for deal in deals_found:
                print(f"{deal['title']}")
                print(f"   [Type: {deal['type']}] | [Condition: {deal['note']}]")
                print(f"   BUY: {deal['price']} RON | EST. PROFIT: {deal['profit']} RON")
                print(f"   LINK: {deal['link']}")
                print("-" * 20)

    finally:
        print("\nSession complete.")
        driver.quit()

if __name__ == "__main__":
    run_sniper()