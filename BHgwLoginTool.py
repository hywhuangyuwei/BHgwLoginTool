# -- coding: utf-8 --
from base64 import b64encode
from urllib import quote
import urllib2


import sys
import os
import time
import win32con
from win32api import *
from win32gui import *
reload(sys)
sys.setdefaultencoding('utf8')


class WindowsBalloonTip:
    def __init__(self, title, msg):
        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
        }
        # Register the Window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map  # could also specify a wndproc.
        classAtom = RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow(classAtom, "Taskbar", style,
                                 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                 0, 0, hinst, None)
        UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(
            os.path.join(sys.path[0], "balloontip.ico"))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            hicon = LoadImage(hinst, iconPathName,
                              win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY,
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER + 20,
                          hicon, "Balloon  tooltip", title, 200, msg))
        # self.show_balloon(title, msg)
        time.sleep(5)
        DestroyWindow(self.hwnd)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)  # Terminate the app.


def balloon_tip(title, msg):
    WindowsBalloonTip(msg, title)


try:
    f = open(u'Login.txt')
except:
    f = open(u'Login.txt', 'w')
    f.write(
        u'''#此文件用于保存登录信息

#用户名 = {123}
#密码 = {123}

#注：请在{  }中输入
'''
    )
    f.close()
    balloon_tip('请先在 Login.txt 中输入登录信息！'.encode('gbk'), 'From BHgwLoginTool By Hyw.')
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

logf = open('log.txt', 'a')
logf.write(res + '\n')
logf.close()

if res[:8] == 'login_ok':
    balloon_tip('网络已连接！'.encode('gbk'), 'From BHgwLoginTool By Hyw.')
else:
    balloon_tip('网络连接失败。（ 记录在 log.txt ）'.encode(
        'gbk'), 'From BHgwLoginTool By Hyw.')
