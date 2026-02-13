from django.db import models
from django.utils import timezone


class RecycleProduct(models.Model):
    product_code = models.CharField('产品编号', max_length=50, unique=True)
    name = models.CharField('产品名称', max_length=100)
    category = models.CharField('产品类型', max_length=50)
    brand = models.CharField('产品品牌', max_length=50)
    model = models.CharField('产品型号', max_length=100)
    avg_price = models.DecimalField('平均回收价格', max_digits=10, decimal_places=2)
    scrape_date = models.DateField('爬取日期')
    price_history = models.JSONField('历史价格', default=list, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '回收产品'
        verbose_name_plural = '回收产品'
        indexes = [
            models.Index(fields=['category', 'brand', 'model']),
            models.Index(fields=['-scrape_date']),
        ]
        ordering = ['-scrape_date']

    def __str__(self):
        return f"{self.brand} {self.model}"


class Policy(models.Model):
    title = models.CharField('政策标题', max_length=200)
    content = models.TextField('政策内容', blank=True)
    attachment = models.FileField('政策文件', upload_to='policies/', blank=True, null=True)
    publish_date = models.DateField('发布日期', default=timezone.now)

    class Meta:
        verbose_name = '以旧换新政策'
        verbose_name_plural = '以旧换新政策'
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

