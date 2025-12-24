# -*- coding: utf-8 -*-

import requests
import json
import os
from config import API_BASE_URL, APP_ID

class UserService:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token_path = os.path.join(os.path.expanduser('~'), '.videosearch_user_token.json')
        self.user_info = None
        self.token = None
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
    
    def _save_token(self, token, user_info):
        """保存令牌到本地"""
        try:
            with open(self.token_path, 'w', encoding='utf-8') as f:
                json.dump({'token': token, 'user_info': user_info}, f)
            self.token = token
            self.user_info = user_info
        except Exception as e:
            print(f"保存令牌失败: {e}")
    
    def clear_token(self):
        """清除本地保存的令牌"""
        try:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
            self.token = None
            self.user_info = None
        except Exception as e:
            print(f"清除令牌失败: {e}")
    
    def login(self, username, password):
        """用户登录"""
        try:
            url = f"{self.base_url}/auth/login"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            token = result.get('access_token')
            
            if token :
                self.token = token
                result, user_info = self.get_user_info()
                if result:
                    self._save_token(token, user_info)
                    return True, user_info
                else:
                    return False, "获取用户信息失败"
            else:
                return False, "登录失败：无效的响应数据"
        
        except requests.exceptions.ConnectionError:
            return False, "连接失败：无法连接到用户服务"
        except requests.exceptions.Timeout:
            return False, "连接超时：用户服务响应超时"
        except requests.exceptions.HTTPError as e:
            try:
                # 尝试获取服务器返回的详细错误信息
                error_response = e.response.json()
                error_message = error_response.get('detail', f"登录失败：HTTP错误 {e.response.status_code}")
            except:
                # 如果无法解析JSON响应，使用默认错误信息
                if e.response.status_code == 401:
                    error_message = "用户名或密码错误"
                else:
                    error_message = f"登录失败：HTTP错误 {e.response.status_code}"
            return False, error_message
        except Exception as e:
            return False, f"登录失败：{str(e)}"
    
    def get_user_info(self):
        """获取用户信息"""
        # 如果已经有用户信息，直接返回
        if self.user_info:
            return True, self.user_info
        
        # 如果没有令牌，返回未登录
        if not self.token:
            return False, "未登录"
        
        try:
            url = f"{self.base_url}/users/me"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            user_info = result
            
            if user_info:
                self.user_info = user_info
                return True, user_info
            else:
                return False, "获取用户信息失败：无效的响应数据"
        
        except requests.exceptions.ConnectionError:
            return False, "连接失败：无法连接到用户服务"
        except requests.exceptions.Timeout:
            return False, "连接超时：用户服务响应超时"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # 令牌过期，清除本地令牌
                self.clear_token()
                return False, "登录已过期，请重新登录"
            else:
                return False, f"获取用户信息失败：HTTP错误 {e.response.status_code}"
        except Exception as e:
            return False, f"获取用户信息失败：{str(e)}"
    
    def check_in(self):
        """用户签到"""
        if not self.token:
            return False, "未登录"
        
        try:
            url = f"{self.base_url}/checkin/"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "app_id": APP_ID
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            points = result.get('points_earned', 0)
            consecutive_days = result.get('consecutive_days', 0)
            message = f"签到成功！获得{points}积分，连续签到{consecutive_days}天"
            
            # 更新用户信息
            if self.user_info:
                self.user_info['points'] = self.user_info.get('points', 0) + points
                # 保存更新后的用户信息
                self._save_token(self.token, self.user_info)
            
            return True, message
        
        except requests.exceptions.ConnectionError:
            return False, "连接失败：无法连接到用户服务"
        except requests.exceptions.Timeout:
            return False, "连接超时：用户服务响应超时"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.clear_token()
                return False, "登录已过期，请重新登录"
            elif e.response.status_code == 400:
                return False, "今日已签到"
            else:
                return False, f"签到失败：HTTP错误 {e.response.status_code}"
        except Exception as e:
            return False, f"签到失败：{str(e)}"
    
    def get_checkin_stats(self):
        """获取用户签到统计信息"""
        if not self.token:
            return False, "未登录"
        
        try:
            url = f"{self.base_url}/checkin/me/stats"
            params = {
                "app_id": APP_ID
            }
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            return True, result
        
        except requests.exceptions.ConnectionError:
            return False, "连接失败：无法连接到用户服务"
        except requests.exceptions.Timeout:
            return False, "连接超时：用户服务响应超时"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.clear_token()
                return False, "登录已过期，请重新登录"
            else:
                return False, f"获取签到统计失败：HTTP错误 {e.response.status_code}"
        except Exception as e:
            return False, f"获取签到统计失败：{str(e)}"
    
    def is_checked_in_today(self):
        """检查用户今天是否已经签到"""
        import datetime
        
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
    
    def save_login_state(self, token, user_info):
        """保存登录状态"""
        self.token = token
        self.user_info = user_info
        self._save_token(token, user_info)
    
    def clear_login_state(self):
        """清除登录状态"""
        self.clear_token()
    
    def register(self, username, password, email):
        """用户注册"""
        try:
            url = f"{self.base_url}/auth/register"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "username": username,
                "password": password,
                "email": email
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            
            if  "id" in result:
                return True, "注册成功"
            else:
                return False, result.get("detail", "注册失败：未知错误")
        
        except requests.exceptions.ConnectionError:
            return False, "连接失败：无法连接到用户服务"
        except requests.exceptions.Timeout:
            return False, "连接超时：用户服务响应超时"
        except requests.exceptions.HTTPError as e:
            try:
                # 尝试获取服务器返回的详细错误信息
                error_response = e.response.json()
                error_message = error_response.get('detail', f"注册失败：HTTP错误 {e.response.status_code}")
            except:
                # 如果无法解析JSON响应，使用默认错误信息
                error_message = f"注册失败：HTTP错误 {e.response.status_code}"
            return False, error_message
        except Exception as e:
            return False, f"注册失败：{str(e)}"
    
    def get_current_points(self):
        """获取当前用户的详细积分信息"""
        if not self.token:
            return False, "未登录"
        
        try:
            url = f"{self.base_url}/points/me"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            points_info = response.json()
            return True, points_info
        
        except requests.exceptions.ConnectionError:
            return False, "连接失败：无法连接到用户服务"
        except requests.exceptions.Timeout:
            return False, "连接超时：用户服务响应超时"
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.clear_token()
                return False, "登录已过期，请重新登录"
            else:
                return False, f"获取积分信息失败：HTTP错误 {e.response.status_code}"
        except Exception as e:
            return False, f"获取积分信息失败：{str(e)}"