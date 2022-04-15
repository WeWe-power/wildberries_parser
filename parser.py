import json

from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, InvalidArgumentException

parser = 'lxml'


def get_soup_parser(
        html: str,
        restrictive_class: str | None = "product-detail"
) -> BeautifulSoup:
    """
    Gets page html and restrictive class that needed to limit parsing zone inside this class, returns soup object
    """

    # All info that we need is contained in div with class product-detail so lets parse only from that div
    # Make parsing faster for about 40%
    div_containing_product_details = SoupStrainer(class_=restrictive_class)
    soup = BeautifulSoup(html, parser, parse_only=div_containing_product_details)

    return soup


def get_web_driver() -> webdriver.Chrome:
    """
    Getting selenium webdriver that make hidden browser operations and has hidden webdriver flag
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    web_driver = webdriver.Chrome(options=options)

    return web_driver


def get_data(url: str) -> str | None:
    """
    Gets html page including dynamically loaded by js content
    """
    driver = get_web_driver()

    # Check if url is correct
    try:
        driver.get(url)
    except InvalidArgumentException:
        return None

    # Tries to find producer info or returns None if cannot find( it may be caused by wrong link )
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "seller-details__title")))
    except TimeoutException:
        return None

    return driver.page_source


def extract_product_info(html: str) -> dict[str, str]:
    """
    Extracts all info about product and return dict containing product info,
    exactly: price, sale price, brand, name, vendor  code
    """

    soup = get_soup_parser(html)

    product_price_with_sale = ''.join(soup.find('span', class_='price-block__final-price').text.strip().split()[:-1])
    # if there is no sale then produce price with sale is our price and product price will be none because there
    # is no block with class price-block__old-price
    try:
        product_price = ''.join(soup.find('del', class_='price-block__old-price').text.strip().split()[:-1])
    except AttributeError:
        product_price = product_price_with_sale

    brand_and_name = soup.find('h1', class_='same-part-kt__header').find_all('span')
    product_brand = brand_and_name[0].text.strip()
    product_name = brand_and_name[1].text.strip()

    product_vendor_code = soup.find('span', id='productNmId').text.strip()
    provider = soup.find('a', class_='seller-details__title').text.strip()

    product_detail = {
        'product_brand': product_brand,
        'product_name': product_name,
        'product_vendor_code': product_vendor_code,
        'product_price': product_price,
        'product_price_with_sale': product_price_with_sale,
        'provider': provider,
    }

    return product_detail


def get_product_info(url: str) -> dict[str, str] | None:
    """
    Parse wildberries product info by product url,

    """
    html = get_data(url)
    if html:
        # getting product details
        product_detail = extract_product_info(html)

        # writing data to output file
        with open('products.json', 'w') as file:
            json.dump(product_detail, file, indent=4, ensure_ascii=False)
        return product_detail
    else:
        return None
