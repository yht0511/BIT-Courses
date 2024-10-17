import ddddocr
import os
import execjs
import base64

def get_captcha(img_path):
    # 创建一个ddddocr对象
    ocr = ddddocr.DdddOcr(show_ad=False)

    # 读取验证码图片的字节数据
    with open(img_path, 'rb') as f:
        img_bytes = f.read()

    # 使用ddddocr进行验证码识别
    result = ocr.classification(img_bytes)

    # 返回识别结果
    return result

def get_encoded_password(password):
    f=open("key.js",'r',encoding='utf-8')
    javascript=f.read()
    f.close()
    try:
        key=execjs.compile(javascript)
    except Exception as e:
        print(f"登录失败!请检查是否安装Node.js或者在settings.py中填写password_encoded项.")
    return base64.b64encode(key.call('strEnc',password).encode()).decode()
    