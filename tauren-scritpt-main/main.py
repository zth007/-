
import time
import sys
import os
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from toutiao.toutiao import Toutiao, set_process_stats
from utils.config import config
from utils.logger import log_login_operation

running = True
process_stats = {
    "total_links": 0,
    "success_likes": 0,
    "failed_likes": 0,
    "failed_reasons": {}
}

tou_tiao = Toutiao("", "match_comment.text", "match_comment.text")
set_process_stats(process_stats)

web_status = None


def signal_handler(signal_num, frame):
    global running
    print("\n接收到中断信号，正在清理资源...")
    running = False
    try:
        driver = tou_tiao.get_driver()
        if driver:
            driver.quit()
            print("浏览器已关闭")
    except Exception as e:
        print(f"关闭浏览器失败: {e}")
    sys.exit(0)


def process_cycle():
    global process_stats
    operation_num = "1"
    
    print("=== 开始处理10个推荐内容 ===")
    try:
        tou_tiao.search_recommended(operation_num)
    except Exception as e:
        print(f"处理推荐列表失败: {e}")
        if "推荐列表" not in process_stats["failed_reasons"]:
            process_stats["failed_reasons"]["推荐列表"] = 0
        process_stats["failed_reasons"]["推荐列表"] += 1
    
    print("=== 开始处理10位关注者 ===")
    try:
        tou_tiao.search_account(operation_num)
    except Exception as e:
        print(f"处理关注列表失败: {e}")
        if "关注列表" not in process_stats["failed_reasons"]:
            process_stats["failed_reasons"]["关注列表"] = 0
        process_stats["failed_reasons"]["关注列表"] += 1


def auto_run(stop_event=None, status_dict=None):
    global running, process_stats, web_status
    
    running = True
    process_stats = {
        "total_links": 0,
        "success_likes": 0,
        "failed_likes": 0,
        "failed_reasons": {}
    }
    from toutiao.toutiao import set_process_stats
    set_process_stats(process_stats)
    
    if status_dict:
        web_status = status_dict
    
    def add_web_log(message, level="INFO"):
        if web_status and "logs" in web_status:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            web_status["logs"].insert(0, {
                "time": timestamp,
                "level": level,
                "message": message
            })
            if len(web_status["logs"]) > 100:
                web_status["logs"].pop()
    
    print("=== 今日头条自动化脚本 ===")
    add_web_log("=== 今日头条自动化脚本 ===")
    
    # 循环处理
    cycle_count = 0
    while True:
        # 每次循环都重新加载最新配置，实现实时生效
        config.reload()
        operation_config = config.get_operation_config()
        max_cycles = operation_config.get("cycle", {}).get("max_cycles", 5)
        cycle_interval = operation_config.get("cycle", {}).get("cycle_interval", 3600)
        
        cycle_count += 1
        add_web_log(f"=== 开始第 {cycle_count} 次循环 ===")
        
        if stop_event and stop_event.is_set():
            break
            
        if cycle_count > max_cycles:
            add_web_log(f"已达到最大循环次数 {max_cycles}，脚本结束")
            break
    
    if web_status:
        web_status["total_cycles"] = max_cycles
    
    print("1. 登录今日头条...")
    add_web_log("正在登录今日头条...")
    try:
        tou_tiao.login()
        log_login_operation(True, "登录成功")
        add_web_log("登录成功")
    except Exception as e:
        print(f"登录失败: {e}")
        add_web_log(f"登录失败: {e}", "ERROR")
        log_login_operation(False, f"登录失败: {str(e)}")
        return
    
    for i in range(max_cycles):
        if stop_event and stop_event.is_set():
            print("收到停止信号，正在退出...")
            add_web_log("收到停止信号，正在退出...")
            break
        if not running:
            break
        
        if web_status:
            web_status["current_cycle"] = i + 1
            web_status["stats"] = process_stats.copy()
        
        print(f"\n=== 第 {i+1} 次循环 ===")
        add_web_log(f"开始第 {i+1} 次循环")
        process_cycle()
        
        print("\n=== 刷新页面保持登录状态 ===")
        add_web_log("刷新页面保持登录状态")
        try:
            driver = tou_tiao.get_driver()
            if driver:
                driver.get('https://www.toutiao.com')
                time.sleep(3)
                print("页面已刷新")
        except Exception as e:
            print(f"刷新页面失败: {e}")
        
        if i < max_cycles - 1 and running:
            if stop_event and stop_event.is_set():
                break
            print(f"\n=== 等待 {cycle_interval//60} 分钟后开始下一次循环 ===")
            add_web_log(f"等待 {cycle_interval//60} 分钟后开始下一次循环")
            wait_time = 0
            while wait_time < cycle_interval:
                if (stop_event and stop_event.is_set()) or not running:
                    break
                time.sleep(10)
                wait_time += 10
    
    print("\n=== 自动化脚本执行完成 ===")
    add_web_log("自动化脚本执行完成")
    print(f"总处理链接数: {process_stats['total_links']}")
    print(f"成功点赞数: {process_stats['success_likes']}")
    print(f"失败点赞数: {process_stats['failed_likes']}")
    if process_stats['failed_reasons']:
        print("失败原因统计:")
        for reason, count in process_stats['failed_reasons'].items():
            print(f"  - {reason}: {count}次")
    
    if web_status:
        web_status["stats"] = process_stats.copy()
        web_status["running"] = False
    
    try:
        driver = tou_tiao.get_driver()
        if driver:
            driver.quit()
            print("浏览器已关闭")
            add_web_log("浏览器已关闭")
    except Exception as e:
        print(f"关闭浏览器失败: {e}")


def auto_run_wrapper(stop_event, status_dict):
    auto_run(stop_event, status_dict)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    auto_run()

