import requests
import schedule
import time
from bs4 import BeautifulSoup  
import ddddocr
import smtplib
from email.mime.text import MIMEText

# 邮件发送者和接收者的邮箱地址及密码
SENDER_EMAIL = '3362863893@qq.com'
SENDER_PASSWORD = 'kfydimmtetqmdadi'
RECEIVER_EMAIL = '1533068067@qq.com'

# 存储上次获取的成绩
last_grades = []

# 登录和成绩抓取类
class User:
    __root = "http://jwxt.gdufe.edu.cn"
    __base = "/jsxsd"
    __captcha = "/verifycode.servlet"
    __login = "/xk/LoginToXkLdap"
    __grades = "/jsxsd/kscj/cjcx_list"

    def __init__(self, username, password):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.logged_in = False

    def login(self):
        try:
            # 获取验证码
            response = self.session.get(self.__root + self.__base + self.__captcha)
            # 识别验证码
            ocr = ddddocr.DdddOcr(show_ad=False)
            captcha_text = ocr.classification(response.content)
            # 发送登录请求
            data = {
                "USERNAME": self.username,
                "PASSWORD": self.password,
                "RANDOMCODE": captcha_text
            }
            response = self.session.post(self.__root + self.__base + self.__login, data=data, allow_redirects=False)


            self.logged_in = response.status_code == 302
        
        except Exception as e:
            print(f"登录时发生错误: {e}")
            self.logged_in = False  # 确保登录失败时logged_in被重置

    def fetch_grades(self):
        print("成绩查询前的登录状态:", self.logged_in)
        if not self.logged_in:
            raise Exception("请先登录再尝试访问成绩页面。")
        
        try:
            # 请求成绩页面
            grades_response = self.session.get(self.__root + self.__grades)
            # 解析成绩页面
            soup = BeautifulSoup(grades_response.text, 'html.parser')
            
            # 查找所有的成绩条目
            grade_entries = soup.find_all('tr')
            
            # 提取成绩信息
            grades = []
            for entry in grade_entries:
                cells = entry.find_all('td')
                if len(cells) >= 12:
                    course_name = cells[3].text.strip()
                    grade_link = entry.find('a', href=lambda href: href and href.startswith('javascript:JsMod'))
                    grade_cell = entry.find('td', string=lambda text: text and text.isdigit())
                    
                    # 如果找到了成绩链接
                    grade = None
                    if grade_link:
                        href = grade_link['href']
                        zcj_start = href.find('zcj=') + 4
                        zcj_end = href.find(',', zcj_start)
                        grade = href[zcj_start:zcj_end]
                        grades.append((course_name, grade))
                    # 如果没有找到成绩链接，但找到了直接显示的成绩
                    elif grade_cell:
                        grade = grade_cell.string
            return grades
        except Exception as e:
            print(f"成绩抓取时发生错误: {e}")
            return []

# 发送邮件
def send_email(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"发送邮件时发生错误: {e}")

# 监控新成绩
def monitor_grades(user):
    global last_grades
    try:
        user.login()
        new_grades = user.fetch_grades()
        new_courses = [course for course in new_grades if course not in last_grades]
        if new_courses:
            message = "\n".join([f"{course[0]}: {course[1]}" for course in new_courses])            
            send_email("新成绩通知", message)
            last_grades = new_grades
    except Exception as e:
        print(f"成绩监控时发生错误: {e}")

# 初始化用户
user = User("23250601316", "xukai8088A")

# 添加定时任务
schedule.every(1).seconds.do(monitor_grades, user)

# 运行定时任务
while True:
    schedule.run_pending()
    time.sleep(1)