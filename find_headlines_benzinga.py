import os
import argparse
import random
import time
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import re
from tqdm import tqdm
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions

eastern = timezone('US/Eastern')

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/93.0.961.47 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
]

def get_webdriver(browser_type='chrome'):
    if browser_type == 'chrome':
        # random_user_agent = random.choice(user_agents)
        random_user_agent = user_agents[0]
        headers = {'User-Agent': random_user_agent}
        options = Options()
        options.add_argument(f"user-agent={random_user_agent}")
        options.page_load_strategy = 'none'
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--headless=new')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument('--log-level=3')
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        options.profile = profile
        driver = webdriver.Chrome(options=options)
        driver.delete_all_cookies()
        driver.execute_cdp_cmd("Network.setBlockedURLs", {
            "urls": ["*.flv*", "*.png", "*.jpg*", "*.jepg*", "*.gif*"]
        })

    elif browser_type == 'firefox':
        options = FirefoxOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        driver.delete_all_cookies()
    else:
        raise
    return driver

def safe_find_element(driver, by, value):
    try:
        content = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((by, value)))
        return content
    except StaleElementReferenceException:
        time.sleep(2)
        content = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((by, value)))
        return content


def safe_find_elements(driver, by, value):
    try:
        content = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((by, value)))
        return content
    except StaleElementReferenceException:
        time.sleep(2)
        content = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((by, value)))
        return content

def process_datetime(date, block_date):
    eastern = timezone('US/Eastern')
    d = pd.to_datetime(datetime.now(eastern))
    if date is None:
        d = pd.to_datetime(block_date).tz_localize(eastern)
    elif 'min' in date.lower():
        n = re.findall(r'^\d+', date)[0]
        d = d.replace(second=0, microsecond=0)
        d = d - timedelta(minutes=int(n))
    elif 'hour' in date.lower():
        n = re.findall(r'^\d+', date)[0]
        d = d.replace(minute=0, second=0, microsecond=0)
        d = d - timedelta(hours=int(n))
    elif 'day' in date.lower():
        n = re.findall(r'^\d+', date)[0]
        d = d - timedelta(days=int(n))
        d = d.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # print("Before", date)
        d = pd.to_datetime(date).tz_localize(eastern)
        # print("After", date)
    return d

def find_headlines(driver, headline_file_path, headline_url,
                   desired_page, last_date, last_headline, 
                   last_url, list_df, index):
    # 'aapl'


    # driver.minimize_window()
    no_headlines = 0
    now_retry = 0
    max_retries = 10
    headlines = []
    sponser = 0
    last_date = pd.to_datetime(last_date)
    if last_date.tzinfo is None:
        last_date = last_date.tz_localize(eastern) 
    else:
        last_date = pd.to_datetime(last_date).tz_convert(eastern)
    while True:
        try:
            time.sleep(1)
            driver.get(headline_url)
            # html_source = driver.page_source
            # print(html_source)
            # time.sleep(2)
            current_page = 0
            last_num_headlines = 0
            while True:
                headlines = []
                # next_pages = safe_find_elements(driver, By.CLASS_NAME, 'pagination__page')
                
                # if desired_page == 9999:
                #     print("This stock has been done")
                #     return desired_page, no_headlines
                
                if now_retry < max_retries:
                    table = safe_find_element(driver, By.CLASS_NAME, "news-content")
                    time.sleep(1)
                    headlines = safe_find_elements(table, By.XPATH, "./div/ul/li")
                    
                    blocks = safe_find_elements(table, By.XPATH, "./div")
                    block_idx = max(-5, -len(blocks))
                    block_date = safe_find_element(blocks[block_idx], By.XPATH, ".//h2").get_property('textContent')
                    block_date = datetime.strptime(block_date, '%A, %B %d, %Y').date()


                    num_headlines = len(headlines)
                    
                    if last_num_headlines == num_headlines:
                        now_retry += 1
                    elif num_headlines > last_num_headlines:
                        now_retry = 0
                        last_num_headlines = num_headlines

                    print("no_headlines:", num_headlines, 'no_blocks', len(blocks), "block date:", block_date, "last date:", last_date.date(),  "trial:", now_retry)
                    time.sleep(1)
                    if opt.restart == False and last_date.date() > block_date:
                        now_retry = max_retries
                        continue  

                    next_page = safe_find_element(table, By.XPATH, "./button")
                    # print(next_page.get_attribute('innerHTML'))
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
                    driver.execute_script("arguments[0].click();", next_page)
                    
                    
                    # button = WebDriverWait(table, 10).until(
                    #     EC.element_to_be_clickable((By.XPATH, "./button"))
                    # )
                    # button.click()
                    
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # time.sleep(2)
                    if now_retry > max_retries-1:
                        time.sleep(10)
                    
                    
        
                    continue
                else:
                    pass
                # print("no_headlines:", num_headlines, "block date:", block_date, "last date:", last_date.date(),  "trial:", now_retry)
                table = safe_find_element(driver, By.CLASS_NAME, "news-content")
                blocks = safe_find_elements(table, By.XPATH, "./div")        
   
                
                # print('start', max(0, desired_page), len(blocks))
        
                for block_idx in tqdm(range(len(blocks))):
                    block_date = safe_find_element(blocks[block_idx], By.XPATH, ".//h2").get_property('textContent')
                    block_date = datetime.strptime(block_date, '%A, %B %d, %Y').date()
                    headlines = safe_find_elements(blocks[block_idx], By.XPATH, "./ul/li")
                    # print('len', len(headlines))
                    current_page = block_idx + 1
                    for headline in headlines:

                        if "content-headline-datetime" in safe_find_element(headline, By.CLASS_NAME, "author-date-text").get_property("innerHTML"):
                            headline_date = safe_find_element(headline, By.CLASS_NAME, "content-headline-datetime").get_property('textContent')
                        else:   
                            sponser += 1
                            print("Sponser", sponser)
                            continue

                        headline_content = safe_find_element(headline, By.XPATH, ".//div[@class='content-title']/span").get_property('textContent')

    
                        headline_url = safe_find_element(headline, By.CLASS_NAME, "content-headline").get_attribute('href')
                    

                        headline_content_cleaned = headline_content.replace(u"\u2018", "'").replace(u"\u2019", "'")
                        date = process_datetime(headline_date, block_date)


                        # if date.date() == last_date.date() and (headline_content_cleaned == last_headline or headline_url == last_url):
                        #     break
                        # if date <= last_date:
                        #     break

                        data = {
                            'date': [date.tz_convert('UTC')],
                            'headline': [headline_content_cleaned],
                            'url': [headline_url]
                        }
                        # print(data)

                        df = pd.DataFrame(data)
                        file_exists = os.path.isfile(headline_file_path) and os.path.getsize(headline_file_path) > 0
                        df.to_csv(headline_file_path, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')
                        list_df.at[index, 'desired_page'] = desired_page
                        list_df.to_csv(list_file_path, index=False)
                        no_headlines += 1
                        if opt.restart == False and date is not None and date.date() == last_date.date() and (headline_content_cleaned == last_headline or headline_url == last_url):
                            print("Last news reach", last_headline, last_date)
                            desired_page = 9999
                            return desired_page, no_headlines

                        if opt.restart == False and date is not None and date <= last_date:
                            print("Last date reach", last_date)
                            desired_page = 9999
                            return desired_page, no_headlines
                next_page = safe_find_element(table, By.XPATH, "./button")
                if next_page.get_attribute("disabled") == True:
                    print("Last page reached.")
                    desired_page = 9999
                    return desired_page, no_headlines    

                if now_retry == max_retries:
                    print("Try too many times.")
                    desired_page = 9999
                    return desired_page, no_headlines

 

            return desired_page, no_headlines
        except TimeoutException:
            print("Time out or wrong url")
            time.sleep(5)
            driver = get_webdriver()
            return desired_page, no_headlines
        except ElementClickInterceptedException:
            print("button missed, desired_page:", desired_page)
            return desired_page, no_headlines
        except NoSuchWindowException:
            print("closed window manually, desired_page:", desired_page)
            print("5 sec later, driver will restart, if you want to TERMINATE this process please be quick")
            time.sleep(15)
            driver = get_webdriver()
            return desired_page, no_headlines
        except StaleElementReferenceException:
            now_retry += 1
            print("maybe too fast, elements weren't ready, desired_page:", desired_page)
            try:
                WebDriverWait(driver, 5).until(
                    EC.staleness_of(headlines[0])
                )
            except Exception:
                pass
            continue
            # return desired_page


def start_find(list_df, list_file_path, directory, subpath, browser_type='firefox'):
    driver = get_webdriver(browser_type)

    for index, row in list_df.iterrows():
        print("start: ", index, row["tic"], "from:", row["desired_page"])
        if row["desired_page"] == 9999:
            print("This stock Has been done")
            continue
        # driver = get_webdriver()
        # print("index: ", index)
        # if row['tic'] == 'TSLA':
        #     pass
        # else:
        #     continue
        if row['tic'] == 'VIXM':
            continue
        # if row['tic'] == 'QQQ':
        #     continue
        if opt.type == 'all':
            pass
        elif opt.type == row['type']:
            pass
        else:
            continue
        headline_file_path = os.path.join(directory, 'headlines', subpath, str(row['tic']) + ".csv")
        stock = str(row['tic']).lower().replace('-', '.')
        headlines_url = f"https://www.benzinga.com/quote/{stock}/news"
        print(headlines_url)
        start = time.time()
        desired_page, no_headlines = find_headlines(driver, headline_file_path, headlines_url, 
                                      row['desired_page'], row['last_date'], row['last_headline'],
                                      row['last_url'], list_df, index)
        # driver.close()
        list_df.at[index, 'desired_page'] = desired_page
        list_df.at[index, 'no_headlines'] = no_headlines
        print("now desired_page: ", list_df.loc[row.name, 'desired_page'], 
              "now no_headlines: ", list_df.loc[row.name, 'no_headlines'],
        )
        # break
        list_df.to_csv(list_file_path, index=False)
        # print(int(time.time() - start)+1)
        if time.time() - start < 5:
            time.sleep(int(time.time() - start)+random.randint(1,4))
        # print(list_df)
    driver.close()
    return list_df







if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default='/content/drive/MyDrive/')
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--browser_type", type=str, default='firefox', choices=['chrome', 'firefox'])
    parser.add_argument("--type", choices=['all', 'stocks', 'etf'], default='all')
    opt = parser.parse_args()
    # driver = get_webdriver()
    

    trial = 0
    subpath = ""
    list_stocks = "list_stocks_benzinga.csv"
    # browser_type = ['firefox', 'chrome']
    browser_type = opt.browser_type

  
    list_file_path = os.path.join(opt.dir, list_stocks)
    if not os.path.isfile(list_file_path):
        print("!!! Wrong list_name !!!")
    else:
        list_df = pd.read_csv(list_file_path, encoding="utf-8")
        while not list_df['desired_page'].isin([9999]).all():
            print("need find")
            list_df = start_find(list_df, list_file_path, opt.dir, subpath, browser_type)
            trial += 1
            if trial == 3:
                break
        print("list_stocks completed")





