from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_common_options(debug=True):
    options = Options()
    options.add_argument('--no-sandbox')
    if not debug:
        options.add_argument('--headless')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--incognito')
    options.add_argument('--window-size=390,844')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    return options

def init_browser(debug):
    options = get_common_options(debug)
    browser = webdriver.Chrome(options=options)
    browser.get('https://www.jd.com')
    return browser

def get_detail(browser, skuid):
    url = f"https://item.jd.com/{str(skuid)}.html"
    browser.get(url)

    result = browser.execute_script("""
    async function get_detail() {
        var n = {
            cat: pageConfig.product.cat.join(","),
            shopId: pageConfig.product.shopId,
            skuId: pageConfig.product.skuid,
            venderId: pageConfig.product.venderId,
        }
        return n;
    }
    const n = await get_detail();
    return n;
    """)
    
    return result
    
