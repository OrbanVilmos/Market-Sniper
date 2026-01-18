import time
import winsound
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

products = {
    "iphone 15": {"market_value": 2600, "min_profit": 350},
    "iphone 14": {"market_value": 2000, "min_profit": 300},
    "iphone 13": {"market_value": 1600, "min_profit": 250},
    "iphone 12": {"market_value": 1200, "min_profit": 200}
}

problems = ["icloud", "piese", "recarosare", "blocat", "nefunctional"]

def clean_price(price_string):
    numeric_filter = filter(str.isdigit, price_string)
    numeric_string = "".join(numeric_filter)
    return int(numeric_string) if numeric_string else 0

def run_sniper():
    print("🤖 Smart Appraisal Sniper: Online...")
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        url = "https://www.olx.ro/oferte/q-iphone-15/?search%5Border%5D=created_at%3Adesc"
        driver.get(url)
        
        print("🚨 ACTION: Click 'DE ACORD' (Cookies) now!")
        time.sleep(8) 

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cy="l-card"]')))

        all_ads = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="l-card"]')
        print(f"🔎 Analyzing {len(all_ads)} ads for profit potential...\n")

        for ad in all_ads:
            try:
                full_card_text = ad.get_attribute('innerText')
                lines = [line.strip() for line in full_card_text.split('\n') if line.strip()]
                
                title = lines[0].lower()
                link = ad.find_element(By.TAG_NAME, 'a').get_attribute('href')
                
                if any(flag in title for flag in problems):
                    continue

                price_raw = ""
                for line in lines:
                    if "lei" in line.lower():
                        price_raw = line
                        break
                
                current_price = clean_price(price_raw)
                if current_price < 200 or current_price > 10000: continue

                for model, data in products.items():
                    if model in title:
                        target_buy = data["market_value"] - data["min_profit"]
                        condition_note = "PERFECT"

                        if "spate spart" in title or "capac spart" in title:
                            target_buy -= 200
                            condition_note = "SPATE SPART (-200 RON)"
                        elif "ecran spart" in title or "display spart" in title:
                            target_buy -= 500
                            condition_note = "ECRAN SPART (-500 RON)"

                        if current_price <= target_buy:
                            actual_profit = data["market_value"] - current_price - (200 if "spate" in condition_note else 500 if "ecran" in condition_note else 0)
                            print(f"!!![DEAL FOUND] {title.upper()}!!!")
                            print(f"   - Condition: {condition_note}")
                            print(f"   - Buy for: {current_price} RON | Target: {target_buy} RON")
                            print(f"   - Estimated Flip Profit: {actual_profit} RON")
                            print(f"   - Link: {link}\n")
                        else:
                            print(f"[MARKET] {model} ({condition_note}): {current_price} RON (Buy at: {target_buy})")

            except Exception:
                continue

    finally:
        print("\nSession complete.")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    run_sniper()