import json
import os
import platform
import ssl
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request as Request
from urllib.request import urlopen as urlopen

ssl._create_default_https_context = ssl._create_unverified_context


def getChallengeUrl(username):
    challengeUrl = 'https://gw.buaa.edu.cn/cgi-bin/get_challenge?callback=jQuery1124040520953767391155_4059734400000&username={0}'.format(
        username)
    return challengeUrl


def getSrunPortalUrl(params):
    queryStr = urlencode(params)
    return 'https://gw.buaa.edu.cn/cgi-bin/srun_portal?' + queryStr


def JSONstringify(username, password, ip):
    res = '{"username":"%s","password":"%s","ip":"%s","acid":"1","enc_ver":"srun_bx1"}' % (
        username, password, ip)
    return res


def popUpNotification(title, msg):
    if platform.system() == 'Windows':
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, msg, icon_path='./src/BHgwLoginTool.ico')

    if platform.system() == 'Linux':
        import notify2
        notify2.init('BHgwLoginTool')
        n = notify2.Notification(title, msg)
        n.show()

    if platform.system() == 'Darwin':
        from subprocess import call
        cmd = 'display notification \"' + \
            msg + '\" with title \"' + title + '\"'
        call(["osascript", "-e", cmd])


try:
    f = open('Login.txt', encoding='utf-8')
except IOError:
    f = open('Login.txt', 'w', encoding='utf-8')
    f.write('''#此文件用于保存登录信息

#用户名 = {123}
#密码 = {123}

#注：请在{  }中输入
''')
    f.close()
    popUpNotification('请先在 Login.txt 中输入登录信息！', 'From BHgwLoginTool By Hyw.')
    sys.exit(0)
s = f.read()
f.close()
index1 = s.find('{')
index2 = s.find('}')
index3 = s.find('{', index1 + 1)
index4 = s.find('}', index2 + 1)
username = s[index1 + 1:index2]
password = s[index3 + 1:index4]

challengeUrl = getChallengeUrl(username)
myReq = Request(url=challengeUrl, method='GET')
myReq.add_header(
    'User-Agent',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Safari/605.1.15'
)
response = urlopen(myReq).read().decode('utf-8')
token = str(eval(response[43:-1])["challenge"])
ip = str(eval(response[43:-1])["client_ip"])
JSONstringified = JSONstringify(username, password, ip)

# i = info(JSONstringified, token)
i = os.popen("info.exe %s %s" %
             (JSONstringified.replace('"', '"""'), token)).read().strip()

# hmd5 = md5(password, token)
hmd5 = os.popen("md5.exe %s %s" % (password, token)).read().strip()

chkstr = token + username
chkstr += token + hmd5
chkstr += token + '1'
chkstr += token + ip
chkstr += token + '200'
chkstr += token + '1'
chkstr += token + i

# chksum = sha1(chkstr)
chksum = os.popen("sha1.exe %s" % (chkstr, )).read().strip()

utc = int(time.time() * 1000)
params = {
    'callback': 'jQuery1124040520953767391155_4059734400000',
    'action': 'login',
    'username': str(username),
    'password': "{MD5}" + str(hmd5),
    'ac_id': '1',
    'ip': str(ip),
    'chksum': str(chksum),
    'info': str(i),
    'n': '200',
    'type': '1',
    'os': platform.system(),
    'name': 'Macintosh',
    'double_stack': '0',
    '_': str(utc)
}
srunPortalUrl = getSrunPortalUrl(params)

myReq1 = Request(url=srunPortalUrl, method='GET')
myReq1.add_header(
    'User-Agent',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Safari/605.1.15'
)
myReq1.add_header(
    'Accept',
    'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01'
)
response = urlopen(myReq1).read().decode('utf-8')[response.index('(') + 1:-1]
responseJSON = json.loads(response)

title = ''
msg = ''
if responseJSON['res'] == 'ok':
    title = '登录成功'
    msg = '信息：' + responseJSON['suc_msg']
else:
    title = '登录失败'
    msg = '信息：' + responseJSON['error']
popUpNotification(title, msg)
