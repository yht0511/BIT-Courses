import json
import sys
import threading
import time
import requests
from rich import print
import settings
import utils
import webvpn

class XK():
    def __init__(self):
        self.ticket = webvpn.login(settings.student_code,settings.password).split("wengine_vpn_ticketwebvpn_bit_edu_cn=")[1].split(";")[0]
        print(f"获取到ticket:{self.ticket}")
        self.cookies = {
            'wengine_vpn_ticketwebvpn_bit_edu_cn': self.ticket,
            'show_vpn': '0',
            'show_faq': '1',
            'refresh': '1',
        }

        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Pragma': 'no-cache',
            'Referer': settings.URL+"/xsxkapp/sys/xsxkapp/*default/index.do",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
            'X-KL-Ajax-Request': 'Ajax_Request',
            'X-Requested-With': 'XMLHttpRequest',
            'language': 'zh_cn',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.headers["token"]=self.refresh_token()
        if not settings.elective_batch_code:
            codes=self.get_elective_batch_codes()
            settings.elective_batch_code=codes[0]["code"]
            print(f"未填写选课轮次,已自动选择:{codes[0]['name']}")
        
        # 自动刷新
        self.auto_refresh_token_thread=threading.Thread(target=self.auto_refresh_token)
        self.auto_refresh_token_thread.daemon=True
        self.auto_refresh_token_thread.start()

    def auto_refresh_token(self):
        """自动刷新token
        """
        while True:
            time.sleep(settings.refresh_token_interval)
            print("自动刷新token中...")
            self.headers["token"]=self.refresh_token()
        
    def refresh_token(self):
        self.send_input(settings.student_code)
        vtoken,captcha=self.get_captcha()
        response = requests.get(f'{settings.URL}/xsxkapp/sys/xsxkapp/student/check/login.do?vpn-12-o2-xk.bit.edu.cn\
                                &timestrap={int(time.time()*1000)}\
                                &loginName={settings.student_code}\
                                &loginPwd={settings.password_encoded if settings.password_encoded else utils.get_encoded_password(settings.password)}\
                                &verifyCode={captcha}\
                                &vtoken={vtoken}'.replace(" ",""),
                                headers=self.headers, cookies=self.cookies)
        if "message" in response.json() and "过期" in response.json()['message']:
            print("WEBVPN会话已过期,请重新登录")
            sys.exit(0)
        if int(response.json()['code'])!=1:
            print(f"登录失败!错误信息:{response.json()['msg']}")
            print("重试中...")
            # raise Exception("登录失败")
            return self.refresh_token()
        self.name=response.json()["data"]["name"]
        self.token=response.json()["data"]["token"]
        print(f"登录成功,姓名:{self.name},token:{self.token}")
        return self.token
    
    def send_input(self,text):
        data={
            "name": "",
            "type": "text",
            "value": text
        }
        response = requests.post(settings.Input_URL, cookies=self.cookies, headers=self.headers, data=data)
        return
        
    def get_captcha(self):
        """获取验证码

        Returns:
            str: 验证码vtoken
            str: 验证码
        """
        vtoken,path=self.get_captcha_img()
        captcha=utils.get_captcha(path).upper()
        self.send_input(captcha)
        return vtoken,captcha
    
    def get_captcha_img(self):
        """获取验证码图片

        Returns:
            str: 验证码vtoken
            str: 验证码文件路径
        """
        ct=self.get_capthcha_token()
        url=f"{settings.URL}/xsxkapp/sys/xsxkapp/student/vcode/image.do?vpn-1&vtoken={ct}"
        # 下载到本地
        with open('captcha.jpg', 'wb') as f:
            f.write(requests.get(url, cookies=self.cookies, headers=self.headers).content)
        return ct,'captcha.jpg'
        
        
    def get_capthcha_token(self):
        """获取验证码token
        
        Returns:
            str: 验证码token
        """
        response = requests.get(f'{settings.URL}/xsxkapp/sys/xsxkapp/student/4/vcode.do?vpn-12-o2-xk.bit.edu.cn&timestamp={int(time.time()*1000)}', cookies=self.cookies, headers=self.headers)
        if 'data' not in response.json():
            raise Exception("用户名或密码错误.")
        return response.json()['data']['token']
    
    def get_elective_batch_codes(self):
        response = requests.get(f'{settings.URL}/xsxkapp/sys/xsxkapp/elective/batch.do?vpn-12-o2-xk.bit.edu.cn&timestamp={int(time.time()*1000)}', cookies=self.cookies, headers=self.headers)
        return response.json()["dataList"]
    
    def list_GX(self,page=0,ans=[],text="",type="XGXK",only_first=False):
        """列出所有公选课

        Args:
            page (int, optional): 第几页. Defaults to 1.
            ans (list, optional): 返回结果. Defaults to [].

        Returns:
            list: 公选课信息
        """
        data = {
            'querySetting': json.dumps({"data":
                {"studentCode":settings.student_code,
                 "campus":"2",
                 "electiveBatchCode":settings.elective_batch_code,
                 "isMajor":"1",
                 "teachingClassType":type,
                 "checkConflict":"2",
                 "checkCapacity":"2",
                 "queryContent":text
                 },
                "pageSize":"100" if not only_first else "10",
                "pageNumber":str(page),
                "order":""
                }),
        }

        response = requests.post(f'{settings.URL}/xsxkapp/sys/xsxkapp/elective/publicCourse.do?vpn-12-o2-xk.bit.edu.cn', cookies=self.cookies, headers=self.headers, data=data)
        
        if ('msg' in response.json() and "登陆信息" in response.json()['msg']) or 'dataList' not in response.json():
            self.headers["token"]=self.refresh_token()
            return self.list_GX(page,ans,text,type)
        
        if len(response.json()['dataList'])==0:
            return ans
        ans+=response.json()['dataList']
        if only_first:
            return ans
        return self.list_GX(page+1,ans,text,type)
     
    def list_all(self,page=0,ans=[],text="",only_first=False):
        """列出全校课表

        Args:
            page (int, optional): 第几页. Defaults to 1.
            ans (list, optional): 返回结果. Defaults to [].

        Returns:
            list: 课程信息
        """
        data = {
            'querySetting': json.dumps({"data":
                {"studentCode":settings.student_code,
                 "campus":"2",
                 "electiveBatchCode":settings.elective_batch_code,
                 "isMajor":"1",
                 "teachingClassType":"QXKC",
                 "checkConflict":"2",
                 "checkCapacity":"2",
                 "queryContent":text
                 },
                "pageSize":"100",
                "pageNumber":str(page),
                "order":""
                }),
        }

        response = requests.post(f'{settings.URL}/xsxkapp/sys/xsxkapp/elective/queryCourse.do?vpn-12-o2-xk.bit.edu.cn', cookies=self.cookies, headers=self.headers, data=data)
        if len(response.json()['dataList'])==0:
            return ans
        ans+=response.json()['dataList']
        if only_first:
            return ans
        return self.list_all(page+1,ans,text)
    
    def query(self,name):
        """获取公选课信息

        Args:
            name (str): 课程名

        Returns:
            dict: 公选课信息
        """
        res=self.list_GX(text=name,only_first=True)
        if not res:
            raise Exception(f"未找到课程:{name}")
        return res[0]
    
    def status(self,name):
        """查询是否有空位

        Args:
            name (str): 课程名

        Returns:
            bool: 是否有空位
        """
        c=self.query(name)
        if c['numberOfSelected']<c['classCapacity']:
            return True
        return False
    
    def select(self,classId):
        """选课

        Args:
            classId (str): 课程ID

        Returns:
            bool: 是否选上
            dict: 返回信息
        """
        data = {
            'addParam': json.dumps({"data":
                    {
                        "operationType":"1",
                        "studentCode":settings.student_code,
                        "electiveBatchCode":settings.elective_batch_code,
                        "teachingClassId":classId,
                        "isMajor":"1",
                        "campus":"2",
                        "teachingClassType":"XGXK"
                    }
                }),
        }
        response = requests.post(f'{settings.URL}/xsxkapp/sys/xsxkapp/elective/volunteer.do?vpn-12-o2-xk.bit.edu.cn', cookies=self.cookies, headers=self.headers, data=data)
        if "成功" in response.json()['msg']:
            return True, response.json()
        
        if 'msg' in response.json() and "未查询到登陆信息" in response.json()['msg']:
            self.headers["token"]=self.refresh_token()
        
        return False, response.json()
    
    def unselect(self,classId):
        """取消选课

        Args:
            classId (id): 课程唯一id

        Returns:
            bool: 是否成功
            dict: 返回信息
        """
        params={
            "timestamp": int(time.time()*1000),
            "deleteParam": json.dumps({"data":
                {   
                    "operationType":"2",
                    "studentCode":settings.student_code,
                    "electiveBatchCode":settings.elective_batch_code,
                    "teachingClassId":classId,
                    "isMajor":"1"
                    }
                })
        }
        response = requests.get(f'{settings.URL}/xsxkapp/sys/xsxkapp/elective/deleteVolunteer.do?vpn-12-o2-xk.bit.edu.cn',params=params, cookies=self.cookies, headers=self.headers)
        if "成功" in response.json()['msg']:
            return True,response.json()
        return False,response.json()