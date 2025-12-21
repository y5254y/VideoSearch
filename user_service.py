# -*- coding: utf-8 -*-

import requests
import json
import os

class UserService:
    def __init__(self):
        self.base_url = "http://101.35.2.102:8000/api/v1"
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
            token = result.get('token')
            user_info = result.get('user')
            
            if token and user_info:
                self._save_token(token, user_info)
                return True, user_info
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
            url = f"{self.base_url}/user/info"
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            user_info = result.get('user')
            
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
            url = f"{self.base_url}/checkin"
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.post(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            message = result.get('message', '签到成功')
            points = result.get('points', 0)
            
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
    
    def is_logged_in(self):
        """检查用户是否已登录"""
        if not self.token:
            return False
        
        # 验证令牌是否有效
        success, _ = self.get_user_info()
        return success
    
    def register(self, username, password, email=None):
        """用户注册"""
        try:
            url = f"{self.base_url}/auth/register"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "username": username,
                "password": password
            }
            
            # 如果提供了邮箱，添加到请求数据中
            if email:
                data["email"] = email
            
            response = requests.post(url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success", False):
                return True, "注册成功"
            else:
                return False, result.get("message", "注册失败：未知错误")
        
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