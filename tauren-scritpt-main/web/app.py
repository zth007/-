import threading
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

script_status = {
    "running": False,
    "start_time": None,
    "current_cycle": 0,
    "total_cycles": 0,
    "stats": {
        "total_links": 0,
        "success_likes": 0,
        "failed_likes": 0,
        "failed_reasons": {}
    },
    "logs": []
}

script_thread = None
stop_event = threading.Event()


def add_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script_status["logs"].insert(0, {
        "time": timestamp,
        "level": level,
        "message": message
    })
    if len(script_status["logs"]) > 100:
        script_status["logs"].pop()


def run_script():
    try:
        from main import tou_tiao
        add_log("正在重置 Toutiao 实例...")
        tou_tiao.reset()
        
        from main import auto_run_wrapper
        auto_run_wrapper(stop_event, script_status)
    except Exception as e:
        add_log(f"脚本运行出错: {str(e)}", "ERROR")
        import traceback
        add_log(traceback.format_exc(), "ERROR")
    finally:
        script_status["running"] = False


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    return jsonify(script_status)


@app.route('/api/start', methods=['POST'])
def start_script():
    global script_thread, stop_event
    if script_status["running"]:
        return jsonify({"success": False, "message": "脚本已在运行中"})
    
    stop_event.clear()
    script_status["running"] = True
    script_status["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script_status["current_cycle"] = 0
    script_status["logs"] = []
    
    add_log("启动脚本...")
    
    script_thread = threading.Thread(target=run_script, daemon=True)
    script_thread.start()
    
    return jsonify({"success": True, "message": "脚本已启动"})


@app.route('/api/stop', methods=['POST'])
def stop_script():
    global stop_event
    if not script_status["running"]:
        return jsonify({"success": False, "message": "脚本未在运行"})
    
    add_log("正在停止脚本...")
    stop_event.set()
    script_status["running"] = False
    
    return jsonify({"success": True, "message": "停止信号已发送"})


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    from utils.config import config as app_config
    
    if request.method == 'GET':
        app_config.reload()
        return jsonify(app_config.config)
    else:
        data = request.json
        success = app_config.save_config(data)
        if success:
            app_config.reload()
            add_log("配置已更新，实时生效")
            return jsonify({"success": True, "message": "配置保存成功，已实时生效"})
        else:
            return jsonify({"success": False, "message": "配置保存失败"})

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    script_status["logs"] = []
    add_log("日志已清空")
    return jsonify({"success": True, "message": "日志已清空"})


@app.route('/api/accounts')
def get_accounts():
    from utils.account_manager import account_manager
    return jsonify(account_manager.get_status())


@app.route('/api/accounts', methods=['POST'])
def add_account():
    from utils.account_manager import account_manager
    data = request.json
    name = data.get('name', '新账号')
    cookie_file = data.get('cookie_file')
    account = account_manager.add_account(name, cookie_file)
    return jsonify({"success": True, "account_id": account.account_id})


@app.route('/api/accounts/<account_id>', methods=['PUT'])
def update_account(account_id):
    from utils.account_manager import account_manager
    data = request.json
    success = account_manager.update_account(account_id, **data)
    return jsonify({"success": success})


@app.route('/api/accounts/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    from utils.account_manager import account_manager
    success = account_manager.delete_account(account_id)
    return jsonify({"success": success})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
