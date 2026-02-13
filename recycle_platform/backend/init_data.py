"""
初始数据导入脚本 - 用于快速填充测试数据

使用方法:
  python backend/init_data.py

该脚本会在数据库中创建示例数据，用于演示平台功能。
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# 配置 Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from recycle.models import RecycleProduct, Policy

def init_products():
    """初始化回收产品数据"""
    products_data = [
        # 手机
        {
            'product_code': 'PHONE001',
            'name': 'Apple iPhone 14 Pro Max',
            'category': '手机',
            'brand': 'Apple',
            'model': 'iPhone 14 Pro Max',
            'avg_price': Decimal('5800.00'),
        },
        {
            'product_code': 'PHONE002',
            'name': 'Huawei Mate 50 Pro',
            'category': '手机',
            'brand': 'Huawei',
            'model': 'Mate 50 Pro',
            'avg_price': Decimal('3200.00'),
        },
        {
            'product_code': 'PHONE003',
            'name': 'Huawei Mate 40',
            'category': '手机',
            'brand': 'Huawei',
            'model': 'Mate 40',
            'avg_price': Decimal('2800.00'),
        },
        {
            'product_code': 'PHONE004',
            'name': 'Samsung Galaxy S23',
            'category': '手机',
            'brand': 'Samsung',
            'model': 'Galaxy S23',
            'avg_price': Decimal('4500.00'),
        },
        {
            'product_code': 'PHONE005',
            'name': 'Apple iPhone 13',
            'category': '手机',
            'brand': 'Apple',
            'model': 'iPhone 13',
            'avg_price': Decimal('4200.00'),
        },
        # 电脑
        {
            'product_code': 'PC001',
            'name': 'Apple MacBook Pro 16',
            'category': '电脑',
            'brand': 'Apple',
            'model': 'MacBook Pro 16',
            'avg_price': Decimal('8500.00'),
        },
        {
            'product_code': 'PC002',
            'name': 'Dell XPS 13',
            'category': '电脑',
            'brand': 'Dell',
            'model': 'XPS 13',
            'avg_price': Decimal('5200.00'),
        },
        {
            'product_code': 'PC003',
            'name': 'Lenovo ThinkPad X1 Carbon',
            'category': '电脑',
            'brand': 'Lenovo',
            'model': 'ThinkPad X1 Carbon',
            'avg_price': Decimal('4800.00'),
        },
        {
            'product_code': 'PC004',
            'name': 'HP EliteBook 840',
            'category': '电脑',
            'brand': 'HP',
            'model': 'EliteBook 840',
            'avg_price': Decimal('3800.00'),
        },
        {
            'product_code': 'PC005',
            'name': 'ASUS VivoBook 15',
            'category': '电脑',
            'brand': 'ASUS',
            'model': 'VivoBook 15',
            'avg_price': Decimal('3200.00'),
        },
        # 平板电脑
        {
            'product_code': 'TABLET001',
            'name': 'Apple iPad Pro 12.9',
            'category': '平板电脑',
            'brand': 'Apple',
            'model': 'iPad Pro 12.9',
            'avg_price': Decimal('4500.00'),
        },
        {
            'product_code': 'TABLET002',
            'name': 'Samsung Galaxy Tab S8',
            'category': '平板电脑',
            'brand': 'Samsung',
            'model': 'Galaxy Tab S8',
            'avg_price': Decimal('2800.00'),
        },
    ]

    today = datetime.now().date()
    count = 0

    for product_data in products_data:
        product_data['scrape_date'] = today
        # 生成示例价格历史数据
        history = []
        base_price = float(product_data['avg_price'])
        for i in range(7):
            day = today - timedelta(days=6 - i)
            # 模拟价格波动（±5%）
            fluctuation = (i - 3) * 100 / 500
            price = round(base_price * (0.98 + fluctuation), 2)
            history.append({
                'date': day.strftime('%Y-%m-%d'),
                'price': price
            })
        product_data['price_history'] = history

        product, created = RecycleProduct.objects.get_or_create(
            product_code=product_data['product_code'],
            defaults=product_data
        )
        if created:
            count += 1
            print(f"✓ 创建: {product.brand} {product.model}")
        else:
            print(f"- 已存在: {product.brand} {product.model}")

    print(f"\n✓ 已创建 {count} 个产品记录")


def init_policies():
    """初始化以旧换新政策数据"""
    policies_data = [
        {
            'title': '2024年全国以旧换新补贴政策',
            'content': '''根据国务院办公厅关于加快消费品以旧换新工作的通知精神，2024年全国推进消费品以旧换新工作。

主要政策内容：

1. 补贴标准
   - 手机：每台补贴200-500元
   - 电脑：每台补贴500-1500元
   - 平板电脑：每台补贴300-800元
   - 其他家电：根据具体情况补贴200-2000元

2. 申请条件
   - 旧产品需为本地注册用户
   - 旧产品使用至少6个月
   - 新产品需在指定门店购买
   - 旧产品需保修卡和发票凭证

3. 申请流程
   - 在指定门店咨询补贴资格
   - 提供身份证、发票等证明材料
   - 门店进行旧产品评估
   - 提交申请表单
   - 等待审核和补贴发放（一般3-7个工作日）

4. 温馨提示
   - 补贴政策会根据情况调整，请及时关注最新政策
   - 不同地区补贴标准可能有差异
   - 建议在购买前咨询当地门店

更多信息请访问官方网站或致电客服热线。''',
            'publish_date': datetime.now().date(),
        },
        {
            'title': '旧产品价格评估标准指南',
            'content': '''为了确保交易的公平公正，我们制定了详细的旧产品评估标准。

评估因素：

1. 产品新旧程度
   - 完好无损：100%价值
   - 轻微划痕：95%价值
   - 明显使用痕迹：85%价值
   - 屏幕有划痕：75%价值
   - 屏幕碎裂：50%价值

2. 功能完整性
   - 功能完整：满价
   - 存在故障：扣20-50%
   - 无法开机：30%价值

3. 配件完整性
   - 配置完整（含原装配件）：满价
   - 缺少部分配件：扣10-20%
   - 仅有产品本体：扣30%

4. 购买时间
   - 2年内购买：高价收购
   - 2-4年购买：正常价格
   - 4年以上：可能降价收购

评估流程：
1. 在线预评估：拍照或视频提交评估
2. 到店评估：由专业人员进行详细评估
3. 价格确认：确认评估价格并生成报价单
4. 交易完成：提交评估报告，完成交易

客服热线：4008-88-8888
营业时间：周一至周日 9:00-18:00''',
            'publish_date': (datetime.now() - timedelta(days=7)).date(),
        },
        {
            'title': '如何提高旧产品的回收价格',
            'content': '''想要获得更高的回收价格？以下建议可能对您有帮助：

1. 保持产品整洁
   - 定期清洁屏幕和机身
   - 使用保护套和膜
   - 避免进水和摔落

2. 妥善保管配件
   - 保留原装充电器和数据线
   - 保留原装包装盒
   - 保留发票和保修卡
   - 这些可能增加20-30%的价格

3. 定期维护
   - 及时清理系统垃圾
   - 定期更新系统
   - 及时修复小故障
   - 保持电池健康度

4. 及时交易
   - 新产品贬值快，及时回收可获得更高价格
   - 通常2-3年内交易价格较好
   - 避免产品过度老化

5. 了解市场行情
   - 关注我们的价格监控数据
   - 对比不同品牌和型号
   - 选择合适的交易时机

6. 准备相关证明
   - 准备产品购买证明
   - 保留维修记录（如有）
   - 这些可以提高评估师的信任

小贴士：
- 最好的交易时间是新产品发布后3-6个月
- 热销产品通常回收价格较好
- 经典款产品相对保值

需要更多帮助？欢迎咨询客服。''',
            'publish_date': (datetime.now() - timedelta(days=14)).date(),
        },
    ]

    count = 0
    for policy_data in policies_data:
        policy, created = Policy.objects.get_or_create(
            title=policy_data['title'],
            defaults=policy_data
        )
        if created:
            count += 1
            print(f"✓ 创建政策: {policy.title}")
        else:
            print(f"- 政策已存在: {policy.title}")

    print(f"\n✓ 已创建 {count} 个政策记录")


def main():
    print("\n=== 初始化回收产品平台数据 ===\n")

    try:
        print("正在初始化回收产品数据...")
        init_products()
        print("\n正在初始化政策数据...")
        init_policies()
        print("\n✓ 所有数据初始化完成！")
        print("\n现在您可以:")
        print("1. 访问前端: http://localhost:5173")
        print("2. 访问后台管理: http://localhost:8000/admin")
        print("3. 查看 API 数据: http://localhost:8000/api/types/")
    except Exception as e:
        print(f"\n✗ 出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
