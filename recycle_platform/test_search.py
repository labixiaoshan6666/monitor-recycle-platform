#!/usr/bin/env python
"""
搜索功能测试脚本
用于验证回收产品和政策搜索功能是否正常工作
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db.models import Q
from recycle.models import RecycleProduct, Policy


def test_product_search():
    """测试产品搜索功能"""
    print("\n" + "="*60)
    print("测试回收产品搜索功能")
    print("="*60)
    
    test_cases = [
        ('iPhone', '搜索包含 iPhone 的产品'),
        ('Apple', '搜索 Apple 品牌产品'),
        ('手机', '搜索手机类型产品'),
        ('14', '搜索包含 14 的产品'),
        ('PHONE', '搜索产品编号包含 PHONE'),
        ('不存在的产品', '搜索不存在的产品'),
    ]
    
    for keyword, description in test_cases:
        print(f"\n【测试】{description}")
        print(f"关键词: '{keyword}'")
        
        # 执行搜索
        queryset = RecycleProduct.objects.filter(
            Q(name__icontains=keyword) | 
            Q(brand__icontains=keyword) | 
            Q(model__icontains=keyword) | 
            Q(category__icontains=keyword) |
            Q(product_code__icontains=keyword)
        )
        
        results = queryset.values('product_code', 'name', 'category', 'brand', 'model', 'avg_price')
        count = results.count()
        
        print(f"结果数量: {count}")
        
        if count > 0:
            print("匹配结果:")
            for i, product in enumerate(results[:5], 1):  # 只显示前5个
                print(f"  {i}. {product['brand']} {product['model']} - {product['category']} - ¥{product['avg_price']}")
            if count > 5:
                print(f"  ... 还有 {count - 5} 个结果")
        else:
            print("  ❌ 未找到匹配结果")
        
        print("-" * 60)


def test_policy_search():
    """测试政策搜索功能"""
    print("\n" + "="*60)
    print("测试政策搜索功能")
    print("="*60)
    
    test_cases = [
        ('补贴', '搜索包含补贴的政策'),
        ('2024', '搜索 2024 年政策'),
        ('标准', '搜索包含标准的政策'),
        ('家电', '搜索家电相关政策'),
        ('不存在的政策', '搜索不存在的政策'),
    ]
    
    for keyword, description in test_cases:
        print(f"\n【测试】{description}")
        print(f"关键词: '{keyword}'")
        
        # 执行搜索
        queryset = Policy.objects.filter(
            Q(title__icontains=keyword) | 
            Q(content__icontains=keyword)
        )
        
        results = queryset.values('id', 'title', 'publish_date')
        count = results.count()
        
        print(f"结果数量: {count}")
        
        if count > 0:
            print("匹配结果:")
            for i, policy in enumerate(results, 1):
                print(f"  {i}. {policy['title']} ({policy['publish_date']})")
        else:
            print("  ❌ 未找到匹配结果")
        
        print("-" * 60)


def test_empty_search():
    """测试空关键词搜索"""
    print("\n" + "="*60)
    print("测试空关键词搜索")
    print("="*60)
    
    print("\n【测试】空关键词产品搜索")
    products = RecycleProduct.objects.all().count()
    print(f"返回所有产品数量: {products}")
    
    print("\n【测试】空关键词政策搜索")
    policies = Policy.objects.all().count()
    print(f"返回所有政策数量: {policies}")
    
    print("-" * 60)


def print_database_stats():
    """打印数据库统计信息"""
    print("\n" + "="*60)
    print("数据库统计信息")
    print("="*60)
    
    product_count = RecycleProduct.objects.count()
    policy_count = Policy.objects.count()
    
    print(f"\n回收产品总数: {product_count}")
    print(f"政策总数: {policy_count}")
    
    if product_count > 0:
        print("\n产品分类统计:")
        categories = RecycleProduct.objects.values_list('category', flat=True).distinct()
        for category in categories:
            count = RecycleProduct.objects.filter(category=category).count()
            print(f"  - {category}: {count} 个产品")
    
    if policy_count > 0:
        print("\n政策列表:")
        policies = Policy.objects.all().values('id', 'title', 'publish_date')
        for policy in policies:
            print(f"  - {policy['title']} ({policy['publish_date']})")
    
    print("-" * 60)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("搜索功能测试开始")
    print("="*60)
    
    try:
        # 打印数据库统计
        print_database_stats()
        
        # 测试产品搜索
        test_product_search()
        
        # 测试政策搜索
        test_policy_search()
        
        # 测试空搜索
        test_empty_search()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
