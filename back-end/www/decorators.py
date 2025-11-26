from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import threading


# 存储IP访问记录的字典
# 格式: {ip: {'attempts': count, 'first_attempt': datetime, 'blocked_until': datetime}}
ip_attempts = defaultdict(lambda: {'attempts': 0, 'first_attempt': None, 'blocked_until': None})
# 线程锁，确保并发安全
ip_lock = threading.Lock()


def rate_limit(max_attempts=5, time_window=60):
    """
    限流装饰器
    :param max_attempts: 时间窗口内最大尝试次数
    :param time_window: 时间窗口（秒）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取客户端IP
            if request.headers.get('X-Forwarded-For'):
                client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
            else:
                client_ip = request.remote_addr

            current_time = datetime.now()

            with ip_lock:
                ip_data = ip_attempts[client_ip]

                # 检查是否在封禁期内
                if ip_data['blocked_until'] and current_time < ip_data['blocked_until']:
                    remaining_seconds = int((ip_data['blocked_until'] - current_time).total_seconds())
                    return jsonify({
                        'status': '2',
                        'message': f'请求过于频繁，请在 {remaining_seconds} 秒后重试'
                    }), 429

                # 如果是新的时间窗口或首次访问，重置计数
                if (ip_data['first_attempt'] is None or 
                    current_time - ip_data['first_attempt'] > timedelta(seconds=time_window)):
                    ip_data['attempts'] = 1
                    ip_data['first_attempt'] = current_time
                    ip_data['blocked_until'] = None
                else:
                    # 在时间窗口内，增加计数
                    ip_data['attempts'] += 1

                # 检查是否超过限制
                if ip_data['attempts'] > max_attempts:
                    # 计算剩余封禁时间
                    time_passed = (current_time - ip_data['first_attempt']).total_seconds()
                    remaining_time = time_window - time_passed
                    ip_data['blocked_until'] = current_time + timedelta(seconds=remaining_time)
                    
                    return jsonify({
                        'status': '2',
                        'message': f'登录尝试次数过多，请在 {int(remaining_time)} 秒后重试'
                    }), 429

            # 继续执行原函数
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def clear_expired_records():
    """
    清理过期的IP记录（可选的后台任务）
    """
    current_time = datetime.now()
    with ip_lock:
        expired_ips = []
        for ip, data in ip_attempts.items():
            if (data['blocked_until'] and current_time > data['blocked_until'] and
                data['first_attempt'] and current_time - data['first_attempt'] > timedelta(minutes=10)):
                expired_ips.append(ip)
        
        for ip in expired_ips:
            del ip_attempts[ip]
