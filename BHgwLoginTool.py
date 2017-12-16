# -- coding: utf-8 --
from base64 import b64encode
from urllib import quote
import urllib2
import os
import sys
import time
import json
import platform


# Windows
import win32con
import win32gui
reload(sys)
sys.setdefaultencoding('utf8')


class WindowsBalloonTip:
    def __init__(self, title, msg):
        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32gui.GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map  # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(classAtom, "Taskbar", style,
                                          0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                          0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "tooltip")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                                  (self.hwnd, 0, win32gui.NIF_INFO, win32con.WM_USER + 20,
                                   hicon, "Balloon  tooltip", title, 200, msg))
        # self.show_balloon(title, msg)
        time.sleep(5)
        win32gui.DestroyWindow(self.hwnd)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)  # Terminate the app.


def balloon_tip(title, msg):
    WindowsBalloonTip(msg, title)
#####


# Linux
if platform.system() == 'Linux':
    import notify2
    notify2.init('BHgwLoginTool')
#####


def autotip(title, msg):
    if platform.system() == 'Windows':
        balloon_tip(title.encode('gbk'), msg)
    elif platform.system() == 'Linux':
        n = notify2.Notification(title, msg)
        n.show()


try:
    f = open(u'Login.txt')
except IOError:
    f = open(u'Login.txt', 'w')
    f.write(
        u'''#此文件用于保存登录信息

#用户名 = {123}
#密码 = {123}

#注：请在{  }中输入
'''
    )
    f.close()
    autotip('请先在 Login.txt 中输入登录信息！', 'From BHgwLoginTool By Hyw.')
    os._exit()

s = f.read()
f.close()

index1 = s.find('{')
index2 = s.find('}')
index3 = s.find('{', index1 + 1)
index4 = s.find('}', index2 + 1)
u = s[index1 + 1:index2]
p = s[index3 + 1:index4]
p = '{B}' + quote(b64encode(p))
form = 'action=login&username=' + u + '&password=' + p + \
    '&ac_id=20&user_ip=&nas_ip=&user_mac=&save_me=1&ajax=1'
req = urllib2.Request(
    url='https://gw.buaa.edu.cn:804/include/auth_action.php', data=form)
res = urllib2.urlopen(req).read()

# logf = open('log.txt', 'a')
# logf.write(res + '\n')
# logf.close()

if res[:8] == 'login_ok':
    req = urllib2.Request(url='https://gw.buaa.edu.cn:801/beihangview.php')
    res = urllib2.urlopen(req).read()
    u = res.find('uid=')
    u1 = res.find('&', u + 1)
    uid = res[u + 4:u1]
    req = urllib2.Request(
        'https://gw.buaa.edu.cn:801/beihang.php?route=getPackage&uid=' + uid + '&pid=1')
    res = urllib2.urlopen(req).read()
    resj = json.loads(res)
    used = resj['acount_used_bytes']
    remain = resj['acount_remain_bytes']

    autotip("网络已连接！\n( 流量已用 " + used + ' , 剩余 ' + remain + ' )',
            'From BHgwLoginTool By Hyw.')
else:
    autotip('网络连接失败。', 'From BHgwLoginTool By Hyw.')
