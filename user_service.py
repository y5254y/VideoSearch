# -*- coding: utf-8 -*-

import requests
import json
import os
from config import API_BASE_URL, APP_ID
import datetime

class UserService:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token_path = os.path.join(os.path.expanduser('~'), '.videosearch_user_token.json')
        self.user_info = None
        self.token = None
        self.app_id = APP_ID
        # 加载保存的令牌
        self._load_token()
    
    def _load_token(self):
        """加载保存的令牌"""
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.user_info = data.get('user_info')
        except Exception as e:
            print(f"加载令牌失败: {e}")
    
    def _save_token(self, token, user_info=None):
        """保存令牌到本地"""
        try:
            # 如果没有提供user_info，使用现有用户信息
            if user_info is None:
                user_info = self.user_info
            
            with open(self.token_path, 'w', encoding='utf-8') as f:
                json.dump({'token': token, 'user_info': user_info}, f)
            
            self.token = token
            if user_info:
                self.user_info = user_info
        except Exception as e:
            print(f"保存令牌失败: {e}")
    
    def save_login_state(self, token, user_info):
        """保存登录状态"""
        self._save_token(token, user_info)

    def clear_token(self):
        """清除本地保存的令牌"""
        try:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
            self.token = None
            self.user_info = None
        except Exception as e:
            print(f"清除令牌失败: {e}")
    
    def _refresh_token(self):
        """刷新访问令牌"""
        if not self.token:
            return False
        
        try:
            # 调用刷新Token接口
            refresh_url = f"{self.base_url}/auth/refresh"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            response = requests.post(refresh_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # 刷新成功，保存新Token
                refresh_result = response.json()
                new_token = refresh_result.get("access_token")
                if new_token:
                    self.token = new_token
                    # 更新本地保存的Token
                    if self.user_info:
                        self._save_token(new_token, self.user_info)
                    else:
                        # 如果没有用户信息，只保存Token
                        self._save_token(new_token, None)
                    return True
        except Exception as e:
            print(f"刷新Token失败: {e}")
        
        return False
    
    def _request(self, endpoint, method='GET', data=None, headers=None, need_auth=True):
        """通用HTTP请求方法"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # 基础请求头
        request_headers = {
            "Content-Type": "application/json"
        }
        
        # 添加认证头
        if need_auth and self.token:
            request_headers["Authorization"] = f"Bearer {self.token}"
        
        # 合并自定义请求头
        if headers:
            request_headers.update(headers)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, params=data, timeout=5)
            elif method == 'POST':
                response = requests.post(url, headers=request_headers, json=data, timeout=5)
            else:
                return False, f"不支持的请求方法: {method}"
            
            response.raise_for_status()
            return True, response.json()
        
        except requests.exceptions.ConnectionError:
            return False, "连接失败：无法连接到用户服务"
        except requests.exceptions.Timeout:
            return False, "连接超时：用户服务响应超时"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # 令牌过期，尝试刷新令牌
                if self._refresh_token():
                    # 刷新成功，重新发送请求
                    return self._request(endpoint, method, data, headers, need_auth)
                else:
                    # 刷新失败，清除本地令牌
                    self.clear_token()
                    return False, "登录已过期，请重新登录"
            
            try:
                # 尝试获取服务器返回的详细错误信息
                error_response = e.response.json()
                error_message = error_response.get('detail', f"请求失败：HTTP错误 {e.response.status_code}")
            except:
                # 如果无法解析JSON响应，使用默认错误信息
                if e.response.status_code == 400:
                    error_message = "请求参数错误"
                else:
                    error_message = f"请求失败：HTTP错误 {e.response.status_code}"
            return False, error_message
        except Exception as e:
            return False, f"请求失败：{str(e)}"
    
   
    
    def login(self, username, password):
        """用户登录"""
        data = {
            "username": username,
            "password": password
        }
        
        success, result = self._request('/auth/login', method='POST', data=data, need_auth=False)
        
        if success:
            token = result.get('access_token')
            
            if token:
                self.token = token
                result, user_info = self.get_user_info()
                if result:
                    self._save_token(token, user_info)
                    return True, user_info
                else:
                    return False, "获取用户信息失败"
            else:
                return False, "登录失败：无效的响应数据"
        else:
            # 处理401错误，返回更友好的提示
            if "登录已过期" not in result and "HTTP错误 401" in result:
                return False, "用户名或密码错误"
            return False, result
    
    def get_user_info(self):
        """获取用户信息"""
        # 如果已经有用户信息，直接返回
        if self.user_info:
            return True, self.user_info
        
        # 如果没有令牌，返回未登录
        if not self.token:
            return False, "未登录"
        
        success, user_info = self._request('/users/me')
        
        if success and user_info:
            self.user_info = user_info
            return True, user_info
        elif not success:
            return False, user_info
        else:
            return False, "获取用户信息失败：无效的响应数据"
    
    def check_in(self):
        """用户签到"""
        if not self.token:
            return False, "未登录"
        
        data = {
            "app_id": self.app_id
        }
        
        success, result = self._request('/checkin/', method='POST', data=data)
        
        if success:
            points = result.get('points_earned', 0)
            consecutive_days = result.get('consecutive_days', 0)
            message = f"签到成功！获得{points}积分，连续签到{consecutive_days}天"
            
            # 更新用户信息
            if self.user_info:
                self.user_info['points'] = self.user_info.get('points', 0) + points
                # 保存更新后的用户信息
                self._save_token(self.token, self.user_info)
            
            return True, message
        else:
            # 特殊处理今日已签到的情况
            if "请求参数错误" in result:
                return False, "今日已签到"
            return False, result
    
    def get_checkin_stats(self):
        """获取用户签到统计信息"""
        if not self.token:
            return False, "未登录"
        
        data = {
            "app_id": self.app_id
        }
        
        return self._request('/checkin/me/stats', method='GET', data=data)
    
    def is_checked_in_today(self):
        """检查用户今天是否已经签到"""
        success, stats = self.get_checkin_stats()
        if not success:
            return False
        
        last_checkin_date = stats.get('last_checkin_date')
        if not last_checkin_date:
            return False
        
        # 获取今天的日期字符串（YYYY-MM-DD格式）
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # 比较最后签到日期和今天的日期
        return last_checkin_date == today
    
    def is_logged_in(self):
        """检查用户是否已登录"""
        if not self.token:
            return False
        
        # 验证令牌是否有效
        success, _ = self.get_user_info()
        return success
    
    def register(self, username, password, email):
        """用户注册"""
        data = {
            "username": username,
            "password": password,
            "email": email
        }
        
        success, result = self._request('/auth/register', method='POST', data=data, need_auth=False)
        
        if success:
            if "id" in result:
                return True, "注册成功"
            else:
                return False, result.get("detail", "注册失败：未知错误")
        else:
            return False, result
    
    def get_current_points(self):
        """获取当前用户的详细积分信息"""
        if not self.token:
            return False, "未登录"
        
        return self._request('/points/me')