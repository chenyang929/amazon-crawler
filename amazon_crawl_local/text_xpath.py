import re
import random
import requests
from lxml import etree
from settings import HEADERS
from parse_product_html import SiteType, ParseProduct
from parse_comment_html import Comment
from pprint import pprint
import datetime


def get_html(url):
    headers = {'User-Agent': random.choice(HEADERS)}
    print(headers)
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        if not exist_captcha(resp.text):
            resp.encoding = 'utf-8'
            with open('test_xpath.html', 'w', encoding='utf-8') as f:
                f.write(resp.text)
        else:
            print('captcha')
    else:
        print(resp.status_code)


def exist_captcha(html):
    sel = etree.HTML(html)
    captcha = sel.xpath('//input[@id="captchacharacters"]')
    if captcha:
        return True
    return False


def parse_html(url, entry):
    with open('test_xpath.html', 'r', encoding='utf-8') as f:
        html = f.read()
    if entry in('l', 'k'):
        parse_list(html, url)
    elif entry == 't':
        parse_top(html, url)
    elif entry == 'tn':
        parse_top_new(html, url)
    elif entry == 'd':
        parse_product(html, url)
    elif entry == 'c':
        parse_comment(html, url)
    else:
        print('no entry')


def parse_list(html, url):
    # 确定站点
    suffix = re.findall(r'www.amazon.(.*?)/', url)[0]  # com美，co.uk英，co.jp日
    domain = SiteType[suffix]
    sign = domain['sign']
    site = domain['site']
    currency = domain['currency']
    sel = etree.HTML(html)
    # category
    category = sel.xpath('//*[@id="s-result-count"]/span/*/text()')
    if category:
        category = '>'.join(category)
    else:
        category = ''
    print(category)

    result_count_xp = sel.xpath('//*[@id="s-result-count"]/text()')
    if result_count_xp:
        result_count = re.findall(r'of (.+) results', result_count_xp[0])
        if result_count:
            result_count = result_count[0].replace(',', '')
        else:
            result_count = ''
    else:
        result_count = ''
    print(result_count)
    products_lst = sel.xpath('//ul[starts-with(@class, "s-result")]/li[@data-asin]')
    for pl in products_lst:
        asin = pl.xpath('./@data-asin')
        if asin:
            asin = asin[0].strip()
        else:
            asin = 0
        # comments
        comments_1 = pl.xpath(
            './/span[@name]/../a[starts-with(@class, "a-size-small a-link-normal")]/text()')
        if comments_1:
            _comments = comments_1[-1].replace(',', '')
            if _comments.isdigit():  # 判断是否为数字
                comments = _comments
            else:
                comments = 0
        else:
            comments = 0
        original_price = pl.xpath('.//span[contains(@aria-label, "Suggested Retail Price")]/text()')
        if original_price:
            original_price = ''.join(original_price[0]).replace('from', '').replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
            if currency == 'EUR':
                original_price = original_price.replace('.', '').replace(',', '.')
            else:
                original_price = original_price.replace(',', '')
        else:
            original_price = 0
        price_1 = pl.xpath('.//span[contains(@class, "a-size-small s-padding-right-micro")]/text()')
        price_2 = pl.xpath('.//span[contains(@class, "sx-price sx-price-large")]/../@aria-label')
        price_3 = pl.xpath('.//span[contains(@class, "a-size-base a-color-price s-price a-text-bold")]/text()')
        price_4 = pl.xpath('.//a[@class="a-link-normal a-text-normal"]/span[@class="a-offscreen"]/text()')
        price_5 = pl.xpath('.//span[@class="sx-price sx-price-large"]')
        if len(price_1) > 0:
            price = price_1
        elif len(price_2) > 0:
            price = price_2[0]
        elif len(price_3) > 0:
            price = price_3
        elif len(price_4) > 0:
            price = price_4[0]
        elif len(price_5) > 0:
            price_whole = price_5[0].xpath('./span[@class="sx-price-whole"]/text()')
            price_fractional = price_5[0].xpath('./sup[@class="sx-price-fractional"]/text()')
            price = '{}.{}'.format(price_whole[0], price_fractional[0])
        else:
            price = 0
        max_price = 0
        if price != 0:
            price = ''.join(price).replace('from', '').replace(sign, '')
            if currency == 'EUR':
                price = price.replace('.', '').replace(',', '.')
            else:
                price = price.replace(',', '')

            if '-' in price:
                price, max_price = [p.strip() for p in price.split('-')]
        try:
            price = float(price)
            max_price = float(max_price)
        except ValueError:
            print('ValueError')
        print(asin, comments, original_price, price, max_price)
    next_page = sel.xpath('//a[@id="pagnNextLink"]/@href')
    if next_page:
        next_page_url = site + next_page[0]
        print(next_page_url)


def parse_top(html, url):
    suffix = re.findall(r'www.amazon.(.*?)/', url)[0]
    domain = SiteType[suffix]
    sign = domain['sign']
    currency = domain['currency']

    sel = etree.HTML(html)
    category = sel.xpath('//h1[@id="zg_listTitle"]/span/text()')
    if category:
        category = category[0].strip()
    else:
        category = ''

    products_lst_1 = sel.xpath('//div[starts-with(@class, "zg_itemImmersion")]')  # 美英法站
    products_lst_2 = sel.xpath('//div[starts-with(@class, "zg_itemRow")]')  # 日站
    if products_lst_1:
        products_lst = products_lst_1
    elif products_lst_2:
        products_lst = products_lst_2
    else:
        products_lst = ''

    for pl in products_lst:
        # asin
        asin = pl.xpath('.//div[@data-p13n-asin-metadata]/@data-p13n-asin-metadata')
        if asin:
            asin = eval(asin[0])['asin']
            rank = pl.xpath('.//span[@class="zg_rankNumber"]/text()')
            if rank:
                rank = rank[0].strip().replace('.', '')
            else:
                rank = 0
            try:
                price_1 = pl.xpath('.//span[starts-with(@class, "a-size-base a-color-price")]/span/text()')
                if len(price_1) > 0:
                    _price = ''.join(price_1).replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
                    if currency == 'EUR':
                        _price = _price.replace('.', '').replace(',', '.')
                    else:
                        _price = _price.replace(',', '')
                    if '-' in _price:
                        price, max_price = [p.strip() for p in _price.split('-')]
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = ''.join(re.findall(r'\d+\.?\d*', max_price))
                    else:
                        price = _price
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = 0
                else:
                    price = 0
                    max_price = 0

                price = float(price)
                max_price = float(max_price)
            except:
                price = 0
                max_price = 0
            percent = ''
            movement_1 = 0
            movement_2 = 0
            percent_xp_1 = pl.xpath('.//span[@class="zg-percent-change"]/text()')
            percent_xp_2 = pl.xpath('.//span[@class="zg_percentChange"]/text()')
            if percent_xp_1:
                percent = percent_xp_1
            elif percent_xp_2:
                percent = percent_xp_2
            if percent:
                percent = percent[0].strip().replace(',', '')
            movement_xp = pl.xpath('.//span[@class="zg_salesMovement"]/text()')
            if movement_xp:
                movement = re.findall(r'\d,?\d*', movement_xp[0])
                if len(movement) == 2:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = movement[1].replace(',', '')
                elif len(movement) == 1:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = 0
            print(asin, rank, price, max_price, percent, movement_1, movement_2)

    current_page = sel.xpath('//ol[starts-with(@class, "zg_pagination")]/li[contains(@class, "zg_page zg_selected")]/a/@page')
    if current_page:
        current_page_num = current_page[0].strip()
        if current_page_num.isdigit():
            next_page_id = int(current_page_num) + 1
            print('next_page_id:', next_page_id)
            next_page = sel.xpath('//ol[starts-with(@class, "zg_pagination")]/li/a[@page="%s"]/@href' % next_page_id)
            if next_page:
                next_page_url = next_page[0].strip()
                print(next_page_url)
        else:
            print("current_page_num is not digit")
    else:
        print("no current page")


def parse_top_new(html, url):
    suffix = re.findall(r'www.amazon.(.*?)/', url)[0]
    domain = SiteType[suffix]
    sign = domain['sign']
    currency = domain['currency']

    sel = etree.HTML(html)
    category = sel.xpath('//h1/span[@class="category"]/text()')
    if category:
        category = category[0].strip()
    else:
        category = ''
    print('category: ', category)
    products_lst_3 = sel.xpath('//ol[starts-with(@id, "zg-ordered-list")]/li')  # 代理问题
    if products_lst_3:
        products_lst = products_lst_3
    else:
        products_lst = ''

    for pl in products_lst:
        # asin
        product_url = pl.xpath('.//a[contains(@class,"a-link-normal")]/@href')
        if product_url:
            asin = re.findall(r'/dp/(.+)/ref', product_url[0])
            if asin:
                asin = asin[0].strip()
            else:
                continue
            rank = pl.xpath('.//span[contains(text(), "#")]/text()')
            if rank:
                rank = rank[0].strip().replace('#', '')
            else:
                rank = 0
            release_date = pl.xpath('.//span[@class="zg-release-date"]/text()')
            if release_date:
                release_date = release_date[0]
            print('release_date: ', release_date)
            try:
                price_1 = pl.xpath('.//span[starts-with(@class, "a-size-base a-color-price")]/span/text()')
                if len(price_1) > 0:
                    _price = ''.join(price_1).replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
                    if currency == 'EUR':
                        _price = _price.replace('.', '').replace(',', '.')
                    else:
                        _price = _price.replace(',', '')
                    if '-' in _price:
                        price, max_price = [p.strip() for p in _price.split('-')]
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = ''.join(re.findall(r'\d+\.?\d*', max_price))
                    else:
                        price = _price
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = 0
                else:
                    price = 0
                    max_price = 0

                price = float(price)
                max_price = float(max_price)
            except:
                price = 0
                max_price = 0
            percent = ''
            movement_1 = 0
            movement_2 = 0
            percent_xp = pl.xpath('.//span[@class="zg_percentChange"]/text()')
            if percent_xp:
                percent = percent_xp[0].strip().replace(',', '')
            movement_xp = pl.xpath('.//span[@class="zg_salesMovement"]/text()')
            if movement_xp:
                movement = re.findall(r'\d,?\d*', movement_xp[0])
                if len(movement) == 2:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = movement[1].replace(',', '')
                elif len(movement) == 1:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = 0
            print(asin, rank, price, max_price, percent, movement_1, movement_2)

    next_page = sel.xpath('//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href')
    if next_page:
        next_page_url = next_page[0].strip()
        print(next_page_url)
    else:
        print("no next page")


def parse_product(html, url):
    # 确定站点
    suffix = re.findall(r'www.amazon.(.*?)/', url)[0]

    product = ParseProduct(html, suffix)

    _name = product.get_title()

    first_title = product.get_first_title()

    url_id = product.get_asin()

    brand = product.get_brand()

    discount = product.get_discount()

    original_price = product.get_original_price()

    price, max_price = product.get_price_maxprice()

    grade_count = product.get_grade_count()

    review_count = product.get_review_count()

    questions = product.get_questions()

    attribute = product.get_attribute()

    main_image_url = product.get_main_image()

    extra_image_urls = product.get_extra_images()

    if not main_image_url and extra_image_urls:
        main_image_url = extra_image_urls.split(',')[0]

    description = product.get_description()

    generation_time = product.get_generations_time()

    shop_name, shop_url = product.get_shop()

    reserve_field_1 = product.get_reserve_1()

    reserve_field_2 = product.get_reserve_2()

    reserve_field_3 = product.get_reserve_3()

    reserve_field_4 = product.get_reserve_4()

    reserve_field_5 = product.get_reserve_5()

    reserve_field_6, reserve_field_7 = product.get_reserve_6_7()

    print('first_title: {}'.format(first_title))
    print('asin: {}'.format(url_id))
    print('brand: {}'.format(brand))
    print('_name: {}'.format(_name))
    print('discount: {}'.format(discount))
    print('original_price: {}'.format(original_price))
    print('price: {}'.format(price))
    print('max_price: {}'.format(max_price))
    print('grade_count: {}'.format(grade_count))
    print('review_count: {}'.format(review_count))
    print('questions: {}'.format(questions))
    print('attribute: {}'.format(attribute))
    print('image_url: {}'.format(main_image_url))
    print('extra_image_urls: {}'.format(extra_image_urls))
    print('description: {}'.format(description))
    print('generation_time: {}'.format(generation_time))
    print('reserve_field_1: {}'.format(reserve_field_1))
    print('reserve_field_2: {}'.format(reserve_field_2))
    print('reserve_field_3: {}'.format(reserve_field_3))
    print('reserve_field_4: {}'.format(reserve_field_4))
    print('reserve_field_5: {}'.format(reserve_field_5))
    print('reserve_field_6: {}'.format(reserve_field_6))
    print('reserve_field_7: {}'.format(reserve_field_7))
    print('shop_name: {}'.format(shop_name))
    print('shop_url: {}'.format(shop_url))


def parse_comment(html, url):
    page_url = url
    suffix = re.findall(r'www.amazon.(.*?)/', url)[0]

    comment = Comment(html, suffix)

    page_num = comment.get_page_num()
    next_page = comment.get_next_page()
    review_count = comment.get_count()
    is_first_page = comment.is_first_page()
    if is_first_page:
        latest_comment_date = comment.get_latest_comment_date()
        print('latest_comment_date: ', latest_comment_date)
    print('page_num: ', page_num)
    print('next_page: ', next_page)
    print('review_count: ', review_count)
    print('is_first_page: ', is_first_page)

    grade_score = comment.get_score()

    print('score:', grade_score)

    comments_list = comment.get_comment_list()
    for xp in comments_list:
        review_id = comment.get_comment_id(xp)
        review_grade = comment.get_comment_grade(xp)
        review_title = comment.get_comment_title(xp)
        review_user = comment.get_comment_user(xp)
        review_user_link = comment.get_comment_user_link(xp)
        review_date = comment.get_comment_date(xp)
        review_content = comment.get_comment_content(xp)
        review_image = comment.get_comment_image(xp)
        review_vote = comment.get_comment_vote(xp)
        review_verified = comment.get_comment_verified(xp)

        print('review_id: ', review_id)
        print('review_grade: ', review_grade)
        print('review_title: ', review_title)
        print('review_user: ', review_user)
        print('review_user_link: ', review_user_link)
        print('review_date: ', review_date)
        print('review_content: ', review_content)
        print('review_image: ', review_image)
        print('review_vote: ', review_vote)
        print('review_verified: ', review_verified)
        print('*'*50)


def main(url, entry, flag=1):   # flag确定是否重新下载
    if flag:
        get_html(url)
    parse_html(url, entry)


if __name__ == '__main__':
    l = 'https://www.jollychic.com/baby-shoes-h982?jsort=0201-120'
    d = 'https://www.amazon.com/dp/B07DD3LT4S'
    c = 'https://www.amazon.com/product-reviews/B07BKNYN9J/?&pageNumber=1&pageSize=50&sortBy=recent'
    main(d, 'd', 1)
