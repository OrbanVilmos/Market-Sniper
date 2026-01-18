from flask import Flask, render_template, request
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

products = {
    "iphone 15 pro max": {"market_value": 2600, "min_profit": 300},
    "iphone 15 pro":     {"market_value": 2400, "min_profit": 300},
    "iphone 15 plus":    {"market_value": 2200, "min_profit": 200},
    "iphone 15":         {"market_value": 2000, "min_profit": 200},
    "iphone 14 pro max": {"market_value": 2000, "min_profit": 200},
    "iphone 14 pro":     {"market_value": 1700, "min_profit": 200},
    "iphone 14":         {"market_value": 1400, "min_profit": 200},
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

def scrape_olx(user_search):
    matching_vals = [v["market_value"] for k, v in products.items() if user_search in k]
    if not matching_vals: return []
    
    min_price = int(min(matching_vals) / 2)
    max_price = max(matching_vals)

    potential_exclusions = ["pro", "max", "plus", "mini"]
    exclude_list = [ex for ex in potential_exclusions if ex not in user_search.lower()]

    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    deals_found = []

    try:
        for page_num in range(1, 4): 
            search_query = user_search.replace(" ", "-")
            url = (f"https://www.olx.ro/electronice-si-electrocasnice/telefoane-mobile/iphone/q-{search_query}/?"
                   f"search%5Bfilter_float_price%3Afrom%5D={min_price}&"
                   f"search%5Bfilter_float_price%3Ato%5D={max_price}&"
                   f"search%5Border%5D=created_at%3Adesc&page={page_num}")
            
            driver.get(url)
            
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cy="l-card"]')))
            except:
                continue 

            all_ads = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="l-card"]')
            for ad in all_ads:
                try:
                    full_card_text = ad.get_attribute('innerText')
                    lines = [line.strip() for line in full_card_text.split('\n') if line.strip()]
                    title = lines[0].lower()
                    
                    if user_search not in title or any(flag in title for flag in problems):
                        continue
                    should_skip = False
                    for ex in exclude_list:
                        if f" {ex}" in f" {title} ":
                            should_skip = True
                            break
                    if should_skip: continue

                    price_raw = next((line for line in lines if "lei" in line.lower()), "0")
                    current_price = clean_price(price_raw)
                    
                    matched_model = next((m for m in products if m in title), None)
                    if matched_model:
                        data = products[matched_model]
                        target_buy = data["market_value"] - data["min_profit"]
                        
                        if current_price <= target_buy and current_price > 200:
                            link = ad.find_element(By.TAG_NAME, 'a').get_attribute('href')
                            deals_found.append({
                                "title": title.upper(),
                                "type": get_sub_model_type(title),
                                "price": current_price,
                                "profit": data["market_value"] - current_price,
                                "link": link
                            })
                except: continue
    finally:
        driver.quit()
    return deals_found
@app.route('/', methods=['GET', 'POST'])
def index():
    deals = None
    search_term = ""
    if request.method == 'POST':
        search_term = request.form.get('model')
        if search_term:
            deals = scrape_olx(search_term.lower())
    return render_template('index.html', deals=deals, search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True)