# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MonitorPriceItem(scrapy.Item):
    """
    二手回收产品爬虫Item类
    对应数据库表: recycle_recycleproduct
    """
    
    # 必填字段（对应数据库表结构）
    product_code = scrapy.Field()      # VARCHAR(50) NOT NULL UNIQUE - 产品唯一编号
    name = scrapy.Field()              # VARCHAR(100) NOT NULL - 产品完整名称
    category = scrapy.Field()          # VARCHAR(50) NOT NULL - 产品分类（手机、电脑、平板电脑等）
    brand = scrapy.Field()             # VARCHAR(50) NOT NULL - 品牌名称
    model = scrapy.Field()             # VARCHAR(100) NOT NULL - 产品型号
    avg_price = scrapy.Field()         # DECIMAL(10,2) NOT NULL - 平均回收价格
    scrape_date = scrapy.Field()       # DATE NOT NULL - 数据爬取日期
    price_history = scrapy.Field()     # JSON DEFAULT NULL - 7天价格历史
    
    # 辅助字段（用于爬虫处理，不直接存入数据库）
    crawl_time = scrapy.Field()        # 爬取时间戳（用于转换为scrape_date）
    source_platform = scrapy.Field()   # 数据来源平台
    page = scrapy.Field()              # 数据所在页码
