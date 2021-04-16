# -- coding: utf-8 --
#!/usr/bin/env python3
import json
import platform
import sys
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64encode


def autotip(title, msg):
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
    autotip('请先在 Login.txt 中输入登录信息！', 'From BHgwLoginTool By Hyw.')
    sys.exit()

s = f.read()
f.close()

index1 = s.find('{')
index2 = s.find('}')
index3 = s.find('{', index1 + 1)
index4 = s.find('}', index2 + 1)
u = s[index1 + 1:index2]
p = s[index3 + 1:index4].encode()
p = '{B}' + urllib.parse.quote(b64encode(p))
form = 'action=login&username=' + u + '&password=' + p + \
    '&ac_id=20&user_ip=&nas_ip=&user_mac=&save_me=1&ajax=1'
form = form.encode()
req = urllib.request.Request(
    url='https://gw.buaa.edu.cn:804/include/auth_action.php', data=form)
res = urllib.request.urlopen(req).read().decode('utf-8')

if res[:8] == 'login_ok':
    req = urllib.request.Request(
        url='https://gw.buaa.edu.cn:801/beihangview.php')
    res = urllib.request.urlopen(req).read().decode('utf-8')
    u = res.find('uid=')
    u1 = res.find('&', u + 1)
    uid = res[u + 4:u1]
    req = urllib.request.Request(
        'https://gw.buaa.edu.cn:801/beihang.php?route=getPackage&uid=' + uid +
        '&pid=1')
    res = urllib.request.urlopen(req).read().decode('utf-8')
    resj = json.loads(res)
    used = resj['acount_used_bytes']
    remain = resj['acount_remain_bytes']
    autotip("网络已连接！\n( 流量已用 " + used + ' , 剩余 ' + remain + ' )',
            'From BHgwLoginTool By Hyw.')
else:
    autotip('网络连接失败。', 'From BHgwLoginTool By Hyw.')
