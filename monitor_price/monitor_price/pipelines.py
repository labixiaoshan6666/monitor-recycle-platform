# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymysql
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from itemadapter import ItemAdapter
from twisted.enterprise import adbapi
from monitor_price import settings


class MonitorPricePipeline:
    """
    二手回收平台数据管道
    功能：数据清洗、格式转换、去重、存储到MySQL数据库
    数据库表：recycle_recycleproduct
    """
    
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.processed_codes = set()  # 用于当前会话的内存去重

    @classmethod
    def from_crawler(cls, crawler):
        """从爬虫配置创建连接池"""
        db_params = {
            'host': settings.MYSQL_HOST if hasattr(settings, 'MYSQL_HOST') else 'localhost',
            'port': settings.MYSQL_PORT if hasattr(settings, 'MYSQL_PORT') else 3306,
            'user': settings.MYSQL_USER if hasattr(settings, 'MYSQL_USER') else 'root',
            'password': settings.MYSQL_PASSWORD,
            'db': settings.MYSQL_DB,
            'charset': settings.MYSQL_CHARSET if hasattr(settings, 'MYSQL_CHARSET') else 'utf8mb4',
            'use_unicode': True,
            'cursorclass': pymysql.cursors.DictCursor
        }

        # 创建数据库连接池
        dbpool = adbapi.ConnectionPool('pymysql', **db_params)
        return cls(dbpool)

    def process_item(self, item, spider):
        """异步处理item"""
        try:
            # 数据清洗和验证
            cleaned_item = self._clean_item(item, spider)
            
            # 检查必填字段
            if not self._validate_item(cleaned_item, spider):
                spider.logger.warning(f"数据验证失败，跳过: {item}")
                return item
            
            # 内存去重检查
            product_code = cleaned_item.get('product_code')
            if product_code in self.processed_codes:
                spider.logger.info(f"重复数据（内存去重）: {product_code}")
                return item
            
            # 异步插入数据库
            query = self.dbpool.runInteraction(self._do_upsert, cleaned_item)
            query.addCallback(self._insert_success, cleaned_item, spider)
            query.addErrback(self._handle_error, cleaned_item, spider)
            
        except Exception as e:
            spider.logger.error(f"处理Item时发生异常: {e}, Item: {item}")
        
        return item

    def _clean_item(self, item, spider):
        """数据清洗和格式转换"""
        adapter = ItemAdapter(item)
        cleaned = {}
        
        # 1. product_code - 必填，唯一标识
        product_code = adapter.get('product_code', '').strip()
        if not product_code:
            # 如果没有提供，尝试自动生成
            category = adapter.get('category', '').strip()
            brand = adapter.get('brand', '').strip()
            model = adapter.get('model', '').strip()
            if category and brand and model:
                # 生成规则: CATEGORY_BRAND_MODEL (去除空格和特殊字符)
                product_code = f"{category}_{brand}_{model}".upper().replace(' ', '_')
                product_code = ''.join(c for c in product_code if c.isalnum() or c == '_')
        cleaned['product_code'] = product_code[:50]  # 限制长度
        
        # 2. name - 产品完整名称
        name = adapter.get('name', '').strip()
        if not name:
            # 尝试从brand和model组合
            brand = adapter.get('brand', '').strip()
            model = adapter.get('model', '').strip()
            name = f"{brand} {model}".strip()
        cleaned['name'] = name[:100]  # 限制长度
        
        # 3. category - 产品分类
        category = adapter.get('category', '').strip()
        cleaned['category'] = category[:50]
        
        # 4. brand - 品牌名称
        brand = adapter.get('brand', '').strip()
        cleaned['brand'] = brand[:50]
        
        # 5. model - 产品型号
        model = adapter.get('model', '').strip()
        cleaned['model'] = model[:100]
        
        # 6. avg_price - 平均价格（转换为Decimal，保留两位小数）
        avg_price = self._convert_to_decimal(adapter.get('avg_price'))
        if avg_price is None:
            # 尝试从price字段获取
            avg_price = self._convert_to_decimal(adapter.get('price'))
        cleaned['avg_price'] = avg_price
        
        # 7. scrape_date - 爬取日期（YYYY-MM-DD格式）
        scrape_date = self._convert_to_date(adapter.get('scrape_date'))
        if not scrape_date:
            # 尝试从crawl_time转换
            scrape_date = self._convert_to_date(adapter.get('crawl_time'))
        cleaned['scrape_date'] = scrape_date
        
        # 8. price_history - 价格历史（JSON格式）
        price_history = adapter.get('price_history')
        cleaned['price_history'] = self._format_price_history(price_history, avg_price, scrape_date)
        
        return cleaned

    def _validate_item(self, item, spider):
        """验证必填字段"""
        required_fields = ['product_code', 'name', 'category', 'brand', 'model', 'avg_price', 'scrape_date']
        
        for field in required_fields:
            value = item.get(field)
            if value is None or value == '':
                spider.logger.warning(f"缺少必填字段 '{field}': {item}")
                return False
        
        # 验证avg_price是否为有效数值
        if item.get('avg_price') is None or item.get('avg_price') <= 0:
            spider.logger.warning(f"avg_price无效: {item.get('avg_price')}")
            return False
        
        return True

    def _convert_to_decimal(self, value):
        """转换为Decimal类型（保留两位小数）"""
        if value is None or value == '':
            return None
        
        try:
            # 如果已经是Decimal类型
            if isinstance(value, Decimal):
                return value.quantize(Decimal('0.01'))
            
            # 移除货币符号和逗号
            if isinstance(value, str):
                value = value.replace('¥', '').replace('$', '').replace(',', '').strip()
            
            # 转换为Decimal
            decimal_value = Decimal(str(value))
            return decimal_value.quantize(Decimal('0.01'))
        
        except (InvalidOperation, ValueError, TypeError) as e:
            return None

    def _convert_to_date(self, value):
        """转换为日期格式（YYYY-MM-DD）"""
        if value is None or value == '':
            return date.today()
        
        # 如果已经是date类型
        if isinstance(value, date):
            return value
        
        # 如果是datetime类型
        if isinstance(value, datetime):
            return value.date()
        
        # 如果是字符串
        if isinstance(value, str):
            try:
                # 尝试解析ISO格式
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.date()
            except:
                try:
                    # 尝试解析常见格式
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']:
                        try:
                            return datetime.strptime(value, fmt).date()
                        except:
                            continue
                except:
                    pass
        
        # 如果是时间戳
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(value).date()
            except:
                pass
        
        # 默认返回今天
        return date.today()

    def _format_price_history(self, price_history, current_price, current_date):
        """格式化价格历史为JSON"""
        if price_history is None:
            # 如果没有历史数据，创建当天的记录
            if current_price and current_date:
                return json.dumps([{
                    'date': current_date.strftime('%Y-%m-%d'),
                    'price': float(current_price)
                }], ensure_ascii=False)
            return json.dumps([])
        
        # 如果已经是字符串（JSON）
        if isinstance(price_history, str):
            try:
                # 验证是否为有效JSON
                parsed = json.loads(price_history)
                if isinstance(parsed, list):
                    return price_history
            except:
                pass
        
        # 如果是列表或字典
        if isinstance(price_history, (list, dict)):
            try:
                return json.dumps(price_history, ensure_ascii=False)
            except:
                pass
        
        # 默认返回空列表
        return json.dumps([])

    def _do_upsert(self, tx, item):
        """
        执行数据库插入或更新操作
        逻辑：
        1. 先查询product_code是否存在
        2. 如果存在：获取历史price_history，追加新价格（保留最近7天）
        3. 如果不存在：插入新记录
        """
        product_code = item['product_code']
        current_price = float(item['avg_price'])
        current_date = item['scrape_date'].strftime('%Y-%m-%d')
        
        # 1. 查询是否存在该product_code
        select_sql = """
            SELECT price_history, avg_price, scrape_date
            FROM `recycle_recycleproduct`
            WHERE product_code = %s
        """
        tx.execute(select_sql, (product_code,))
        existing_record = tx.fetchone()
        
        if existing_record:
            # 2. 记录已存在，更新price_history
            new_price_history = self._update_price_history(
                existing_record['price_history'],
                current_price,
                current_date
            )
            
            # 更新现有记录
            update_sql = """
                UPDATE `recycle_recycleproduct`
                SET name = %s,
                    category = %s,
                    brand = %s,
                    model = %s,
                    avg_price = %s,
                    scrape_date = %s,
                    price_history = %s
                WHERE product_code = %s
            """
            
            tx.execute(update_sql, (
                item['name'],
                item['category'],
                item['brand'],
                item['model'],
                item['avg_price'],
                item['scrape_date'],
                new_price_history,
                product_code
            ))
            
            return ('updated', product_code)
        else:
            # 3. 记录不存在，插入新记录
            # 创建初始price_history（只包含当前价格）
            initial_price_history = json.dumps([{
                'date': current_date,
                'price': current_price
            }], ensure_ascii=False)
            
            insert_sql = """
                INSERT INTO `recycle_recycleproduct`
                (product_code, name, category, brand, model, avg_price, scrape_date, price_history, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            tx.execute(insert_sql, (
                product_code,
                item['name'],
                item['category'],
                item['brand'],
                item['model'],
                item['avg_price'],
                item['scrape_date'],
                initial_price_history
            ))
            
            return ('inserted', product_code)

    def _update_price_history(self, old_history_json, new_price, new_date):
        """
        更新价格历史，保留最近7天的数据
        参数：
            old_history_json: 旧的price_history JSON字符串
            new_price: 新价格（float）
            new_date: 新日期（YYYY-MM-DD字符串）
        返回：
            更新后的JSON字符串
        """
        # 解析现有历史数据
        try:
            if old_history_json:
                price_history = json.loads(old_history_json)
                if not isinstance(price_history, list):
                    price_history = []
            else:
                price_history = []
        except (json.JSONDecodeError, TypeError):
            price_history = []
        
        # 检查是否已经有今天的记录
        existing_dates = [entry.get('date') for entry in price_history]
        
        if new_date in existing_dates:
            # 如果今天已有记录，更新价格
            for entry in price_history:
                if entry.get('date') == new_date:
                    entry['price'] = new_price
                    break
        else:
            # 添加新记录
            price_history.append({
                'date': new_date,
                'price': new_price
            })
        
        # 按日期排序（最新的在后面）
        price_history.sort(key=lambda x: x.get('date', ''))
        
        # 保留最近7天的数据
        if len(price_history) > 7:
            price_history = price_history[-7:]  # 保留最后7条
        
        # 转换回JSON字符串
        return json.dumps(price_history, ensure_ascii=False)

    def _insert_success(self, result, item, spider):
        """插入成功回调"""
        operation, product_code = result
        self.processed_codes.add(product_code)
        
        if operation == 'inserted':
            spider.logger.info(f"✓ 新增产品: {product_code} - {item['name']}")
        else:  # updated
            spider.logger.info(f"✓ 更新产品: {product_code} - {item['name']}")

    def _handle_error(self, failure, item, spider):
        """处理数据库错误"""
        spider.logger.error(f"数据库操作失败: {failure}")
        spider.logger.error(f"失败的Item: {item}")

    def close_spider(self, spider):
        """爬虫关闭时的清理工作"""
        if hasattr(self, 'dbpool'):
            self.dbpool.close()
        
        spider.logger.info(f"数据库连接池已关闭")
        spider.logger.info(f"本次共处理 {len(self.processed_codes)} 条唯一数据")




