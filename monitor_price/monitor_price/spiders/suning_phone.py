import scrapy
import time
from monitor_price.items import MonitorPriceItem
from datetime import datetime
import random
import json


class SuningSpider(scrapy.Spider):
    name = "suning_phone"
    allowed_domains = ["hx.suning.com"]
    base_url = "https://hx.suning.com/photo/{page}/{brand}.htm"

    brands = {
        'pa00018': '苹果',
        'pa00009': '华为',
        'pa00022': '小米',
        'pa00019': '三星',
        'pa00003': 'OPPO',
        'pa00005': 'vivo',
        'pa00026': '荣耀',
        'pa00031': 'Realme'
    }

    def start_requests(self):
        for brand_code, brand_name in self.brands.items():
            url = self.base_url.format(page=1, brand=brand_code)
            yield scrapy.Request(
                url,
                headers=self.get_headers(),
                callback=self.parse,
                meta={
                    'brand_code': brand_code,
                    'brand_name': brand_name,
                    'page': 1,
                    'retry_count': 0
                },
                dont_filter=True
            )

    def get_headers(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'
        ]

        return {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'hx.suning.com',
            'Referer': 'https://hx.suning.com/photo/pa00009.htm',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': random.choice(user_agents),
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="120", "Not=A?Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def parse(self, response):
        brand_code = response.meta['brand_code'] #brand_code 是动态网页的API接口，每次都需要传递
        brand_name = response.meta['brand_name'] #品牌名字
        current_page = response.meta['page']
        retry_count = response.meta['retry_count']

        if response.status != 200:
            self.logger.warning(f'请求失败: {response.url}, 状态码: {response.status}')
            yield from self.handle_request_failure(response, retry_count)
            return

        try:
            # 使用response.text而不是response.body
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f'JSON解析失败: {response.url}, 错误: {e}')
            yield from self.handle_request_failure(response, retry_count)
            return

        if 'listItem' not in data:
            self.logger.warning(f'返回数据异常: {response.url}')
            return

        # 处理商品数据
        for item_data in data.get('listItem', []):
            item = MonitorPriceItem()

            # 新Item字段映射
            item_code = item_data.get('itemCode', '').strip()
            item_name = item_data.get('itemName', '').strip()
            
            item['product_code'] = item_code  # 产品唯一编号（对应原item_code）
            item['name'] = item_name  # 产品完整名称（对应原product_name）
            item['category'] = '手机'  # 产品分类（对应原item_kind）
            item['brand'] = brand_name  # 品牌名称（对应原brand_name）
            item['model'] = item_name  # 产品型号（对应原product_model）
            item['avg_price'] = item_data.get('averagePrice', '0').strip()  # 平均价格（对应原price）
            item['scrape_date'] = datetime.now().date()  # 爬取日期
            item['price_history'] = []  # 价格历史（初始为空列表）
            
            # 辅助字段（不直接存入数据库）
            item['crawl_time'] = datetime.now().isoformat()
            item['source_platform'] = '苏宁'  # 对应原item_platform
            item['page'] = current_page

            yield item

        # 翻页处理
        total_pages = int(data.get('totalPage', 1))
        if current_page < total_pages:
            yield from self.handle_pagination(response, data, brand_code, brand_name, current_page)

    def handle_pagination(self, response, data, brand_code, brand_name, current_page):
        total_pages = int(data.get('totalPage', 1))
        next_page = current_page + 1

        # 随机延迟
        delay = random.uniform(2, 5)
        time.sleep(delay)

        # 修复：URL格式化参数名
        next_url = self.base_url.format(page=next_page, brand=brand_code)

        # 修复：scrapy.Request而不是scrapy.request，get_headers而不是get_header
        yield scrapy.Request(
            next_url,
            callback=self.parse,
            headers=self.get_headers(),  # 修复方法名
            meta={
                'brand_code': brand_code,
                'brand_name': brand_name,
                'page': next_page,  # 修复：统一使用'page'
                'retry_count': 0
            },
            dont_filter=True
        )

    def handle_request_failure(self, response, retry_count):
        if retry_count < 3:
            self.logger.info(f'准备重试请求: {response.url}, 重试次数: {retry_count + 1}')
            delay = (retry_count + 1) * 10

            # 修复：scrapy.Request和方法名
            yield scrapy.Request(
                response.url,
                headers=self.get_headers(),  # 修复方法名
                callback=self.parse,
                meta={
                    'brand_code': response.meta['brand_code'],
                    'brand_name': response.meta['brand_name'],
                    'page': response.meta['page'],  # 修复：使用'page'
                    'retry_count': retry_count + 1
                },
                dont_filter=True
            )
        else:
            self.logger.error(f'请求超过最大次数: {response.url}')