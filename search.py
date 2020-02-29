import re
import time
import subprocess
import threading
import requests
from lxml import html

import urllib3
urllib3.disable_warnings()

domain_list = [
    "http://kubozy.net/",
    "http://zy.kakazycj.com/",
    "http://www.kubozy.org/",
    "http://zycaiji.com/",
    "http://www.zxziyuan.com/",
    "http://api.kbzyapi.com/",
    "http://www.kuyunzyw.tv/",
    "http://www.kuyun.co/",
    "http://superpan.me/",
    "http://www.gxzyw.net/",
    "http://www.yongjiuzy1.com/",
    "http://www.yongjiuzy2.com/",
    "http://www.yongjiuzy3.com/",
    "http://www.yongjiuzy4.com/",
    "http://www.yongjiuzy5.com/",
    "http://yongjiuzy.vip/",
    "http://135zy0.com/",
    "http://www.okzyw.com/",
    "http://okzy.co/",
    "http://www.haozy.cc/",
    "http://www.okzyw.net/",
    "http://www.apiokzy.com/",
    "http://www.okp2pzy.com/",
    "http://zy.yswy.top/",
    "http://www.okokzy.net/",
    "http://www.okzyw.cc/",
    "https://okzy8.com/",
    "http://haku77.com/",
    "http://www.okzy10.com/",
    "http://www.okzy5.com/",
    "http://okzy1.com/",
    "http://www.zuidazy5.com/",
    "http://www.zuidazy1.com/",
    "http://135zy1.com/",
    "http://cj.135zy.co/",

    # "http://kuyunzy1.com/",
    # "http://www.kuyunzyw.vip/",
    # "http://kuyun9.com/",
    # "http://www.kuyunzy1.com/",

    # "http://ys1.xingyaox.com/",
    # "http://vip.xiaoheizaixian.com/",
    # "http://61166.net",
    # "http://www.btdytt8.net",
    # "http://www.panmanman.com/",
    # "https://xqzxwz.com/",
    # "http://v.hyage.com/",
]

domain_list = [
    "https://wolongzy.net/",
    "http://zy.bajieziyuan.com/",
    "http://www.mahuazy.net/",
    "http://zuidazy.net/",
    "http://www.156zy.cc/",
    # "http://kuyunzy.cc/",
    "http://www.haozy.cc/",
    "http://www.765zy.com/",
    # "http://www.kukuzy.com/",
    # "http://www.1977zy.com/",
    "http://zuikzy.cc/",
    "http://www.123ku.com/",
    "http://kankanzy.com/",
    "http://www.doubanzy.com/",
    "http://gaoqingzy.com/",
    "http://zuidazy2.com/",
    "http://www.subo8988.com/",
    "http://www.leduozy.com/",
    "http://yongjiuzy.cc/",
    "http://www.ziyuanpian.net/",
    "http://www.666zy.com/",
    "https://www.baiwanzy.com/",
    "http://www.wuxiou.com/",
    "http://www.bbkdj.com/",
    "http://niuniuzy.com/",
    # "http://www.398zy.com/",
    "http://www.czhiziyuan.com/",
    "http://kubozy.net/",
    # "http://chaojizy.com/",
    "https://www.mb700.com/",
    "http://www.zuixinzy.cc/",
    "https://www.solezy.com/",
    "https://mokazy.com/",
    "http://265zy.cc/",
    # "http://www.88zyw.net/",
    # "http://www.mp4ba.cc/",
    # "http://www.agenya.cn/",
    "http://zy.ataoju.com/",
    "http://zy.itono.cn/",
    # "https://zy.nmbaojie.com/",
    # "http://www.ttzy.cc/",
    # "http://www.ckzy.cc/",
    "http://www.156zy.me/",
]
# for d in domain_list:
#     _ = requests.get(d).url
#     if _ != d:
#         print(d, _)
#     else:
#         print(d, True)
# input()

print("Keyword: ", end="")
keyword = input()
if keyword == "":
    # keyword = "女皇之刃"
    keyword = "猫娘乐园"
error_list = []
result_list = {}
ps = []
sema = threading.Semaphore(value=2**4)
for _i, domain in enumerate(domain_list):
    def job(_i, domain):
        try:
            sema.acquire()
            start = time.time()
            # if domain != "http://kankanzy.com/":
            #     continue
            url = domain+"index.php?m=vod-search"
            data = {
                "wd": keyword,
                "submit": "search"
            }
            try:
                r = requests.post(url, data)
            except:
                error_list.append(domain)
                raise Exception
            if r.status_code == 404:
                error_list.append(domain)
                raise Exception
            r = r.content.decode()
            # print(url, data, r)
            # input()
            r = html.fromstring(r)
            result = r.xpath("//div[@class='xing_vb']/ul")[1:-1]
            if len(result) == 0:
                raise Exception
            # print(domain+"\t\t"+str(len(result)))
            for r in result:
                # title = r.xpath(".//span[@class='xing_vb4']/a/text()")[0].strip()
                url = r.xpath(".//span[@class='xing_vb4']/a/@href")[0]
                url = domain+url
                url = url.replace("//?", "/?")
                r = requests.get(url).content.decode()
                title = re.search(r"<h2>(.*?)<\/h2>", r)[1]
                title = re.sub(r"<.*?>", "", title)
                m3u8s = re.findall(r"\"(http.*?m3u8)\"", r)
                try:
                    verify = True
                    if "s1.jxtvsb.com" in m3u8s[0]:
                        # print(m3u8s[0])
                        verify = False
                    check = requests.get(m3u8s[0], verify=verify).status_code
                except:
                    check = 404
                if check != 200:
                    # print(title+"\t\t"+str(check), url)
                    continue
                title_key = title+f"[{len(m3u8s)}]"
                if title_key not in result_list:
                    result_list[title_key] = []
                result_list[title_key].append(url)
                # print("\t"+title+"\t\t"+url)
            # print()
            print(f"\rProgress: {_i+1}/{len(domain_list)}\n", end="", flush=True)
        except:
            pass
        finally:
            sema.release()

    p = threading.Thread(target=job, args=(_i, domain))
    ps.append(p)
    p.start()
for p in ps:
    p.join()
print()
# for k, v in result_list.items():
#     print(k, v)
# print("error_list", error_list)
for _i, k in enumerate(result_list.keys()):
    print(f"{_i+1}: {k}", result_list[k])
print("\nEnter Choice: ", end="")
choices = input().split()
# print(choices)
urls = []
for choice in choices:
    k = list(result_list.keys())[int(choice)-1]
    urls += result_list[k]
    # print(result_list[k])
cmd = f'download.py "{urls[0]}"'
# print(cmd)
subprocess.run(cmd, shell=True)
