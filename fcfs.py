import sys
import requests
import lzstring
import uuid
import rsa
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup

import time

def encrypt(naver_id, naver_pw):
    key_str = requests.get('https://nid.naver.com/login/ext/keys.nhn').content.decode("utf-8")
    sessionkey , Keyname, evalue, nvalue = key_str.split(',') 
    evalue, nvalue = int(evalue, 16), int(nvalue, 16)
    pubkey = rsa.PublicKey(evalue, nvalue)
    message = [sessionkey,naver_id,naver_pw]
    merge_message = ""
    for s in message:
        merge_message = merge_message + ''.join([chr(len(s)) + s])
    merge_message = merge_message.encode()
    encpw = rsa.encrypt(merge_message, pubkey).hex()
    return Keyname, encpw

def naver_login(nid, npw):
    print("[{}] START NAVER ACCOUNT LOGIN ".format(datetime.now()))
    encnm, encpw = encrypt(nid, npw)
    bvsd_uuid = uuid.uuid4()
    o = '{"a":"' + str(bvsd_uuid) + '","b":"1.3.4","h":"1f","i":{"a":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Whale/2.7.100.20 Safari/537.36"}}'  
    encData = lzstring.LZString.compressToEncodedURIComponent(o)
    bvsd = '{"uuid":"'+ str(bvsd_uuid) + '","encData":"'+ encData +'"}'
    session = requests.Session()
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Whale/2.7.100.20 Safari/537.36'
    }
    data = {
        'enctp': '1',
        'svctype': '0',
        'encnm': encnm,
        'locale' : 'ko_KR',
        'url': 'www.naver.com',
        'smart_level': '1',
        'encpw': encpw,
        'bvsd': bvsd
    }
    resp = session.post('https://nid.naver.com/nidlogin.login?url=http://m.naver.com/aside/', data=data, headers=headers)
    if(resp.text.find("location.replace")>-1):
        print("[{}] Login Successfully !!".format(datetime.now()))
        return session
    else:
        print("[{}] Login Fail ".format(datetime.now()))
        return False

def check_post(session, cafeid):
    print("[{}] CHECKING START .........".format(datetime.now()))
    post_url = 'https://apis.naver.com/cafe-web/cafe2/ArticleList.json'
    params = {
        'search.clubid' : cafeid,
        'search.queryType' : 'lastArticle',
        'search.boardtype' : 'L',
        'search.page' : 1
    }
    article_list = []

    while(True):
        res = session.get(post_url, params=params)
        jsondata = res.text
        f = False
        responseJson = json.loads(jsondata)
        post_list = responseJson.get("message").get("result").get('articleList')
        for post in post_list:
            if '□' in post['subject'] or '■' in post['subject']:
                arcid = post['articleId']
                if arcid not in article_list:
                    article_list.append(arcid)
                    print("[{}] I found a NEW related post. Title: {}".format(datetime.now(), post['subject']))
                    print("[{}] =========================== ".format(datetime.now()))
                    print("[{}] Title: {}".format(datetime.now(), post['subject']))
                    print("[{}] Article Id: {}".format(datetime.now(), arcid))
                    write_comment(session, arcid, cafeid)
                    print("[{}] I commented a related post.".format(datetime.now()))
                    print("[{}] =========================== ".format(datetime.now()))
                    f = True
                    time.sleep(2.5)
            else:
                pass
        if f:
            print("[{}] {}".format(datetime.now(), "Please check comment at cafe"))
            break
    return 0

def write_comment(session, arcid, cafeid):
    commet_url = 'https://apis.naver.com/cafe-web/cafe-mobile/CommentPost.json'
    formdata = {
        'cafeId' : cafeid,
        'articleId' : arcid,
        'content' : 'ppp'
    }
    commented = session.post(commet_url, data=formdata)
    print("[{}] {}".format(datetime.now(), commented.text))

def check_cafe(session, cafeid):
    get_url = 'https://m.cafe.naver.com/ca-fe/web/cafes/' + cafeid
    res = requests.get(get_url)
    soup = BeautifulSoup(res.content, 'html.parser')
    result = soup.find('title')
    print(result)
    #print(result.decode('utf-8'))


if __name__ == "__main__":
    print("""
    ╔════════════════════╗
    ║    ╔═╗╔═╗╔═╗╔═╗    ║
    ║    ╠╣ ║  ╠╣ ╚═╗    ║
    ║    ╚  ╚═╝╚  ╚═╝    ║
    ╚════════════════════╝ by.daekp
""")
    if len(sys.argv) > 5 or len(sys.argv) < 5:
        print("[{}] ERROR: Please check arguments".format(datetime.now()))
        print("[*] Usage")
        print("> fcfs.exe ID PW TIME")
        print("> example) fcfs.exe cafeid idididid pwpwpwpw 13:00:00")
        sys.exit()
    else:
        times = sys.argv[4].split(':')
        sched = BlockingScheduler()
        dt = datetime.now()
        run_date = datetime(dt.year, dt.month, dt.day, int(times[0]), int(times[1]), int(times[2]))
        if (run_date-dt).days < 0:
            print("[{}] ERROR: Can not run at a time prior to the current time.".format(dt))
            sys.exit()
        print("[{}] Running main process ".format(dt))
        print("[{}] Process will start after {} ".format(dt, run_date-dt))
        session = ''
        while True:
            dt = datetime.now()
            if (run_date-dt).seconds < 60:
                print("[{}] Process will start after {} ".format(dt, run_date - dt))
                session = naver_login(sys.argv[2], sys.argv[3])
                break

        if session != False:
            rdata = sched.add_job(check_post, 'date',
                                  run_date=run_date - timedelta(seconds=2),
                                  args=[session, sys.argv[1]])
            print('[{}] '.format(datetime.now()) + str(rdata))
            sched.start()
        else:
            print("[{}] ERROR: Please check login id/pw".format(dt))
            sys.exit()
