import re
import time
import json
from lxml import etree

# 采集站点：美、英、日、法、意、西、德、印、加、澳、墨站
SiteType = {
    'com': {'site': 'https://www.amazon.com', 'currency': 'USD', 'sign': '$'},
    'co.uk': {'site': 'https://www.amazon.co.uk', 'currency': 'GBP', 'sign': '£'},
    'co.jp': {'site': 'https://www.amazon.co.jp', 'currency': 'YEN', 'sign': '￥'},
    'fr': {'site': 'https://www.amazon.fr', 'currency': 'EUR', 'sign': 'EUR'},
    'it': {'site': 'https://www.amazon.it', 'currency': 'EUR', 'sign': 'EUR'},
    'es': {'site': 'https://www.amazon.es', 'currency': 'EUR', 'sign': 'EUR'},
    'de': {'site': 'https://www.amazon.de', 'currency': 'EUR', 'sign': 'EUR'},
    'in': {'site': 'https://www.amazon.in', 'currency': 'INR', 'sign': ''},
    'ca': {'site': 'https://www.amazon.ca', 'currency': 'CDN', 'sign': '$'},
    'com.au': {'site': 'https://www.amazon.com.au', 'currency': 'USD', 'sign': '$'},
    'com.mx': {'site': 'https://www.amazon.com.mx', 'currency': 'USD', 'sign': '$'},
}

# 评论日期 日站的时间格式是数字形式的
Month = {
    'com': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']},
    'co.uk': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']},
    'fr': {'month': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']},
    'it': {'month': ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
                     'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']},
    'es': {'month': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'noviembre', 'Diciembre']},
    'de': {'month': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                     'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']},
    'in': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']},
    'ca': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']},
    'com.au': {'month': ['January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December']},
    'com.mx': {'month': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'noviembre', 'Diciembre']},
}


class Comment:
    """
    解析亚马逊评论页
    实例化类时传入参数：
    html：评论页html文本
    suffix：站点类型('com', 'co.uk', 'co.jp', 'fr', 'it', 'es', 'de', 'in', 'ca')
    类方法get_xxx()返回解析得到的相应字段值
    """

    def __init__(self, html, suffix):
        self.sel = etree.HTML(html)
        self.suffix = suffix

    # 总体评分
    def get_score(self):
        score = 0
        score_1 = self.sel.xpath('//div[@id="cm_cr-product_info"]//span[contains(@class, "rating-out-of-text")]/text()')
        if score_1:
            score = re.findall(r'\d\.?\d*', score_1[0])
            if score:
                score = score[0]
        return score

    # 总评论人数
    def get_count(self):
        count = 0
        count_1 = self.sel.xpath('//div[@id="cm_cr-product_info"]//span[@data-hook="total-review-count"]/text()')
        if count_1:
            count = count_1[0].strip().replace(',', '')
        return count

    # 评分百分比
    def get_percent(self):
        percent = ''
        histogram_review_count = dict()
        histogram_review_count_1 = self.sel.xpath('//div[starts-with(@id, "rev")]//tr[contains(@class, "histogram-row")]')
        histogram_review_count_2 = self.sel.xpath('//div[@id="aggregatedReviews"]/table[@id="histogramTable"]//tr[contains(@class, "histogram-row")]')
        if histogram_review_count_1:
            _histogram_review_count = histogram_review_count_1
        elif histogram_review_count_2:
            _histogram_review_count = histogram_review_count_2
        else:
            _histogram_review_count = ''
        for h in _histogram_review_count[:5]:
            star_1 = h.xpath('./td[1]/*[1]/text()')
            star_2 = h.xpath('./td[1]/text()')
            if star_1:
                _star = star_1[0]
            else:
                _star = star_2[0]
            star = re.findall(r'\d', _star)[0]
            percent_1 = h.xpath('./td[3]//text()')   # 更精确
            percent_2 = h.xpath('.//div[contains(@class, "a-meter") and @aria-label]/@aria-label')
            if percent_1:
                percent = percent_1[0].strip()
            elif percent_2:
                percent = percent_2[0].strip()
            else:
                percent = '0%'
            histogram_review_count[star] = percent
        if histogram_review_count:
            percent = json.dumps(histogram_review_count, ensure_ascii=False)

        return percent

    # 下面是用户评论

    # 所有评论
    def get_comment_list(self):
        comment_list = []
        comment_list_1 = self.sel.xpath('//div[@id="cm_cr-review_list"]/div[@id]')
        if comment_list_1:
            comment_list = comment_list_1
        return comment_list

    # 评论id
    def get_comment_id(self, xp):
        comment_id = ''
        comment_id_1 = xp.xpath('./@id')
        if comment_id_1:
            comment_id = comment_id_1[0].strip()
        return comment_id

    # 评分
    def get_comment_grade(self, xp):
        comment_grade = ''
        comment_grade_1 = xp.xpath('.//a[@title]/@title')
        if comment_grade_1:
            comment_grade_1 = re.findall(r'\d[.,]\d*', comment_grade_1[0])
            if comment_grade_1:
                comment_grade = comment_grade_1[0].replace(',', '.')
        return comment_grade

    # 评论标题
    def get_comment_title(self, xp):
        comment_title = ''
        comment_title_1 = xp.xpath('.//a[@data-hook="review-title"]/text()')
        if comment_title_1:
            comment_title = comment_title_1[0].strip()
        return comment_title

    # 评论用户
    def get_comment_user(self, xp):
        comment_user = ''
        comment_user_1 = xp.xpath('.//a[contains(@data-hook, "author")]/text()')
        if comment_user_1:
            comment_user = comment_user_1[0].strip()
        return comment_user

    # 评论用户链接
    def get_comment_user_link(self, xp):
        comment_user_link = ''
        comment_user_link_1 = xp.xpath('.//a[contains(@data-hook, "author")]/@href')
        if comment_user_link_1:
            comment_user_link = SiteType[self.suffix]['site'] + comment_user_link_1[0].strip()
        return comment_user_link

    # 评论内容
    def get_comment_content(self, xp):
        comment_content_1 = xp.xpath('.//span[contains(@data-hook, "body")]/text()')
        comment_content = ''.join(comment_content_1)
        return comment_content

    # 评论图片
    def get_comment_image(self, xp):
        comment_image_1 = xp.xpath('.//img[@alt="review image"]/@src')
        comment_image = ','.join([image.replace('._SY88', '') for image in comment_image_1])
        return comment_image

    # 评论时期
    def get_comment_date(self, xp):
        comment_date = '1900-01-01'
        comment_date_1 = xp.xpath('.//span[contains(@data-hook, "date")]/text()')
        if comment_date_1:
            comment_date_1 = comment_date_1[0].strip()
            date = re.findall(r'\d+', comment_date_1)
            if self.suffix == 'co.jp':
                comment_date = '-'.join(date)
            else:
                day, year = date
                if self.suffix in ('com', 'ca'):
                    month = comment_date_1.split()[1]
                else:
                    month = re.findall(r'\d\.?\d* (.+) \d+', comment_date_1)
                    if month:
                        month = month[0].strip()
                        if self.suffix in ('es', 'com.mx'):
                            month = month.replace('de', '').strip()
                month = self._format_month(month)
                comment_date = '{}-{}-{}'.format(year, month, day)
        return comment_date

    def _format_month(self, m):
        month = Month[self.suffix]['month']
        for index, item in enumerate(month):
            if item.lower().startswith(m.lower()):
                return index+1

    # 评论点赞数
    def get_comment_vote(self, xp):
        comment_vote = ''
        comment_vote_1 = xp.xpath('.//span[contains(@data-hook, "vote")]/text()')
        if comment_vote_1:
            comment_vote_1 = re.findall(r'\d+', comment_vote_1[0])
            if comment_vote_1:
                comment_vote = comment_vote_1[0]
        return comment_vote

    # 确认购买
    def get_comment_verified(self, xp):
        comment_verified = 0
        comment_verified_1 = xp.xpath('.//span[contains(@data-hook, "avp-badge")]/text()')
        if comment_verified_1:
            comment_verified = 1
        return comment_verified

    # 首页获取总页数:
    def get_page_num(self):
        page_num = 0
        page_button = self.sel.xpath('//div[@id="cm_cr-pagination_bar"]//li[contains(@class, "button")]/a/text()')
        select_button = self.sel.xpath(
            '//div[@id="cm_cr-pagination_bar"]//li[contains(@class, "a-selected page-button")]/a/text()')
        if select_button and int(select_button[0]) == 1:
            page_num = int(page_button[-1])
        return page_num

    # 下一页
    def get_next_page(self):
        next_page = ''
        next_page_1 = self.sel.xpath('//div[@id="cm_cr-pagination_bar"]//li[contains(@class, "a-last")]/a/@href')
        if next_page_1:
            next_page = SiteType[self.suffix]['site'] + next_page_1[0].strip()
        return next_page

    # 是否首页
    def is_first_page(self):
        is_first = False
        select_button = self.sel.xpath(
            '//div[@id="cm_cr-pagination_bar"]//li[contains(@class, "a-selected page-button")]/a/text()')
        if not select_button or int(select_button[0]) == 1:
            is_first = True
        return is_first

    # 最新一条评论
    def get_latest_comment_date(self):
        latest_comment_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        latest_comment_date_1 = self.sel.xpath('//div[@id="cm_cr-review_list"]/div[@id][1]')
        if latest_comment_date_1:
            latest_comment_date = self.get_comment_date(latest_comment_date_1[0])
        return latest_comment_date
