from datetime import timedelta

import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Policy, RecycleProduct


def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=False, json_dumps_params={'ensure_ascii': False})


def products_list(request):
    keyword = request.GET.get('keyword', '').strip()
    queryset = RecycleProduct.objects.all()
    
    # 模糊搜索：支持产品名称、品牌、型号、类型
    if keyword:
        queryset = queryset.filter(
            Q(name__icontains=keyword) | 
            Q(brand__icontains=keyword) | 
            Q(model__icontains=keyword) | 
            Q(category__icontains=keyword) |
            Q(product_code__icontains=keyword)
        )
    
    products = queryset.values(
        'id', 'product_code', 'name', 'category', 'brand', 'model', 'avg_price', 'scrape_date'
    )
    return json_response(list(products))


def types_list(request):
    types = RecycleProduct.objects.values_list('category', flat=True).distinct().order_by('category')
    return json_response(list(types))


def brands_list(request):
    category = request.GET.get('category')
    if not category:
        return json_response([])
    brands = RecycleProduct.objects.filter(category=category).values_list('brand', flat=True).distinct().order_by('brand')
    return json_response(list(brands))


def models_list(request):
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    if not category or not brand:
        return json_response([])
    models = RecycleProduct.objects.filter(category=category, brand=brand).values_list('model', flat=True).distinct().order_by('model')
    return json_response(list(models))


def price_trend(request):
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    if not all([category, brand, model]):
        return json_response({'detail': '缺少参数'}, status=400)

    product = RecycleProduct.objects.filter(category=category, brand=brand, model=model).first()
    if not product:
        return json_response({'detail': '未找到对应产品'}, status=404)

    # 获取价格历史数据
    history = product.price_history or []
    
    # 确保history是列表格式
    if not isinstance(history, list):
        history = []
    
    # 如果有历史数据，直接使用（有几天显示几天）
    if history:
        # 按日期排序，确保数据按时间顺序排列
        history_sorted = sorted(history, key=lambda x: x.get('date', ''))
        
        # 格式化数据，确保price是浮点数
        formatted_history = []
        for item in history_sorted:
            try:
                formatted_history.append({
                    'date': item.get('date', ''),
                    'price': float(item.get('price', 0))
                })
            except (ValueError, TypeError):
                continue
        
        history = formatted_history
    else:
        # 如果没有历史数据，生成模拟的7天数据
        base_date = product.scrape_date or timezone.now().date()
        base_price = float(product.avg_price)
        history = []
        for i in range(7):
            day = base_date - timedelta(days=6 - i)
            price = round(base_price * (0.96 + i * 0.01), 2)
            history.append({'date': day.strftime('%Y-%m-%d'), 'price': price})

    return json_response({
        'product': {
            'id': product.id,
            'product_code': product.product_code,
            'name': product.name,
            'category': product.category,
            'brand': product.brand,
            'model': product.model,
            'avg_price': float(product.avg_price),
            'scrape_date': product.scrape_date.strftime('%Y-%m-%d'),
        },
        'history': history,
    })


def policies_list(request):
    keyword = request.GET.get('keyword', '').strip()
    queryset = Policy.objects.all()
    if keyword:
        queryset = queryset.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))

    policies = []
    for policy in queryset:
        attachment_url = policy.attachment.url if policy.attachment else ''
        policies.append({
            'id': policy.id,
            'title': policy.title,
            'content': policy.content,
            'publish_date': policy.publish_date.strftime('%Y-%m-%d'),
            'attachment_url': attachment_url,
        })
    return json_response(policies)


def policy_detail(request, policy_id):
    policy = Policy.objects.filter(id=policy_id).first()
    if not policy:
        return json_response({'detail': '未找到政策'}, status=404)
    return json_response({
        'id': policy.id,
        'title': policy.title,
        'content': policy.content,
        'publish_date': policy.publish_date.strftime('%Y-%m-%d'),
        'attachment_url': policy.attachment.url if policy.attachment else '',
    })


@csrf_exempt
def ai_chat(request):
    """
    AI问答接口 - 集成DeepSeek API
    """
    if request.method != 'POST':
        return json_response({'detail': '只支持POST请求'}, status=405)
    
    import json
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return json_response({'detail': '请求格式错误'}, status=400)
    
    question = body.get('question', '').strip()
    history = body.get('history', [])
    
    if not question:
        return json_response({'detail': '问题不能为空'}, status=400)
    
    # 获取API密钥（从环境变量或数据库配置）
    api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
    
    if not api_key:
        return json_response({
            'detail': '未配置DeepSeek API密钥，请联系管理员在环境变量中设置DEEPSEEK_API_KEY'
        }, status=503)
    
    # 构建对话消息
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的以旧换新政策咨询助手。你的任务是帮助用户理解以旧换新政策，解答相关疑问。请提供准确、专业、易懂的回答。如果不确定，请提醒用户查看官方文件或咨询相关部门。"
        }
    ]
    
    # 添加历史对话（最多保留最近5轮）
    if history:
        recent_history = history[-10:]  # 最多10条消息（5轮对话）
        for msg in recent_history:
            if msg.get('role') in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
    
    # 添加当前问题
    messages.append({
        "role": "user",
        "content": question
    })
    
    # 调用DeepSeek API
    try:
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2000,
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', '未知错误')
            return json_response({
                'detail': f'DeepSeek API错误: {error_msg}'
            }, status=response.status_code)
        
        result = response.json()
        answer = result['choices'][0]['message']['content']
        
        return json_response({
            'answer': answer,
            'model': 'deepseek-chat'
        })
        
    except requests.Timeout:
        return json_response({'detail': 'API请求超时，请稍后重试'}, status=504)
    except requests.RequestException as e:
        return json_response({'detail': f'网络请求失败: {str(e)}'}, status=503)
    except Exception as e:
        return json_response({'detail': f'处理请求时发生错误: {str(e)}'}, status=500)


