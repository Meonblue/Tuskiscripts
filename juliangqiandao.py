from selenium.webdriver.common.action_chains import ActionChains
import requests, re, os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import cv2 as cv

driver = webdriver.Chrome()


def get_users():
    users= []
    os.environ.get("jlqduser")
    if '&' in os.environ["jlqduser"]:
    users = os.environ["jlqduser"].split('&')
    return users
    
def _tran_canny(image):
    """消除噪声"""
    image = cv.GaussianBlur(image, (3, 3), 0)
    return cv.Canny(image, 50, 150)


def detect_displacement(img_slider_path, image_background_path):
    """detect displacement"""
    # # 参数0是灰度模式
    image = cv.imread(img_slider_path, 0)
    template = cv.imread(image_background_path, 0)
    background = cv.resize(template, (0, 0), fx=0.5, fy=0.5)
    # 寻找最佳匹配
    res = cv.matchTemplate(_tran_canny(image), _tran_canny(background), cv.TM_CCOEFF_NORMED)
    # 最小值，最大值，并得到最小值, 最大值的索引
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

    top_left = max_loc[0]  # 横坐标
    # 展示圈出来的区域
    x, y = max_loc  # 获取x,y位置坐标

    w, h = image.shape[::-1]  # 宽高
    cv.rectangle(background, (x, y), (x + w, y + h), (7, 249, 151), 2)
    return top_left


class juliangqd(object):
    url = 'https://www.juliangip.com/user/login'
    def login(self,name,password):
        name = name
        password = password
        print('执行登录')
        driver.get(self.url)
        driver.maximize_window()
        driver.find_element(By.XPATH, '//*[@id="phone"]').send_keys(name)
        sleep(1)
        driver.find_element(By.XPATH, '//*[@id="app"]/form/div/ul/li[2]/input').send_keys(password)
        sleep(1)
        driver.find_element(By.XPATH, '//*[@id="login"]').click()

    def checkout(self):
        print('登录成功')
        print('检测是否已经签到...')
        dtdl = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[4]/ul/li[1]/p')
        if '1个' not in dtdl.get_attribute('outerHTML'):
            print('该账号未签到')
            return True
        else:
            return False

    def getimages(self):

        driver.refresh()
        driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[2]/a[1]').click()
        sleep(3)
        driver.switch_to.frame('tcaptcha_iframe_dy')
        idata = driver.find_element(By.XPATH, '//*[@id="slideBg"]')
        imagedata = idata.get_attribute('style')
        imges_link = re.findall('url\("(.*?)\*"\);', imagedata)[0]
        # print(imges_link)
        try:
            image = requests.get(url=imges_link).content
            with open('background.png', 'wb') as f:
                f.write(image)
        except Exception as e:
            print("获取验证码失败")
        else:
            print('成功获取验证码')
        driver.find_element(By.XPATH, '//*[@id="tcOperation"]/div[6]').click()
        sleep(1)
        image2 = driver.find_element(By.XPATH, '/html/body/div/div[3]/div[2]/div[8]')
        image2.screenshot('target.png')
        image3 = driver.find_element(By.XPATH, '/html/body/div/div[3]/div[2]/div[7]')
        image3.screenshot('target1.png')
        '''
        image2= driver.find_element(By.XPATH, '//div[@id="tcOperation"]')
        image2=image2.get_attribute('outerHTML')
        # print(image2)
        x= re.findall('left: (.*?)px',image2)[2].split('.')[0]
        y = re.findall('top: (.*?)px', image2)[2].split('.')[0]
        print(x,y)
        x1, y1= 789 + int(x), 355 + int(y)
        x2, y2 = x1 + 57, y1 + 55
        #print(image2.size['width'], image2.size['height'])
        print('截图坐标：',x1,y1,x2,y2)
        screen_shot= driver.get_screenshot_as_png()
        screen_shot= Image.open(BytesIO(screen_shot))
        driver.switch_to.default_content()
        target= screen_shot.crop((int(x1),int(y1),int(x2),int(y2)))
        target.save('target.png')
        driver.switch_to.default_content()
'''

    def get_track(seft, distance):  # distance为传入的总距离
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 1

        while current < distance:
            if current < mid:
                # 加速度为2
                a = 4
            else:
                # 加速度为-2
                a = -3
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def checkin(self, tracks):
        huatiao = driver.find_element(By.XPATH, '//*[@id="tcOperation"]/div[6]')
        ActionChains(driver).click_and_hold(huatiao).perform()
        for x in tracks:
            ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
            sleep(0.1)
        ActionChains(driver).release().perform()
        sleep(1)
        driver.get('https://www.juliangip.com/users/')


if __name__ == '__main__':
    users= get_users()
    if len(users) == 0 :
        print('未配置账户，退出脚本')
    else:
        i= 1
        for x in users:
            print(f'====================正在执行第{i}个账号=========\n')
            name= re.findall('(.*?)@$', x)[0]
            password= re.findall('@(.*?)', x)[0]
            jlqd = juliangqd(name,password)
            jlqd.login()
            sleep(2)
            checkout = jlqd.checkout()
            i= 1
            while checkout == True and i <= 5 :
                print(f'正在执行第{i}次签到')
                jlqd.getimages()
                try:
                    remove = detect_displacement('target.png', 'background.png')
                    print('首次值为:', remove)
                except Exception as e:
                    remove = detect_displacement('target1.png', 'background.png')
                    print('二次值为:', remove)
                tracks = jlqd.get_track(remove - 18)
                jlqd.checkin(tracks)
                sleep(5)
                print('任务执行完成，重新检测是否签到....')
                checkout = jlqd.checkout()
                i= i+1
            else:
                print('该账号已签到或重试超过5次，即将退出程序')
            driver.quit()
