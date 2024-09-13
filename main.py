import time
import xk
import json

def get_status():
    total=len(tasks)
    chosen=0
    for task in tasks:
        if task["status"]:
            chosen+=1
    return f"{chosen}/{total}"

# 登录
print("正在登录...")
xuanke=xk.XK()
print("读取任务...")

# 获取任务列表
tasks=json.load(open("tasks.json",'r',encoding='utf-8'))
# 更新任务信息
for task in tasks:
    t=xuanke.query(task["name"])
    task["id"]=t["teachingClassID"]
    task["name"]=t["courseName"]
    if "type" not in task:
        task["type"]="select"
    elif task["type"]=="replace":
        t1=xuanke.query(task["replace"]["name"])
        task["replace"]["id"]=t1["teachingClassID"]
        task["replace"]["name"]=t1["courseName"]
    task["status"]=False
open("tasks.json",'w',encoding='utf-8').write(json.dumps(tasks,ensure_ascii=False,indent=4))

print(f"初始化完毕,3s后开始抢课")
time.sleep(3)

print("\n***开始抢课***")

# 抢课
while True:
    lt=time.time()
    for task in tasks:
        if task["type"]=="select":
            res,j=xuanke.select(task["id"])
            if res or '已在' in j['msg']:
                print(f"填报 {task['name']} 成功 ",time.time())
                task["status"]=True
                open("tasks.json",'w',encoding='utf-8').write(json.dumps(tasks,ensure_ascii=False,indent=4))
        elif task["type"]=="replace":
            if xuanke.status(task["name"]):
                res,j=xuanke.unselect(task["replace"]["id"])
                if res:
                    print(f"退课 {task['name']} 成功 ",time.time())
                    res,j=xuanke.select(task["id"])
                    if res or '已在' in j['msg']:
                        print(f"填报 {task['replace']['name']} 成功 ",time.time())
                        task["status"]=True
                        open("tasks.json",'w',encoding='utf-8').write(json.dumps(tasks,ensure_ascii=False,indent=4))
                    else:
                        print(f"填报 {task['replace']['name']} 失败 ",time.time())
                        res,j=xuanke.select(task["replace"]["id"])
                        if res:
                            print(f"重新填报 {task['replace']['name']} 成功 ",time.time())
                        else:
                            print(f"重新填报 {task['replace']['name']} 失败 ",time.time())
                            task["type"]="select"
                            open("tasks.json",'w',encoding='utf-8').write(json.dumps(tasks,ensure_ascii=False,indent=4))
    print(f"抢课中... 时间:{format(time.time(), '.3f')} 频率:{format(1/(time.time()-lt), '.1f')}次/s 状态:{get_status()}            \r",end="")