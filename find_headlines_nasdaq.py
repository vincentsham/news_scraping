import os
import argparse
import random
import time
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import re

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
        # 禁用图片加载
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
    """安全地查找元素，处理可能的StaleElementReferenceException."""
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
    """安全地查找元素，处理可能的StaleElementReferenceException."""
    try:
        content = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((by, value)))
        return content
    except StaleElementReferenceException:
        time.sleep(2)
        content = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((by, value)))
        return content

def process_datetime(date):
    eastern = timezone('US/Eastern')
    d = pd.to_datetime(datetime.now(eastern))
    if 'min' in date.lower():
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
        d = pd.to_datetime(date).tz_localize(eastern)
    return d

def find_headlines(driver, headline_file_path, headline_url,
                   desired_page, last_date, last_headline, 
                   last_url, list_df, index):
    # 'aapl'


    # driver.minimize_window()
    no_headlines = 0
    now_retry = 0
    max_retries = 3
    headlines = []
    while True:
        if now_retry == max_retries:
            return desired_page
        try:
            driver.get(headline_url)
            # from bs4 import BeautifulSoup
            # soup = BeautifulSoup(driver.page_source)
            # driver.minimize_window()

            attempts = 0

            while attempts < 2:
                try:
                    # 设置检测是否访问成功的标志，此处是加载其logo
                    flag_loaded = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'nsdq-logo--default'))
                    )
                    print("Loaded Logo")
                    break
                except NoSuchElementException:
                    attempts += 1
                    print(attempts, "times meet NoSuchElementException, Maybe meet Special Page")
            current_page = 0
            while True:
                headlines = []
                # next_pages = safe_find_elements(driver, By.CLASS_NAME, 'pagination__page')
                
                if desired_page == 9999:
                    print("This stock has been done")
                    break
                
        
                if current_page < desired_page:
                    next_page = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'pagination__next')))
                    driver.execute_script("arguments[0].click();", next_page)
                    current_page += 1
                    if next_page.get_attribute("disabled") == "true":
                        print("Last page reached.")
                        break
                    continue
                else:
                    # 如果老是断，就改大一点，2s比较稳定
                    time.sleep(2)

                headlines = safe_find_elements(driver, By.CLASS_NAME, 'jupiter22-c-article-list__item')
                # print(headlines[0].get_attribute('outerHTML'))
                for headline in headlines:
                    # 获取 headline的日期和内容

                    headline_date = WebDriverWait(headline, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-article-list__item_timeline')))


                    headline_content = WebDriverWait(headline, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-article-list__item_title')))

 
                    headline_url = WebDriverWait(headline, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-article-list__item_title_wrapper'))).get_attribute('href')
                    if type(headline_url) == str and "https://www" not in headline_url:
                        headline_url = "https://www.nasdaq.com" + headline_url

                    headline_content_cleaned = headline_content.text.replace(u"\u2018", "'").replace(u"\u2019", "'")
                    date = process_datetime(headline_date.text)

                    last_date = pd.to_datetime(last_date).tz_convert(eastern)

                    if date.date() == last_date.date() and (headline_content_cleaned == last_headline or headline_url == last_url):
                        break
                    if date <= last_date:
                        break

                    data = {
                        'date': [date.tz_convert('UTC')],
                        'headline': [headline_content_cleaned],
                        'url': [headline_url]
                    }

                    # 创建一个DataFrame
                    df = pd.DataFrame(data)
                    # 检查文件是否存在并且非空
                    file_exists = os.path.isfile(headline_file_path) and os.path.getsize(headline_file_path) > 0
                    # 然后根据文件是否已存在来决定是否写入列名
                    df.to_csv(headline_file_path, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')
                    list_df.at[index, 'desired_page'] = desired_page
                    list_df.to_csv(list_file_path, index=False)
                    no_headlines += 1
                # 翻页按钮
                try:
                    exist_next = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'pagination__next')))
                except:
                    exist_next = None

                if exist_next:
                    active_page_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'pagination__page--active')))         
                    current_page = int(active_page_element.text)
   

                # next_page = next_pages[0]
                # 只有一页

                if opt.restart == False and date.date() == last_date.date() and (headline_content_cleaned == last_headline or headline_url == last_url):
                    print("Last news reach", last_headline, last_date)
                    desired_page = 9999
                    break

                if opt.restart == False and date <= last_date:
                    print("Last date reach", last_date)
                    desired_page = 9999
                    break

                if not exist_next:
                    print("Only one page")
                    desired_page = 9999
                    break

                next_page = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pagination__next')))
                if next_page.get_attribute("disabled") == "true":
                    print("Last page reached.")
                    desired_page = 9999
                    break
                print("current_page:", current_page)
                desired_page = current_page

                # Click the next page button
                driver.execute_script("arguments[0].click();", next_page)
            return desired_page, no_headlines
        except TimeoutException:
            try:
                # 查找页面中的<h1>标签 判断是否是特殊情况
                h2_elements = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'alert__heading')))
                # 找到匹配项后退出循环
                for h2 in h2_elements:
                    if h2.text.find("trading") != -1:
                        print("time out, finding alerts")
                        print("Alert found")
                        desired_page = 9999
                        return desired_page, no_headlines
            except TimeoutException:
                print("Time out or wrong url")
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
        if row['tic'] == 'VIXM':
            continue
        if row['tic'] == 'GEN':
            continue
        if opt.type == 'all':
            pass
        elif opt.type == row['type']:
            pass
        else:
            continue
        headline_file_path = os.path.join(directory, 'headlines', subpath, str(row['tic']) + ".csv")
        stock = str(row['tic']).lower().replace('-', '.')
        headlines_url = f"https://www.nasdaq.com/market-activity/{row['type']}/{stock}/news-headlines"
        print(headlines_url)
        desired_page, no_headlines = find_headlines(driver, headline_file_path, headlines_url, 
                                      row['desired_page'], row['last_date'], row['last_headline'],
                                      row['last_url'], list_df, index)
        # driver.close()
        list_df.at[index, 'desired_page'] = desired_page
        list_df.at[index, 'no_headlines'] = no_headlines
        print("now desired_page: ", list_df.loc[row.name, 'desired_page'], 
              "now no_headlines: ", list_df.loc[row.name, 'no_headlines'],
        )
        list_df.to_csv(list_file_path, index=False)
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
    list_stocks = "list_stocks_nasdaq.csv"
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





