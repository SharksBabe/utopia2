from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import csv
import datetime
import hashlib
import re

# 目标网址
URL = "https://www.biligame.com/detail/?id=108406&sourceFrom=2000040011&spm_id_from=333.337.0.0"

# 模拟浏览器配置
edge_options = Options()
# 使用无头模式，提高爬取速度
edge_options.add_argument("--headless")  # 无头模式
edge_options.add_argument("--disable-gpu")  # 禁用GPU加速
edge_options.add_argument("--no-sandbox")  # 禁用沙箱
edge_options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化控制标记
edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
edge_options.add_experimental_option("useAutomationExtension", False)
# 禁用图片加载，提高速度
edge_options.add_argument("--blink-settings=imagesEnabled=false")
# 禁用插件
edge_options.add_argument("--disable-extensions")
# 禁用缓存
edge_options.add_argument("--disable-cache")
# 禁用应用缓存
edge_options.add_argument("--disable-application-cache")
# 禁用媒体自动播放
edge_options.add_argument("--media-cache-size=0")

# 初始化浏览器
driver = webdriver.Edge(options=edge_options)

# 访问目标网址
driver.get(URL)

# 等待页面加载
wait = WebDriverWait(driver, 20)

# 等待评论区域加载
print("等待页面加载...")
print(f"当前页面标题: {driver.title}")
print(f"当前页面URL: {driver.current_url}")

comments_data = []
# 取消30000条限制，设置为一个非常大的值
max_comments = 999999999
# 分批处理大小
batch_size = 1000
# 全局去重集合
global_comment_hashes = set()
# 文件路径
json_path = "bilibili_endfield_comments_edge.json"
csv_path = "bilibili_endfield_comments_edge.csv"

# 初始化CSV文件
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    # 写入表头
    writer.writerow(['content', 'username', 'level', 'stars', 'likes', 'time'])

try:
    # 等待页面完全加载
    time.sleep(3)  # 减少等待时间
    
    # 尝试找到评价标签 - 根据用户提供的信息
    print("尝试找到评价标签...")
    
    # 尝试不同的选择器，优先使用最可能的选择器
    selectors = [
        "//a[contains(text(), '评价')]",
        "//*[contains(text(), '评价')]",
        "//a[contains(@class, 'active') and contains(text(), '评价')]",
        "//a[contains(@style, 'cursor: pointer') and contains(text(), '评价')]"
    ]
    
    comment_button = None
    for selector in selectors:
        try:
            buttons = driver.find_elements(By.XPATH, selector)
            if buttons:
                comment_button = buttons[0]
                print(f"使用选择器 '{selector}' 找到评价标签")
                break
        except Exception as e:
            print(f"使用选择器 '{selector}' 失败: {str(e)}")
            continue
    
    if comment_button:
        # 点击评价标签
        print("点击评价标签")
        comment_button.click()
        
        # 等待评论区域加载
        time.sleep(2)  # 减少等待时间
        
        print("开始获取评论...")
        
        # 尝试找到评论列表
        while len(global_comment_hashes) < max_comments:
            # 尝试不同的选择器来找到评论列表
            comment_list = []
            selectors = [
                "comment-item",
                "comment-list-item",
                "comment",
                "review-item",
                "review"
            ]
            
            for selector in selectors:
                try:
                    comment_list = driver.find_elements(By.CLASS_NAME, selector)
                    if comment_list:
                        print(f"使用选择器 '{selector}' 找到 {len(comment_list)} 条评论")
                        break
                except:
                    continue
            
            if not comment_list:
                # 尝试使用XPath
                try:
                    comment_list = driver.find_elements(By.XPATH, "//div[contains(@class, 'comment')]")
                    if comment_list:
                        print(f"使用XPath找到 {len(comment_list)} 条评论")
                except:
                    pass
            
            if not comment_list:
                print("未找到评论列表")
                # 尝试滚动页面
                print("尝试滚动页面...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                continue
            
            # 解析评论数据
            for comment in comment_list:
                try:
                    # 先查找comment-main标签
                    comment_main = None
                    try:
                        comment_main = comment.find_element(By.XPATH, ".//div[@class='comment-main']")
                    except:
                        # 如果没有找到comment-main，使用当前元素
                        comment_main = comment
                    
                    # 检查是否有星星评分
                    has_stars = False
                    try:
                        # 使用CSS选择器查找带有filled类的星星
                        filled_stars = comment_main.find_elements(By.CSS_SELECTOR, "svg.bui-icon.bui-icon-star.filled")
                        if len(filled_stars) > 0:
                            has_stars = True
                        else:
                            # 没有星星评分，跳过该评论
                            continue
                    except:
                        # 没有找到星星评分，跳过该评论
                        continue
                    
                    # 评论内容 - 尝试不同的选择器
                    content = ""
                    content_selectors = [
                        "comment-content",
                        "content",
                        "review-content",
                        "comment-text"
                    ]
                    
                    for cs in content_selectors:
                        try:
                            content = comment_main.find_element(By.CLASS_NAME, cs).text
                            break
                        except:
                            continue
                    
                    if not content:
                        try:
                            content = comment_main.find_element(By.XPATH, ".//div[contains(@class, 'content')]").text
                        except:
                            pass
                    
                    # 去重检查
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    if content_hash in global_comment_hashes:
                        continue
                    global_comment_hashes.add(content_hash)
                    
                    # 用户名 - 尝试不同的选择器
                    username = ""
                    username_selectors = [
                        "username",
                        "user-name",
                        "reviewer",
                        "commenter"
                    ]
                    
                    for us in username_selectors:
                        try:
                            username = comment_main.find_element(By.CLASS_NAME, us).text
                            break
                        except:
                            continue
                    
                    if not username:
                        try:
                            username = comment_main.find_element(By.XPATH, ".//div[contains(@class, 'user')]").text
                        except:
                            pass
                    
                    # 用户等级 - 根据用户提供的信息
                    level = ""
                    try:
                        # 查找带有level属性的i元素
                        level_element = comment_main.find_element(By.XPATH, ".//i[@class='bui-user-level']")
                        level = level_element.get_attribute("level")
                    except:
                        # 尝试其他可能的选择器
                        level_selectors = [
                            "user-level",
                            "level",
                            "user-info",
                            "user-level-info"
                        ]
                        
                        for ls in level_selectors:
                            try:
                                level = comment_main.find_element(By.CLASS_NAME, ls).text
                                break
                            except:
                                continue
                        
                        if not level:
                            try:
                                level = comment_main.find_element(By.XPATH, ".//div[contains(@class, 'level')]").text
                            except:
                                pass
                    
                    # 推荐星星数
                    stars = 0
                    try:
                        # 使用CSS选择器查找带有filled类的星星
                        filled_stars = comment_main.find_elements(By.CSS_SELECTOR, "svg.bui-icon.bui-icon-star.filled")
                        stars = len(filled_stars)
                    except:
                        stars = 0
                    
                    # 获赞数
                    likes = 0
                    try:
                        # 查找up-count类的元素
                        up_count_element = comment_main.find_element(By.CLASS_NAME, "up-count")
                        likes_text = up_count_element.text.strip()
                        # 提取数字
                        likes_match = re.search(r'\d+', likes_text)
                        if likes_match:
                            likes = int(likes_match.group())
                    except:
                        # 尝试查找带有like类的元素
                        try:
                            like_elements = comment_main.find_elements(By.XPATH, ".//*[contains(@class, 'like')]")
                            for element in like_elements:
                                try:
                                    likes_text = element.text.strip()
                                    likes_match = re.search(r'\d+', likes_text)
                                    if likes_match:
                                        likes = int(likes_match.group())
                                        break
                                except:
                                    continue
                        except:
                            pass
                    
                    # 只有当评论内容不为空时才添加
                    if content:
                        # 获取评论时间
                        normal_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        try:
                            # 查找footer标签内的span标签，获取title属性中的时间
                            footer = comment_main.find_element(By.XPATH, ".//footer[@class='clearfix']")
                            time_span = footer.find_element(By.TAG_NAME, "span")
                            time_title = time_span.get_attribute("title")
                            if time_title:
                                normal_time = time_title
                        except:
                            pass
                        comments_data.append({
                            "content": content,
                            "username": username,
                            "level": level,
                            "stars": stars,
                            "likes": likes,
                            "time": normal_time
                        })
                        
                        # 检查是否达到分批处理大小
                        if len(comments_data) >= batch_size:
                            # 写入CSV文件
                            with open(csv_path, 'a', encoding='utf-8-sig', newline='') as f:
                                writer = csv.writer(f)
                                for comment in comments_data:
                                    writer.writerow([
                                        comment['content'].replace('\n', ' '),
                                        comment['username'],
                                        comment['level'],
                                        comment['stars'],
                                        comment['likes'],
                                        comment['time']
                                    ])
                            # 清空数据，释放内存
                            comments_data = []
                            print(f"已处理 {len(global_comment_hashes)} 条评论")
                        
                        # 检查是否达到目标数量
                        if len(global_comment_hashes) >= max_comments:
                            break
                            
                except Exception as e:
                    # 静默处理错误，减少输出
                    continue
            
            # 尝试点击下一页 - 尝试不同的选择器
            next_page_found = False
            
            # 尝试找到下一页链接
            try:
                next_page = driver.find_element(By.XPATH, "//a[contains(text(), '下一页')]")
                if next_page.is_displayed() and next_page.is_enabled():
                    next_page.click()
                    time.sleep(0.5)  # 进一步减少等待时间
                    next_page_found = True
            except:
                pass
            
            if not next_page_found:
                # 尝试其他可能的选择器
                next_selectors = [
                    "next-page",
                    "page-next",
                    "next",
                    "pagination-next"
                ]
                
                for ns in next_selectors:
                    try:
                        next_page = driver.find_element(By.CLASS_NAME, ns)
                        if next_page.is_displayed() and next_page.is_enabled():
                            next_page.click()
                            time.sleep(0.5)  # 进一步减少等待时间
                            next_page_found = True
                            break
                    except:
                        continue
            
            if not next_page_found:
                # 尝试使用XPath查找按钮
                try:
                    next_page = driver.find_element(By.XPATH, "//button[contains(text(), '下一页')]")
                    if next_page.is_displayed() and next_page.is_enabled():
                        next_page.click()
                        time.sleep(0.5)  # 减少等待时间
                        next_page_found = True
                except:
                    pass
            
            if not next_page_found:
                # 尝试滚动加载
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)  # 进一步减少等待时间
                
                # 检查是否有新评论加载
                new_comment_list = []
                for selector in selectors:
                    try:
                        new_comment_list = driver.find_elements(By.CLASS_NAME, selector)
                        if len(new_comment_list) > len(comment_list):
                            break
                    except:
                        continue
                
                if len(new_comment_list) <= len(comment_list):
                    break
                
        # 保存最后一批数据
        if comments_data:
            # 写入CSV文件
            with open(csv_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                for comment in comments_data:
                    writer.writerow([
                        comment['content'].replace('\n', ' '),
                        comment['username'],
                        comment['level'],
                        comment['stars'],
                        comment['likes'],
                        comment['time']
                    ])
        
        print(f"共获取到 {len(global_comment_hashes)} 条评论")
        print(f"评论数据已保存到 {csv_path}")
            
finally:
    # 关闭浏览器
    driver.quit()
    print("浏览器已关闭")