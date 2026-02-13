#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
二手回收价格爬虫定时任务脚本
功能：每天自动运行两个爬虫（suning_phone 和 suning_computer）
作者：Your Name
日期：2026-02-13
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f'crawl_{datetime.now().strftime("%Y%m%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_spider(spider_name):
    """
    运行单个爬虫
    
    Args:
        spider_name: 爬虫名称（suning_phone 或 suning_computer）
    
    Returns:
        bool: 是否运行成功
    """
    logger.info(f"{'='*60}")
    logger.info(f"开始运行爬虫: {spider_name}")
    logger.info(f"{'='*60}")
    
    try:
        # 获取项目根目录
        project_dir = Path(__file__).parent
        
        # 构建命令
        cmd = ['scrapy', 'crawl', spider_name]
        
        # 运行爬虫
        process = subprocess.Popen(
            cmd,
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # 实时输出日志
        for line in process.stdout:
            logger.info(line.rstrip())
        
        # 等待进程结束
        return_code = process.wait()
        
        if return_code == 0:
            logger.info(f"✓ 爬虫 {spider_name} 运行成功")
            return True
        else:
            # 输出错误信息
            stderr = process.stderr.read()
            logger.error(f"✗ 爬虫 {spider_name} 运行失败，返回码: {return_code}")
            logger.error(f"错误信息: {stderr}")
            return False
            
    except FileNotFoundError:
        logger.error(f"✗ 未找到 scrapy 命令，请确保已安装 Scrapy")
        logger.error(f"  安装命令: pip install scrapy")
        return False
    except Exception as e:
        logger.error(f"✗ 运行爬虫 {spider_name} 时发生异常: {e}")
        return False


def main():
    """主函数：按顺序运行所有爬虫"""
    start_time = datetime.now()
    logger.info(f"\n{'#'*60}")
    logger.info(f"# 二手回收价格爬虫定时任务")
    logger.info(f"# 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'#'*60}\n")
    
    # 要运行的爬虫列表
    spiders = ['suning_phone', 'suning_computer']
    
    results = {}
    
    # 依次运行每个爬虫
    for spider in spiders:
        success = run_spider(spider)
        results[spider] = success
        
        # 爬虫之间间隔10秒
        if spider != spiders[-1]:
            logger.info(f"\n等待10秒后运行下一个爬虫...\n")
            import time
            time.sleep(10)
    
    # 统计结果
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    success_count = sum(1 for v in results.values() if v)
    fail_count = len(results) - success_count
    
    logger.info(f"\n{'#'*60}")
    logger.info(f"# 任务执行完成")
    logger.info(f"# 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"# 耗时: {duration:.2f} 秒")
    logger.info(f"# 成功: {success_count} 个，失败: {fail_count} 个")
    logger.info(f"{'#'*60}\n")
    
    # 输出详细结果
    logger.info("详细结果:")
    for spider, success in results.items():
        status = "✓ 成功" if success else "✗ 失败"
        logger.info(f"  {spider}: {status}")
    
    # 返回退出码（0表示全部成功，1表示有失败）
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
