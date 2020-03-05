import os
import requests
import re
import sys
import threading
import subprocess
import shutil

import urllib3
urllib3.disable_warnings()

try:
    sema = threading.Semaphore(value=2**6)
    _dldir = r"Z:\www\stream"
    if len(sys.argv) == 1:
        print("Enter URI: ", end="")
        _ins = input()
        if _ins == "":
            _ins = ["http://www.kubozy.net/?m=vod-detail-id-9875.html"]
            # _ins = ["http://www.okp2pzy.com/?m=vod-detail-id-24095.html"]
        else:
            _ins = [_ins]
    else:
        _ins = sys.argv[1:]
    for _in in _ins:
        dldir = _dldir
        print(_in)
        r = requests.get(_in).content.decode()
        title = re.search(r"<h2>(.*?)<\/h2>", r)[1]
        title = re.sub(r"<.*?>", "", title)
        m3u8s = re.findall(r"\$(http.*?m3u8)<", r)
        print(title)
        dldir += f"\\{title}\\"
        print("\t"+dldir)
        i = 0
        m3u8s = sorted(set(m3u8s), key=m3u8s.index)
        for m3u8 in m3u8s:
            i += 1
            dir = dldir+str(i).zfill(5)
            fn = dir+".ts"
            print("\t\t"+fn)
            verify = True
            if "s1.jxtvsb.com" in m3u8:
                verify = False
            r = requests.get(m3u8, verify=verify).content.decode()
            m3u8_org = r
            if ".ts" not in r:
                r = re.sub(r"\n$", "", r).split("\n")
                if not r[-1].endswith("index.m3u8"):
                    if r[0] != "#EXTM3U":
                        raise Exception("no m3u8 found", m3u8, r)
                if not r[-1].startswith("/"):
                    m3u8 = m3u8.replace("index.m3u8", r[-1])
                else:
                    m3u8 = re.search(r".*?(?:\:\/\/).*?\/", m3u8)[0]+r[-1][1:]
                r = requests.get(m3u8).content
                # open(dir+".m3u8", "wb").write(r)
                m3u8_org = r.decode()
                r = r.decode().split("\n")
            else:
                r = re.sub(r"\n$", "", r).split("\n")
            r = [_ for _ in r if not _.startswith("#") and _.endswith(".ts")]
            try:
                os.makedirs(dir)
            except:
                pass
            ps = []
            prefix = -1
            for _ in r:
                def job(_, p):
                    global m3u8_org
                    link = _
                    tmp = ""
                    try:
                        sema.acquire()
                        m3u8_org = m3u8_org.replace(_, f"{str(p).zfill(5)}.ts")
                        if "://" in _:
                            link = _
                        elif not _.startswith("/"):
                            link = m3u8.replace("index.m3u8", _)
                        else:
                            link = re.search(r".*?(?:\:\/\/).*?\/", m3u8)[0]+_[1:]
                            _ = re.search(r".*\/(.*?)$", _)[1]
                        tmp = rf"{dir}\{str(p).zfill(5)}.ts"
                        verify = True
                        if "s1.jxtvsb.com" in link:
                            verify = False
                        _r_ = requests.get(link, verify=verify, timeout=20)
                        # print(p, _r_.status_code, flush=True)
                        # print(p, "", end="", flush=True)
                        open(tmp, "wb").write(_r_.content)
                    except Exception as e:
                        # sys.stderr.write(f"{_in} {m3u8} {tmp} {link}\n")
                        open(f"error.{title}.log", "ab").write(f"{tmp} {link}\n".encode())
                        # print(e)
                    finally:
                        sema.release()

                prefix += 1
                p = threading.Thread(target=job, args=(_, prefix))
                ps.append(p)
                p.start()
            for p in ps:
                p.join()
            open(dir+"\\index.m3u8", "wb").write(m3u8_org.encode())
            # cmd = rf'''copy /b "{dir}\*.ts" "{fn}"'''
            # print("\t\t\t"+cmd)
            # subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            # shutil.rmtree(dir)
            # break
except Exception as e:
    print(e)
    input()
exit()



# source: http://www.pakinfotv.com/vodplay/60622-4-12.html
# http://80ysm.com/v/api.php?url=
# http://api.69ne.com/index.php?url=
