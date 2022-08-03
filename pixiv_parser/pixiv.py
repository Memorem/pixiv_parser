import os, requests, asyncio, aiohttp, pickle, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from tqdm import tqdm

from datetime import datetime

from config import HEADERS, LOGIN, PASSWORD, PATH_IMAGE, PATH_SOURCE
from config.logger import info, error

logging.getLogger('WDM').setLevel(logging.NOTSET)


options = Options()
options.headless = True
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument(f'user-agent={HEADERS["user-agent"]}')


def get_page(user_id: str) -> dict:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    links = []
    info('Processing... ')
    try:
        driver.get(f'https://www.pixiv.net/en/users/{user_id}/artworks')
        with open(f'{PATH_SOURCE}cookies.pkl', 'rb') as f:
            cookie = pickle.load(f)
        for c in cookie:
            driver.add_cookie(c)
        driver.refresh()
        WebDriverWait(driver, timeout=10).until(lambda x: x.find_element(By.CSS_SELECTOR, 'div.sc-gulj4d-4.jaZOzF > div'))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        author = soup.select_one('div.sc-gulj4d-4.jaZOzF > div').get('title')
        links.append({'author': author})
        WebDriverWait(driver, timeout=10).until(lambda x: x.find_element(By.CSS_SELECTOR, 'nav.sc-xhhh7v-0.kYtoqc'))
        page = 1
        while True:
            try:
                driver.get(f'https://www.pixiv.net/en/users/{user_id}/artworks?p={str(page)}')
                WebDriverWait(driver, timeout=6).until(lambda x: x.find_element(By.CSS_SELECTOR, 'ul.sc-9y4be5-1.jtUPOE > li'))

                soup = BeautifulSoup(driver.page_source, 'lxml')
                content = soup.select('ul.sc-9y4be5-1.jtUPOE > li')
                for item in content:
                    link = 'https://www.pixiv.net' + item.select_one('div.sc-iasfms-0.jtpclu > a').get('href')
                    name = item.select_one('div.sc-iasfms-0.jtpclu > a').text
                    links.append({
                        'link': link,
                        'name': name,
                    })
                info(f'Getting page {page}')
                page += 1
            except:
                info('Done!')
                break
    except Exception:
        error(Exception.__class__.__name__)
    finally:
        driver.close()
        driver.quit()

    return links

async def get_json(user_id, session):
    async with session.get(f'https://www.pixiv.net/ajax/illust/{user_id}/pages?lang=en', timeout=3) as response:
        return await response.json()

async def collect_tasks_json(users_id, session):
    tasks = [asyncio.create_task(get_json(user_id, session)) for user_id in users_id]
    return await asyncio.gather(*tasks)

async def collect_data(data):
    cookies = get_cookies()
    users_id, pre_links = [], []
    author = data[0].get('author', 'No author')
    for item in data:
        if item.get('link') is not None:
            user_id = item['link'].split('/')[-1].strip()
            users_id.append(user_id)
    users_id = set(users_id)
    async with aiohttp.ClientSession(cookies=cookies, headers=HEADERS) as session:
        response = await collect_tasks_json(users_id, session)
        for r in response:
            for url in r['body']:
                link = url['urls'].get('original')
                if link:
                    pre_links.append(link)

    async def infinity(links):
        info('Downloading... ')
        for link in tqdm(links):
            try:
                name = link.split('/')[-1].split('.')[-2].strip()
                folder_name = name.split('_')[-2]
                path_to_download = f'{PATH_IMAGE}{author}\\{folder_name}'
                extention = link.split('.')[-1]
                os.makedirs(path_to_download, exist_ok=True)
                response = requests.get(link, headers=HEADERS)
                with open(f'{path_to_download}\\{name}.{extention}', 'wb') as f:
                    f.write(response.content)
            except Exception:
                error(f'Get problem with {link}\nDownloading... ')
                return await infinity([link])

    await infinity(pre_links)

def authorization(url=r'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2Fen%2F&lang=en&source=pc&view_type=page') -> dict:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    info('Authorization...')
    try:
        driver.get(url)
        driver.implicitly_wait(30)
        driver.find_element(By.CSS_SELECTOR, 'input[type="text"]').click()
        email_pix = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
        email_pix.clear()
        email_pix.send_keys(LOGIN + Keys.ENTER)
        
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').click()
        password_pix = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_pix.clear()
        password_pix.send_keys(PASSWORD + Keys.ENTER)
        driver.implicitly_wait(10)

        WebDriverWait(driver, timeout=10).until(lambda x: x.find_element(By.CSS_SELECTOR, 'div.sc-1asno00-0.feBRRY'))
        with open(f'{PATH_SOURCE}cookies.pkl', 'wb') as f:
            pickle.dump(driver.get_cookies(), f)

        start_time = datetime.now().strftime('%Y.%m.%d::%H.%M')
        with open(f'{PATH_SOURCE}log', 'w', encoding='utf-8') as f:
            f.write(start_time)

    except Exception as ex:
        error(f'Got unexpected issue {ex.__class__.__name__}')
    finally:
        driver.close()
        driver.quit()

def get_cookies():
    cookies = {}
    with open(f'{PATH_SOURCE}cookies.pkl', 'rb') as f:
        cookie = pickle.load(f)
    for item in cookie:
        cookies[item['name']] = item['value']
    
    return cookies

async def main():
    if not os.path.exists(f'{PATH_SOURCE}log'):
        authorization()

    time_now = datetime.now().strftime('%Y.%m.%d::%H.%M')
    with open(f'{PATH_SOURCE}log', 'r', encoding='utf-8') as f:
        time_created = f.read()

    if time_created.split('::')[-2] != time_now.split('::')[-2]:
        authorization()
        
    elif abs(float(time_created.split('::')[-1]) - float(time_now.split('::')[-1])) > 2:
        authorization()

    user_id = input('Enter user id: ')
    pixi = get_page(user_id)
    await collect_data(pixi)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())