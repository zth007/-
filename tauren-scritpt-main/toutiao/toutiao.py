import time
import random
import pickle
import os

from helium import *
from helium import get_driver
from selenium.webdriver.common.by import By

from load.load import Load as file_load
from operation.operation_toutiao import Operation
from utils.logger import log_login_operation, log_follow_operation, log_recommend_operation

# 全局统计变量 - 从 main.py 共享
process_stats = None


def set_process_stats(stats):
    global process_stats
    process_stats = stats

"""
 1. 用户内容针对性点赞
 2. 文章/视频点赞
"""


class Toutiao:
    _instance = None
    _driver = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Toutiao, cls).__new__(cls)
        return cls._instance

    def __init__(self, target_file_name, match_content_file_name, match_comment_file_name):
        if not hasattr(self, '_initialized'):
            self._init_data(target_file_name, match_content_file_name, match_comment_file_name)
            self._initialized = True
    
    def _init_data(self, target_file_name, match_content_file_name, match_comment_file_name):
        self.is_login = False
        self.operate = Operation()
        if target_file_name:
            self.link_items = file_load.load(target_file_name)
        else:
            self.link_items = []
        self.match_content_items = file_load.load(match_content_file_name)
        self.match_comment_item_map = file_load.load_map(match_comment_file_name)
        self.cookie_file = "toutiao_cookies.pkl"
        self.processed_users = set()
        self.all_followed_users = []
    
    def reset(self, target_file_name="", match_content_file_name="match_content.text", match_comment_file_name="match_comment.text"):
        """重置 Toutiao 实例，用于多次运行"""
        try:
            driver = self.get_driver()
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        except:
            pass
        
        Toutiao._driver = None
        self._init_data(target_file_name, match_content_file_name, match_comment_file_name)

    def login(self):
        """登录今日头条"""
        driver = self._initialize_driver()
        cookie_loaded = self._load_cookies(driver)
        
        # 如果加载了cookie，直接检查登录状态
        if cookie_loaded:
            print("检查cookie登录状态...")
        
        # 检查是否已登录
        login_success = self._check_login_status(driver)
        
        # 如果未登录，执行登录流程
        if not login_success:
            login_success = self._perform_login(driver)
            if login_success:
                self._save_cookies(driver)
        
        self.is_login = True
        print("登录成功")
        log_login_operation(True, "登录成功")
        
        # 随机延迟，避免被风控
        time.sleep(random.uniform(2, 4))
    
    def _initialize_driver(self):
        """初始化浏览器驱动"""
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        from helium import set_driver
        from utils.config import config
        
        # 检查是否已有driver实例
        if Toutiao._driver is None:
            # 配置Edge浏览器选项
            edge_options = Options()
            
            # 从配置读取浏览器设置
            headless = config.get("operation.browser.headless", False)
            maximize = config.get("operation.browser.maximize", True)
            
            if headless:
                edge_options.add_argument("--headless")
            if maximize:
                edge_options.add_argument("--start-maximized")
            
            # 启动Edge浏览器
            driver = webdriver.Edge(options=edge_options)
            driver.get('https://www.toutiao.com')
            
            # 将driver传递给Helium
            set_driver(driver)
            Toutiao._driver = driver
        else:
            driver = Toutiao._driver
            # 确保在首页
            driver.get('https://www.toutiao.com')
            time.sleep(5)
            print("使用现有driver实例")
        
        return driver
    
    def _load_cookies(self, driver):
        """加载cookie"""
        cookie_loaded = False
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'rb') as f:
                    cookies = pickle.load(f)
                    print(f"加载 {len(cookies)} 个cookie")
                    for cookie in cookies:
                        try:
                            driver.add_cookie(cookie)
                        except Exception as e:
                            print(f"添加cookie失败: {e}")
                # 重新加载页面
                driver.get('https://www.toutiao.com')
                time.sleep(5)
                cookie_loaded = True
                print("Cookie加载成功")
            except Exception as e:
                print(f"加载cookie失败: {e}")
        return cookie_loaded
    
    def _check_login_status(self, driver):
        """检查登录状态"""
        login_success = False
        # 增加等待时间，确保页面完全加载
        time.sleep(10)
        try:
            # 打印当前页面标题，用于调试
            print(f"当前页面标题: {driver.title}")
            print(f"当前页面URL: {driver.current_url}")
            
            # 打印页面上的所有cookie，用于调试
            cookies = driver.get_cookies()
            print(f"当前页面cookie数量: {len(cookies)}")
            for cookie in cookies:
                if "token" in cookie["name"] or "user" in cookie["name"] or "login" in cookie["name"]:
                    print(f"找到登录相关cookie: {cookie['name']}")
            
            # 首先检查是否存在登录按钮，如果存在，则说明未登录
            print("检查是否存在登录按钮...")
            if Button('登录').exists():
                print("检测到登录按钮，未登录")
            elif Text('登录').exists():
                print("检测到登录文本，未登录")
            elif S("//button[contains(text(), '登录')]").exists():
                print("检测到登录按钮，未登录")
            else:
                # 尝试获取页面源代码，检查是否包含登录成功后的特征
                page_source = driver.page_source
                print("检查页面源代码中的登录特征...")
                
                # 检查是否包含登录成功后的特征
                login_indicators = ["个人中心", "退出登录", "我的主页", "欢迎回来"]
                login_found = False
                for indicator in login_indicators:
                    if indicator in page_source:
                        print(f"检测到登录特征: {indicator}")
                        login_found = True
                        break
                
                # 检查是否存在用户头像
                if not login_found and S("//div[@class='user-avatar']").exists():
                    print("检测到用户头像，已登录")
                    login_found = True
                
                # 检查是否存在用户名
                if not login_found and S("//span[@class='user-name']").exists():
                    print("检测到用户名，已登录")
                    login_found = True
                
                login_success = login_found
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            # 如果检查失败，默认认为未登录
            login_success = False
        return login_success
    
    def _perform_login(self, driver):
        """执行登录流程"""
        # 等待登录按钮出现
        time.sleep(3)
        # 点击登录按钮（今日头条登录入口通常在右上角）
        try:
            if Button('登录').exists():
                click('登录')
            elif Text('登录').exists():
                click(Text('登录'))
            elif S("//button[contains(text(), '登录')]").exists():
                click(S("//button[contains(text(), '登录')]"))
        except Exception as e:
            print(f"登录按钮点击失败: {e}")
        
        # 等待登录完成
        time.sleep(10)
        # 检查是否登录成功
        while True:
            # 尝试找到用户相关元素
            login_success = self._check_login_status(driver)
            
            if login_success:
                break
            else:
                print("请扫码或输入账号密码登录...")
                time.sleep(5)
        
        return login_success
    
    def _save_cookies(self, driver):
        """保存cookie"""
        try:
            cookies = driver.get_cookies()
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            print("Cookie保存成功")
        except Exception as e:
            print(f"保存cookie失败: {e}")
    
    def get_driver(self):
        """获取当前的浏览器驱动"""
        from helium import get_driver
        if Toutiao._driver is None:
            return get_driver()
        return Toutiao._driver

    def get_followed_content(self):
        """从个人主页获取关注用户的主页链接"""
        try:
            driver = get_driver()
            
            # 导航到个人主页
            self._navigate_to_profile(driver)
            
            # 查找并点击关注数，进入关注列表
            follow_list_found = self._navigate_to_follow_list(driver)
            
            if not follow_list_found:
                print("未找到关注数，返回空列表")
                return []
            
            # 滚动加载更多关注用户
            self._scroll_to_load_more(driver, 5)
            
            # 提取关注用户的主页链接
            user_links = self._extract_user_links(driver)
            
            # 去重并限制数量为20个
            user_links = list(set(user_links))[:20]
            print(f"获取到 {len(user_links)} 个关注用户链接")
            return user_links
        except Exception as e:
            print(f"获取关注用户失败: {e}")
            return []
    
    def _navigate_to_profile(self, driver):
        """导航到个人主页"""
        print("导航到个人主页...")
        # 使用用户提供的个人主页URL
        user_profile_url = 'https://www.toutiao.com/c/user/token/Civnj1EumV1Q5xqB7CaEAirJhMQqwTJFiM7yo80tcwLp9jyQ7naWplSiW0e5GkkKPAAAAAAAAAAAAABQJk1hnETc2hiVXM6ouya5YLFCzfl9GHsElL_VwC90UdIWZyMf_Wnv0jiwckIZHBBIGxC-rosOGMPFg-oEIgEDlm1y5Q==/?source=list&log_from=85125f6838cbf_1772784129339'
        driver.get(user_profile_url)
        time.sleep(5)
        
        # 打印当前页面标题和URL，用于调试
        print(f"当前页面标题: {driver.title}")
        print(f"当前页面URL: {driver.current_url}")
    
    def _navigate_to_follow_list(self, driver):
        """导航到关注列表"""
        print("查找并点击关注数...")
        follow_list_found = False
        try:
            # 尝试不同的关注数定位方式
            follow_elements = [
                S("//a[contains(text(), '关注')]"),
                S("//span[contains(text(), '关注')]"),
                S("//div[contains(text(), '关注')]"),
                S("//span[contains(@class, 'follow')]")
            ]
            
            for element in follow_elements:
                if element.exists():
                    print("找到关注数")
                    click(element)
                    time.sleep(5)
                    follow_list_found = True
                    break
        except Exception as e:
            print(f"点击关注数失败: {e}")
        
        if not follow_list_found:
            print("未找到关注数，尝试直接访问关注列表")
            # 尝试直接访问关注列表
            try:
                # 从当前URL构建关注列表URL
                current_url = driver.current_url
                if 'c/user/token/' in current_url:
                    # 提取用户token
                    import re
                    token_match = re.search(r'c/user/token/([^/?]+)', current_url)
                    if token_match:
                        token = token_match.group(1)
                        follow_list_url = f'https://www.toutiao.com/c/user/token/{token}/follow/?source=list'
                        print(f"尝试直接访问关注列表: {follow_list_url}")
                        driver.get(follow_list_url)
                        time.sleep(5)
                        follow_list_found = True
                        print("成功访问关注列表")
            except Exception as e:
                print(f"直接访问关注列表失败: {e}")
        
        return follow_list_found
    
    def _scroll_to_load_more(self, driver, scroll_times):
        """滚动加载更多内容"""
        print("开始滚动加载关注用户...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(scroll_times):  # 滚动指定次数，确保加载足够的内容
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("滚动到底部，停止滚动")
                break
            last_height = new_height
            print(f"第 {i+1} 次滚动完成")
    
    def _extract_user_links(self, driver):
        """提取用户链接，排除自己的链接"""
        user_links = []
        print("开始提取关注用户链接...")
        
        # 获取当前页面URL，用于排除自己的链接
        current_url = driver.current_url
        import re
        # 提取自己的token或用户名用于比较
        self_token = None
        self_username = None
        
        if 'c/user/token/' in current_url:
            token_match = re.search(r'c/user/token/([^/?]+)', current_url)
            if token_match:
                self_token = token_match.group(1)
        elif 'toutiao.com/@' in current_url:
            username_match = re.search(r'toutiao\.com/@([^/?]+)', current_url)
            if username_match:
                self_username = username_match.group(1)
        
        print(f"自己的token: {self_token}, 自己的用户名: {self_username}")
        
        # 尝试不同的元素定位器
        try:
            # 方法1: 查找用户头像链接
            print("尝试方法1: 查找用户头像链接")
            user_elements = find_all(S("//a[contains(@href, 'toutiao.com/@')]"))
            print(f"找到 {len(user_elements)} 个用户链接")
            for element in user_elements:
                try:
                    link = element.web_element.get_attribute('href')
                    if link and 'toutiao.com/@' in link:
                        # 排除自己的链接
                        if self_username and f'toutiao.com/@{self_username}' in link:
                            continue
                        user_links.append(link)
                        print(f"找到用户链接: {link}")
                except:
                    pass
        except Exception as e:
            print(f"方法1失败: {e}")
        
        try:
            # 方法2: 从页面源代码中提取用户链接
            print("尝试方法2: 从页面源代码中提取用户链接")
            page_source = driver.page_source
            # 正则表达式匹配用户链接
            user_link_pattern = r'https?://www\.toutiao\.com/(?:@[^"\'\s]+|c/user/token/[^"\'\s/?]+)'
            matches = re.findall(user_link_pattern, page_source)
            print(f"找到 {len(matches)} 个用户链接")
            for link in matches:
                if link not in user_links:
                    # 排除自己的链接
                    exclude = False
                    if self_token and f'c/user/token/{self_token}' in link:
                        exclude = True
                    if self_username and f'toutiao.com/@{self_username}' in link:
                        exclude = True
                    if not exclude:
                        user_links.append(link)
                        print(f"找到用户链接: {link}")
        except Exception as e:
            print(f"方法2失败: {e}")
        
        try:
            # 方法3: 查找带有用户信息的div下的链接
            print("尝试方法3: 查找带有用户信息的div下的链接")
            user_containers = find_all(S("//div[contains(@class, 'user-item')]"))
            print(f"找到 {len(user_containers)} 个用户容器")
            for container in user_containers:
                try:
                    a_element = container.web_element.find_element(By.TAG_NAME, 'a')
                    link = a_element.get_attribute('href')
                    if link and ('toutiao.com/@' in link or 'toutiao.com/c/user/' in link):
                        # 排除自己的链接
                        exclude = False
                        if self_token and f'c/user/token/{self_token}' in link:
                            exclude = True
                        if self_username and f'toutiao.com/@{self_username}' in link:
                            exclude = True
                        if not exclude:
                            user_links.append(link)
                            print(f"找到用户链接: {link}")
                except:
                    pass
        except Exception as e:
            print(f"方法3失败: {e}")
        
        try:
            # 方法4: 查找所有包含用户链接的a标签
            print("尝试方法4: 查找所有包含用户链接的a标签")
            all_a_elements = find_all(S("//a"))
            print(f"找到 {len(all_a_elements)} 个a标签")
            for element in all_a_elements:
                try:
                    link = element.web_element.get_attribute('href')
                    if link and ('toutiao.com/@' in link or 'toutiao.com/c/user/' in link):
                        # 排除自己的链接
                        exclude = False
                        if self_token and f'c/user/token/{self_token}' in link:
                            exclude = True
                        if self_username and f'toutiao.com/@{self_username}' in link:
                            exclude = True
                        if not exclude and link not in user_links:
                            user_links.append(link)
                            print(f"找到用户链接: {link}")
                except:
                    pass
        except Exception as e:
            print(f"方法4失败: {e}")
        
        return user_links
    
    def get_recommended_content(self):
        """获取首页推荐列表的内容链接"""
        try:
            driver = get_driver()
            
            # 确保在首页
            driver.get('https://www.toutiao.com')
            time.sleep(5)
            
            # 打印当前页面标题和URL，用于调试
            print(f"当前页面标题: {driver.title}")
            print(f"当前页面URL: {driver.current_url}")
            
            # 滚动加载更多推荐内容
            print("开始滚动加载推荐内容...")
            last_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(3):  # 滚动3次
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("滚动到底部，停止滚动")
                    break
                last_height = new_height
                print(f"第 {i+1} 次滚动完成")
            
            # 提取推荐内容链接
            content_links = []
            print("开始提取推荐内容链接...")
            
            # 尝试不同的元素定位器
            try:
                # 方法1: 查找推荐列表中的内容链接
                print("尝试方法1: 查找推荐列表中的内容链接")
                # 查找所有可能的内容链接
                content_elements = find_all(S("//a"))
                print(f"找到 {len(content_elements)} 个链接元素")
                for element in content_elements:
                    link = element.web_element.get_attribute('href')
                    if link and ('toutiao.com/article/' in link or 'toutiao.com/video/' in link):
                        content_links.append(link)
                        print(f"找到内容链接: {link}")
            except Exception as e:
                print(f"方法1失败: {e}")
            
            try:
                # 方法2: 查找带有标题的div下的链接
                print("尝试方法2: 查找带有标题的div下的链接")
                title_divs = find_all(S("//div[contains(@class, 'title')]"))
                print(f"找到 {len(title_divs)} 个标题元素")
                for div in title_divs:
                    try:
                        parent_a = div.web_element.find_element(By.XPATH, "ancestor::a")
                        link = parent_a.get_attribute('href')
                        if link and ('toutiao.com/article/' in link or 'toutiao.com/video/' in link):
                            content_links.append(link)
                            print(f"找到内容链接: {link}")
                    except:
                        pass
            except Exception as e:
                print(f"方法2失败: {e}")
            
            # 去重并限制数量为20个
            content_links = list(set(content_links))[:20]
            print(f"获取到 {len(content_links)} 个推荐内容链接")
            return content_links
        except Exception as e:
            print(f"获取推荐内容失败: {e}")
            return []



    def process_content(self, links, operation_num):
        """处理链接，对内容进行点赞"""
        from selenium.common.exceptions import NoSuchWindowException, WebDriverException, TimeoutException
        from utils.logger import log_like_operation
        
        # 导入全局统计变量
        global process_stats
        
        driver = self.get_driver()
        success_count = 0
        total_count = len(links)
        
        for link in links:
            try:
                # 检查链接类型
                if 'toutiao.com/@' in link or 'toutiao.com/c/user/token/' in link:
                    print(f"正在处理用户主页: {link}")
                    # 处理用户主页链接
                    result = self._process_user_page(link, driver, driver.current_window_handle, log_like_operation)
                    success_count += result
                else:
                    print(f"正在处理内容链接: {link}")
                    # 处理内容链接
                    result = self._process_content_link(link, driver, driver.current_window_handle, log_like_operation)
                    success_count += result
            except NoSuchWindowException as e:
                print(f"窗口已关闭: {e}")
                log_like_operation(link, False, f"窗口已关闭: {str(e)}")
                # 重新获取driver
                try:
                    driver = self.get_driver()
                    if not driver:
                        # 如果没有driver，重新登录
                        print("没有可用driver，尝试重新登录...")
                        self.login()
                        driver = self.get_driver()
                except Exception as login_e:
                    print(f"重新获取driver失败: {login_e}")
            except WebDriverException as e:
                print(f"WebDriver错误: {e}")
                log_like_operation(link, False, f"WebDriver错误: {str(e)}")
                # 尝试重新登录
                try:
                    print("尝试重新登录...")
                    self.login()
                    driver = self.get_driver()
                except Exception:
                    pass
            except TimeoutException as e:
                print(f"操作超时: {e}")
                log_like_operation(link, False, f"操作超时: {str(e)}")
            except Exception as e:
                print(f"处理链接 {link} 失败: {e}")
                log_like_operation(link, False, f"处理失败: {str(e)}")
        
        # 记录最终结果
        if operation_num == "1":
            log_follow_operation(total_count, success_count)
        else:
            log_recommend_operation(total_count, success_count)
    

    
    def _process_user_page(self, link, driver, original_window, log_like_operation):
        """处理用户主页，返回成功点赞数量 - 只点赞前5个视频"""
        from selenium.common.exceptions import NoSuchWindowException, WebDriverException
        global process_stats
        
        page_success_count = 0
        
        try:
            # 直接在当前窗口导航到用户主页
            driver.get(link)
            time.sleep(random.uniform(2, 4))
            
            page_title = driver.title
            print(f"当前用户主页: {page_title}")
            print(f"当前URL: {driver.current_url}")
            
            # 尝试在当前页面直接找视频链接（不切换标签页）
            video_links = []
            print("在当前页面查找视频链接...")
            
            # 多次尝试查找视频链接
            for attempt in range(3):
                try:
                    # 滚动一下页面加载内容
                    if attempt > 0:
                        driver.execute_script("window.scrollTo(0, 300);")
                        time.sleep(1)
                    
                    # 查找所有a标签
                    all_a_elements = driver.find_elements(By.TAG_NAME, 'a')
                    temp_links = []
                    
                    for element in all_a_elements:
                        try:
                            href = element.get_attribute('href')
                            if href:
                                if ('toutiao.com/video/' in href or 
                                    'toutiao.com/i/video/' in href or
                                    '/video/' in href):
                                    if href not in temp_links and href != driver.current_url:
                                        temp_links.append(href)
                        except Exception:
                            continue
                    
                    # 保持顺序，去重
                    seen = set()
                    for href in temp_links:
                        if href not in seen:
                            seen.add(href)
                            video_links.append(href)
                    
                    if video_links:
                        break
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"第 {attempt+1} 次查找视频链接失败: {e}")
            
            print(f"共找到 {len(video_links)} 个视频链接")
            for vlink in video_links:
                print(f"  - {vlink}")
            
            # 取配置的每个用户处理视频数量
            from utils.config import config
            videos_per_user = config.get("operation.cycle.videos_per_user", 5)
            video_links = video_links[:videos_per_user]
            print(f"将处理前 {len(video_links)} 个视频")
            
            # 对视频链接执行点赞操作
            for i, video_link in enumerate(video_links):
                try:
                    print(f"正在处理视频 {i+1}/{len(video_links)}: {video_link}")
                    
                    # 直接在当前窗口导航到视频页面
                    driver.get(video_link)
                    time.sleep(random.uniform(2, 4))
                    
                    # 执行点赞操作
                    liked = self.operate.content_click_like()
                    log_like_operation(video_link, liked, f"点赞用户视频 {i+1}")
                    if liked:
                        page_success_count += 1
                        if process_stats:
                            process_stats["success_likes"] += 1
                    else:
                        if process_stats:
                            process_stats["failed_likes"] += 1
                    
                    # 执行评论操作（100%概率）
                    if self.match_comment_item_map:
                        try:
                            print("尝试执行视频评论操作...")
                            page_title = driver.title
                            comment_text = self.operate.generate_comment(
                                page_title, 
                                self.match_comment_item_map
                            )
                            print(f"生成评论: {comment_text}")
                            comment_success = self.operate.content_comment(comment_text)
                            if comment_success:
                                print("视频评论成功")
                            else:
                                print("视频评论失败")
                        except Exception as e:
                            print(f"视频评论操作异常: {e}")
                    
                except Exception as e:
                    print(f"处理视频 {i+1} 失败: {e}")
        except Exception as e:
            print(f"处理用户主页失败: {e}")
        
        return page_success_count
    
    def _process_content_link(self, link, driver, original_window, log_like_operation):
        """处理内容链接，返回成功点赞数量"""
        from selenium.common.exceptions import NoSuchWindowException, WebDriverException
        global process_stats
        
        content_success_count = 0
        try:
            # 直接在当前窗口导航到内容链接
            driver.get(link)
            # 随机延迟，避免被风控
            time.sleep(random.uniform(2, 4))
            
            # 执行点赞操作
            liked = self.operate.content_click_like()
            log_like_operation(link, liked, "点赞内容")
            if liked:
                content_success_count = 1
                if process_stats:
                    process_stats["success_likes"] += 1
            else:
                if process_stats:
                    process_stats["failed_likes"] += 1
            
            # 执行评论操作（100%概率）
            if self.match_comment_item_map:
                try:
                    print("尝试执行评论操作...")
                    page_title = driver.title
                    comment_text = self.operate.generate_comment(
                        page_title, 
                        self.match_comment_item_map
                    )
                    print(f"生成评论: {comment_text}")
                    comment_success = self.operate.content_comment(comment_text)
                    if comment_success:
                        print("评论成功")
                    else:
                        print("评论失败")
                except Exception as e:
                    print(f"评论操作异常: {e}")
            
        except Exception as e:
            print(f"处理内容链接失败: {e}")
        
        return content_success_count
    
    def search_account(self, operation_num):
        """处理关注列表的内容 - 每次批量处理10位关注者，循环处理"""
        try:
            # 如果还没有获取所有关注者，先获取一次
            if not self.all_followed_users:
                print("首次获取所有关注用户列表...")
                self.all_followed_users = self.get_followed_content()
                print(f"共获取到 {len(self.all_followed_users)} 个关注用户")
            
            # 过滤出未处理的用户
            unprocessed_users = [user for user in self.all_followed_users if user not in self.processed_users]
            print(f"剩余未处理用户: {len(unprocessed_users)}")
            
            # 如果所有用户都已处理，重置processed_users，从头开始
            if not unprocessed_users:
                print("所有用户已处理完毕，重置并从头开始...")
                self.processed_users.clear()
                unprocessed_users = self.all_followed_users.copy()
            
            # 取配置的未处理用户数量
            from utils.config import config
            users_per_cycle = config.get("operation.cycle.users_per_cycle", 10)
            batch_users = unprocessed_users[:users_per_cycle]
            print(f"本次批量处理 {len(batch_users)} 位用户")
            
            # 处理这批用户
            log_follow_operation(len(batch_users), 0)
            self.process_content(batch_users, operation_num)
            
            # 标记这批用户为已处理
            for user in batch_users:
                self.processed_users.add(user)
            
            print(f"已处理用户数: {len(self.processed_users)}/{len(self.all_followed_users)}")
            
        except Exception as e:
            print(f"处理关注内容失败: {e}")
            log_follow_operation(0, 0)
    
    def search_recommended(self, operation_num):
        """处理推荐列表的内容 - 使用配置项控制数量"""
        # 获取首页推荐列表的内容链接
        try:
            from utils.config import config
            max_links_per_cycle = config.get("operation.max_links_per_cycle", 10)
            recommended_content = self.get_recommended_content()
            # 取配置的推荐内容数量
            recommended_content = recommended_content[:max_links_per_cycle]
            print(f"总共处理 {len(recommended_content)} 个推荐内容链接")
            log_recommend_operation(len(recommended_content), 0)  # 初始记录，后续在process_content中更新
            self.process_content(recommended_content, operation_num)
        except Exception as e:
            print(f"处理推荐内容失败: {e}")
            log_recommend_operation(0, 0)


