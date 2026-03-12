import random
import time

from helium import *
from helium import get_driver
from selenium.webdriver.common.by import By

"""
1. 内容点赞
2. 内容收藏
3. 内容评论
4. 用户关注
"""


class Operation:

    #
    # 内容点赞
    #
    def content_click_like(self):
        """点赞内容"""
        time.sleep(random.uniform(1.5, 3))
        try:
            driver = get_driver()
            current_url = driver.current_url
            print(f"开始执行点赞操作... 当前URL: {current_url}")
            
            # 检测页面类型
            is_article = '/article/' in current_url or '/i/' in current_url
            is_video = '/video/' in current_url or '/i/video/' in current_url
            
            if is_article:
                print("检测到文章页面")
            elif is_video:
                print("检测到视频页面")
            else:
                print("无法确定页面类型，尝试通用定位")
            
            # 文章页面专用定位器
            article_like_locators = [
                "//*[contains(@class, 'digg')]//*[self::button or self::div]",
                "//*[contains(@class, 'like')]//*[self::button or self::div]",
                "//*[local-name()='svg']/ancestor::*[self::button or self::div][contains(@class, 'digg') or contains(@class, 'like')]",
                "//*[local-name()='svg']/ancestor::*[self::button or self::div]",
                "//div[contains(@class, 'article-interact')]//*[self::button or self::div]",
                "//div[contains(@class, 'interact-bar')]//*[self::button or self::div]",
                "//div[contains(@class, 'interaction')]//*[self::button or self::div]",
                "//button[@data-log-click*='like']",
                "//button[@data-log-click*='digg']",
                "//div[@data-log-click*='like']",
                "//div[@data-log-click*='digg']",
            ]
            
            # 视频页面专用定位器
            video_like_locators = [
                "//button[contains(@class, 'like')]",
                "//div[contains(@class, 'like')]//button",
                "//span[contains(@class, 'like')]",
                "//button[contains(text(), '点赞')]",
                "//div[contains(text(), '点赞')]",
                "//span[contains(text(), '点赞')]",
                "//button[@data-testid='like']",
                "//div[@class='like-btn']",
                "//button[@class='digg-btn']",
                "//div[@class='digg']//button",
            ]
            
            # 通用定位器
            general_like_locators = [
                "//button[.//*[local-name()='svg']]",
                "//div[.//*[local-name()='svg']]",
                "//*[contains(@class, 'btn')]//*[local-name()='svg']/ancestor::*[self::button or self::div]",
            ]
            
            # 组合定位器优先级
            if is_article:
                like_locators = article_like_locators + video_like_locators + general_like_locators
            elif is_video:
                like_locators = video_like_locators + article_like_locators + general_like_locators
            else:
                like_locators = video_like_locators + article_like_locators + general_like_locators
            
            for locator in like_locators:
                try:
                    elements = driver.find_elements(By.XPATH, locator)
                    print(f"尝试点赞定位器: {locator[:80]}, 找到 {len(elements)} 个")
                    
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                class_name = element.get_attribute('class') or ''
                                text = element.text or ''
                                
                                # 检查是否已点赞
                                if "active" in class_name.lower() or "已" in text:
                                    print("该内容已经点赞啦，跳过")
                                    return False
                                
                                # 检查位置，排除顶部导航栏元素
                                location = element.location
                                if location['y'] < 100:
                                    continue
                                
                                try:
                                    element.click()
                                    print("✅ 点赞成功")
                                    time.sleep(1)
                                    return True
                                except Exception:
                                    try:
                                        driver.execute_script("arguments[0].click();", element)
                                        print("✅ 点赞成功 (JS)")
                                        time.sleep(1)
                                        return True
                                    except:
                                        continue
                        except:
                            continue
                except:
                    continue
            
            print("❌ 未找到点赞按钮")
            return False
        except Exception as e:
            print(f"❌ 点赞失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    #
    # 用户关注
    #
    def user_click_follow(self):
        time.sleep(random.uniform(2, 4))
        try:
            if Button("关注").exists():
                click("关注")
                print("关注成功")
            elif S("//button[@class='follow-btn']").exists():
                follow_button = S("//button[@class='follow-btn']")
                if "已关注" not in follow_button.web_element.text:
                    click(follow_button)
                    print("关注成功")
                else:
                    print("该用户已关注啦")
            elif Text("关注").exists():
                click(Text("关注"))
                print("关注成功")
            else:
                print("未找到关注按钮")
        except Exception as e:
            print(f"关注失败: {e}")

    #
    # 内容评论
    #
    def content_comment(self, comment_text):
        """对内容进行评论（发送表情）"""
        time.sleep(random.uniform(1, 2))
        try:
            driver = get_driver()
            current_url = driver.current_url
            print("=" * 60)
            print("开始评论（发送表情）")
            print(f"当前URL: {current_url}")
            
            # 检测页面类型
            is_article = '/article/' in current_url or '/i/' in current_url
            is_video = '/video/' in current_url or '/i/video/' in current_url
            
            if is_article:
                print("检测到文章页面")
            elif is_video:
                print("检测到视频页面")
            else:
                print("无法确定页面类型，尝试通用定位")
            
            print("\n【步骤1】滚动到页面交互区域...")
            try:
                if is_article:
                    # 文章页面滚动到评论区
                    driver.execute_script("window.scrollTo(0, Math.max(300, document.body.scrollHeight - 1500));")
                    time.sleep(1)
                else:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 800);")
                    time.sleep(1)
            except:
                pass
            
            print("\n【步骤2】尝试点击评论按钮打开评论区...")
            comment_button_found = False
            
            def is_valid_interact_element(element):
                """判断元素是否可能是交互按钮（评论、点赞等）"""
                try:
                    cls = (element.get_attribute('class') or '').lower()
                    text = (element.text or '').lower()
                    aria = (element.get_attribute('aria-label') or '').lower()
                    
                    excluded_keywords = ['city', 'search', 'header', 'nav', 'logo', 'publish', 'notification', 'back']
                    for keyword in excluded_keywords:
                        if keyword in cls or keyword in text or keyword in aria:
                            return False
                    
                    included_keywords = ['comment', 'like', 'digg', 'share', 'collect', 'interact', 'btn', 'button', '评论']
                    for keyword in included_keywords:
                        if keyword in cls or keyword in text or keyword in aria:
                            return True
                    
                    has_svg = len(element.find_elements(By.XPATH, ".//*[local-name()='svg']")) > 0
                    return has_svg
                except:
                    return False
            
            # 文章页面专用评论定位器
            article_comment_locators = [
                "//*[contains(@class, 'comment')]//*[self::button or self::div]",
                "//*[local-name()='svg']/ancestor::*[self::button or self::div][contains(@class, 'comment')]",
                "//*[local-name()='svg']/ancestor::*[self::button or self::div]",
                "//div[contains(@class, 'article-interact')]//*[self::button or self::div]",
                "//div[contains(@class, 'interact-bar')]//*[self::button or self::div]",
                "//div[contains(@class, 'interaction')]//*[self::button or self::div]",
                "//button[@data-log-click*='comment']",
                "//div[@data-log-click*='comment']",
                "//*[contains(text(), '评论')]//ancestor::*[self::button or self::div]",
                "//button[contains(@title, '评论')]",
                "//div[contains(@title, '评论')]",
            ]
            
            # 视频页面专用评论定位器
            video_comment_locators = [
                "//button[contains(@class, 'comment')]",
                "//div[contains(@class, 'comment-btn')]",
                "//button[@data-testid='comment']",
                "//div[@data-testid='comment']",
                "//*[contains(@class, 'interact')]//*[contains(@class, 'comment')]",
                "//*[contains(@class, 'action')]//*[contains(@class, 'comment')]",
            ]
            
            # 通用评论定位器
            general_comment_locators = [
                "//button[.//*[local-name()='svg']]",
                "//div[.//*[local-name()='svg']]",
            ]
            
            # 组合定位器优先级
            if is_article:
                comment_locators = article_comment_locators + video_comment_locators + general_comment_locators
            elif is_video:
                comment_locators = video_comment_locators + article_comment_locators + general_comment_locators
            else:
                comment_locators = video_comment_locators + article_comment_locators + general_comment_locators
            
            for locator in comment_locators:
                try:
                    elements = driver.find_elements(By.XPATH, locator)
                    print(f"尝试定位器: {locator[:80]}... 找到 {len(elements)} 个")
                    
                    valid_elements = []
                    for element in elements:
                        try:
                            if element.is_displayed() and is_valid_interact_element(element):
                                # 排除顶部导航栏的元素
                                location = element.location
                                if location['y'] < 100:
                                    continue
                                valid_elements.append(element)
                        except:
                            continue
                    
                    print(f"  其中 {len(valid_elements)} 个有效候选")
                    
                    for element in valid_elements:
                        try:
                            cls = element.get_attribute('class') or ''
                            text = element.text or ''
                            print(f"  候选元素 - class: {cls[:50]}, text: {text[:25]}")
                            
                            try:
                                element.click()
                                print("  ✅ 点击成功！")
                                time.sleep(2)
                                comment_button_found = True
                                break
                            except:
                                try:
                                    driver.execute_script("arguments[0].click();", element)
                                    print("  ✅ JS点击成功！")
                                    time.sleep(2)
                                    comment_button_found = True
                                    break
                                except:
                                    continue
                        except:
                            continue
                    if comment_button_found:
                        break
                except:
                    continue
            
            if not comment_button_found:
                print("⚠️ 未找到评论按钮，继续尝试后续步骤...")
            
            time.sleep(1.5)
            
            # 对于文章页面，可能不需要点击评论按钮，直接就有评论输入框
            print("\n【步骤3】查找评论输入框...")
            input_found = False
            input_element = None
            
            # 文章页面输入框定位器
            article_input_locators = [
                "//textarea[@placeholder or contains(@placeholder, '说点什么')]",
                "//div[@contenteditable='true' and (@placeholder or contains(text(), '说点什么'))]",
                "//textarea[contains(@placeholder, '评论')]",
                "//div[@contenteditable='true' and contains(@placeholder, '评论')]",
                "//div[@contenteditable='true']",
                "//textarea",
                "//*[contains(@class, 'comment-input')]//div[@contenteditable='true']",
                "//*[contains(@class, 'comment-editor')]//div[@contenteditable='true']",
                "//*[contains(@class, 'comment')]//div[@contenteditable='true']",
                "//*[contains(@class, 'comment')]//textarea",
            ]
            
            # 视频页面输入框定位器
            video_input_locators = [
                "//div[@contenteditable='true']",
                "//textarea",
            ]
            
            if is_article:
                input_locators = article_input_locators + video_input_locators
            else:
                input_locators = video_input_locators + article_input_locators
            
            for locator in input_locators:
                try:
                    elements = driver.find_elements(By.XPATH, locator)
                    print(f"尝试输入框定位器: {locator[:60]}... 找到 {len(elements)} 个")
                    
                    for elem in elements:
                        try:
                            if elem.is_displayed() and elem.is_enabled():
                                location = elem.location
                                if location['y'] < 100:
                                    continue
                                input_element = elem
                                input_found = True
                                print("  ✅ 找到输入框")
                                break
                        except:
                            continue
                    if input_found:
                        break
                except:
                    continue
            
            # 直接输入文本评论（不使用表情）
            if input_found and input_element:
                try:
                    print(f"\n【步骤4】输入评论内容: {comment_text}")
                    input_element.click()
                    time.sleep(0.5)
                    input_element.clear()
                    time.sleep(0.3)
                    input_element.send_keys(comment_text)
                    time.sleep(1)
                    print("  ✅ 输入评论内容成功")
                    
                    print("\n【步骤5】点击发送按钮...")
                    send_success = False
                    
                    # 文章页面发送按钮定位器
                    article_send_locators = [
                        "//button[contains(@class, 'submit') and contains(@class, 'comment')]",
                        "//button[contains(text(), '发布')]",
                        "//button[contains(text(), '发送')]",
                        "//div[contains(@class, 'submit')]//button",
                        "//*[contains(@class, 'comment')]//button[contains(@class, 'send')]",
                        "//*[contains(@class, 'comment')]//button[contains(text(), '发布')]",
                        "//*[contains(@class, 'comment')]//button[contains(text(), '发送')]",
                    ]
                    
                    # 视频页面发送按钮定位器
                    video_send_locators = [
                        "//button[contains(text(), '评论')]",
                        "//div[contains(text(), '评论')]",
                        "//button[contains(text(), '发送')]",
                        "//button[contains(text(), '发布')]",
                        "//div[contains(text(), '发送')]",
                        "//div[contains(text(), '发布')]",
                        "//button[contains(@class, 'send')]",
                        "//button[contains(@class, 'submit')]",
                        "//*[contains(@class, 'comment')]//button",
                        "//button",
                        "//div[@role='button']",
                    ]
                    
                    if is_article:
                        send_locators = article_send_locators + video_send_locators
                    else:
                        send_locators = video_send_locators + article_send_locators
                    
                    def is_valid_send_element(element):
                        try:
                            if not element.is_displayed() or not element.is_enabled():
                                return False
                            cls = (element.get_attribute('class') or '').lower()
                            text = (element.text or '').lower()
                            aria = (element.get_attribute('aria-label') or '').lower()
                            
                            excluded_keywords = ['city', 'search', 'header', 'nav', 'logo', 'notification', 'back', 'follow', '关注', 'home', '首页', 'channel', '频道', 'like', '点赞', 'collect', '收藏', 'share', '分享', 'emoji', '表情']
                            for keyword in excluded_keywords:
                                if keyword in cls or keyword in text or keyword in aria:
                                    return False
                            
                            location = element.location
                            if location['y'] < 100:
                                return False
                            
                            return True
                        except:
                            return False
                    
                    for locator in send_locators:
                        try:
                            elements = driver.find_elements(By.XPATH, locator)
                            print(f"尝试发送按钮定位器: {locator[:60]}... 找到 {len(elements)} 个")
                            
                            valid_elements = []
                            for element in elements:
                                if is_valid_send_element(element):
                                    valid_elements.append(element)
                            
                            print(f"  其中 {len(valid_elements)} 个有效候选")
                            
                            for element in valid_elements:
                                try:
                                    text = element.text or ''
                                    cls = element.get_attribute('class') or ''
                                    print(f"  发送候选 - text: {text[:25]}, class: {cls[:45]}")
                                    
                                    try:
                                        element.click()
                                        print("  ✅ 点击发送按钮成功！")
                                        time.sleep(1.5)
                                        send_success = True
                                        break
                                    except:
                                        try:
                                            driver.execute_script("arguments[0].click();", element)
                                            print("  ✅ JS点击发送按钮成功！")
                                            time.sleep(1.5)
                                            send_success = True
                                            break
                                        except:
                                            continue
                                except:
                                    continue
                            if send_success:
                                break
                        except Exception as e:
                            print(f"  发送按钮定位器异常: {e}")
                            continue
                    
                    if send_success:
                        print("\n✅ 评论流程完成！")
                        return True
                    else:
                        print("\n❌ 评论发送失败，未找到发送按钮")
                        return False
                    
                except Exception as e:
                    print(f"  输入评论异常: {e}")
                    import traceback
                    traceback.print_exc()
            
            print("\n❌ 评论流程失败")
            return False
                
        except Exception as e:
            print(f"❌ 评论异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    #
    # 智能评论生成
    #
    def generate_comment(self, content_keywords, comment_map):
        """根据关键词生成智能评论"""
        for keyword, comment in comment_map.items():
            if keyword.lower() in str(content_keywords).lower():
                return comment
        
        default_comments = [
            "说得太好了！",
            "学习了，感谢分享！",
            "这个观点很有道理",
            "支持一下！",
            "写得不错！",
            "太有意思了！",
            "精彩！",
        ]
        return random.choice(default_comments)

    #
    # 评论区互动
    #
    def interact_with_comments(self, max_replies=3):
        """与评论区互动"""
        time.sleep(random.uniform(2, 4))
        try:
            driver = get_driver()
            
            reply_locators = [
                "//button[contains(text(), '回复')]",
                "//span[contains(text(), '回复')]",
            ]
            
            reply_count = 0
            for locator in reply_locators:
                try:
                    elements = driver.find_elements(By.XPATH, locator)
                    for element in elements:
                        if reply_count >= max_replies:
                            break
                        try:
                            if element.is_displayed() and element.is_enabled():
                                element.click()
                                time.sleep(random.uniform(1, 2))
                                reply_count += 1
                                print(f"回复了第 {reply_count} 条评论")
                        except:
                            continue
                except:
                    continue
            
            if reply_count > 0:
                print(f"共回复了 {reply_count} 条评论")
                return True
            return False
        except Exception as e:
            print(f"评论区互动失败: {e}")
            return False
