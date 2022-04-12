import requests
import json
from bs4 import BeautifulSoup, SoupStrainer

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Accept-Language": "ru",
    "Connection": "keep-alive",
}
parser = 'lxml'


def get_data(url: str) -> str | None:
    """
    Returns string containing all html code from a page with given url
    """
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return response.text


def extract_product_info(soup: BeautifulSoup) -> dict[str, str]:
    """
    Extracts all info about product and return dict containing product info,
    exactly: price, sale price, brand, name, vendor  code
    """
    product_price = ''.join(soup.find('del', class_='price-block__old-price').text.strip().split()[:-1])
    product_price_with_sale = ''.join(soup.find('span', class_='price-block__final-price').text.strip().split()[:-1])

    brand_and_name = soup.find('h1', class_='same-part-kt__header').find_all('span')
    product_brand = brand_and_name[0].text.strip()
    product_name = brand_and_name[1].text.strip()

    product_vendor_code = soup.find('span', id='productNmId').text.strip()

    product_detail = {
        'product_brand': product_brand,
        'product_name': product_name,
        'product_vendor_code': product_vendor_code,
        'product_price': product_price,
        'product_price_with_sale': product_price_with_sale,
    }

    return product_detail


def get_product_info(url: str) -> dict[str, str] | None:
    """
    Parse wildberries product info by product url,

    """
    html = get_data(url)

    # check if data is get properly
    if html:
        # All info that we need is contained in div with class product-detail so lets parse only from that div
        # Make parsing faster for about 40%
        div_containing_product_details = SoupStrainer(class_="product-detail")
        soup = BeautifulSoup(html, parser, parse_only=div_containing_product_details)

        # getting product details
        product_detail = extract_product_info(soup)

        # writing data to output file
        with open('products.json', 'w') as file:
            json.dump(product_detail, file, indent=4, ensure_ascii=False)
        return product_detail
    else:
        return None


url = 'https://www.wildberries.ru/catalog/70796973/detail.aspx?targetUrl=GP'
get_product_info(url)
