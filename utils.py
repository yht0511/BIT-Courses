import ddddocr


def get_captcha(img_path):
    # 创建一个ddddocr对象
    ocr = ddddocr.DdddOcr(show_ad=False)

    # 读取验证码图片的字节数据
    with open(img_path, 'rb') as f:
        img_bytes = f.read()

    # 使用ddddocr进行验证码识别
    result = ocr.classification(img_bytes).upper()

    # 返回识别结果
    return result
