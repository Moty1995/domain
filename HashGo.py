# -*- coding:gbk -*-

import wx  # wxPython可视化编程
import hashlib  # 哈希值计算
import os
import time  # 时间获取
import gevent.pool  # 协程池
import gevent.monkey  # 高效协程
import csv  # CSV文件读写
import itertools  # 操作迭代对象
import os.path  # 路径获取
import PIL  # 图片处理
import imagehash  # 感知哈希计算


###############################################################################
# 功能函数

# 函数功能：获取所读文件的哈希值
def GetHash(file_path):
    f = open(file_path, 'rb')
    if hashType.GetCurrentSelection() == -1 or hashType.GetCurrentSelection() == 0:
        hash_obj = hashlib.md5()
    elif hashType.GetCurrentSelection() == 1:
        hash_obj = hashlib.sha1()
    elif hashType.GetCurrentSelection() == 2:
        hash_obj = hashlib.sha256()
    elif hashType.GetCurrentSelection() == 3:
        hash_obj = hashlib.sha512()
    while True:
        d = f.read(8096)  # 数据分块读取，防止大文件哈希值计算错误
        if not d:
            break
        hash_obj.update(d)
    hash_code = hash_obj.hexdigest()
    f.close()
    hash = str(hash_code).lower()
    return hash


# 函数功能：遍历匹配表，查找是否有相同哈希的文件
def Match(hash):
    for i in CSVReader(matchListPath.GetValue()):
        if hash == i[1]:  # i[1]是匹配表哈希值所在列
            return 'Success'
    return 'Fail'


# 函数功能：获取文件属性
def GetStat(file_path):
    statinfo = os.stat(file_path)
    name = os.path.basename(file_path)
    mode = statinfo.st_mode
    ino = statinfo.st_ino
    dev = statinfo.st_dev
    uid = statinfo.st_uid
    gid = statinfo.st_gid
    size = statinfo.st_size
    atime = time.ctime(statinfo.st_atime)
    mtime = time.ctime(statinfo.st_mtime)
    ctime = time.ctime(statinfo.st_ctime)
    hash = GetHash(file_path)
    contents.AppendText(name + '\n' + hash + '\n\n')
    if matchListPath.GetValue() == '':
        return (name, file_path, mode, ino, dev, uid, gid, size, atime, mtime, ctime, hash)
    else:
        match = Match(hash)
        return (name, file_path, mode, ino, dev, uid, gid, size, atime, mtime, ctime, hash, match)


# 函数功能：保存结果为CSV格式
def CSVWriter(result):
    csvfile = open('HASH.csv', 'w', newline='')  # 默认文件名
    writer = csv.writer(csvfile)
    if hashType.GetCurrentSelection() == -1 or hashType.GetCurrentSelection() == 0:
        hashTypeStr = 'MD5'
    elif hashType.GetCurrentSelection() == 1:
        hashTypeStr = 'SHA1'
    elif hashType.GetCurrentSelection() == 2:
        hashTypeStr = 'SHA256'
    elif hashType.GetCurrentSelection() == 3:
        hashTypeStr = 'SHA512'
    if matchListPath.GetValue() == '':
        writer.writerow(('name', 'file_path', 'mode', 'ino', 'dev', 'uid', 'gid', 'size(B)', 'atime', 'mtime', 'ctime', hashTypeStr))
    else:
        writer.writerow(('name', 'file_path', 'mode', 'ino', 'dev', 'uid', 'gid', 'size(B)', 'atime', 'mtime', 'ctime', hashTypeStr, 'match'))
    writer.writerows(result)
    csvfile.close()


# 函数功能：读取匹配表
def CSVReader(list_path):
    content = []
    csvfile = open(list_path, 'r', newline='')  # 设置newline，否则两行之间会空一行
    csvReader = csv.reader(csvfile)
    for i in csvReader:
        content.append(i)
    return content


# 函数功能：获取生成密码的哈希值
def GetHash_RB(salt, password):
    if hashType2.GetCurrentSelection() == -1 or hashType2.GetCurrentSelection() == 0:
        hash_obj = hashlib.md5()
    elif hashType2.GetCurrentSelection() == 1:
        hash_obj = hashlib.sha1()
    elif hashType2.GetCurrentSelection() == 2:
        hash_obj = hashlib.sha256()
    elif hashType2.GetCurrentSelection() == 3:
        hash_obj = hashlib.sha512()
    hash_obj.update((salt + password).encode('utf-8'))  # 必须转换编码才能写入hashlib
    hash_code = hash_obj.hexdigest()
    hash = str(hash_code).lower()
    contents2.AppendText(password + '\t' + hash + '\n')
    return salt, password, hash


# 函数功能：保存结果为CSV格式
def CSVWriter_RB(keyList):
    if hashType2.GetCurrentSelection() == -1 or hashType2.GetCurrentSelection() == 0:
        hashTypeStr2 = 'MD5'
    elif hashType2.GetCurrentSelection() == 1:
        hashTypeStr2 = 'SHA1'
    elif hashType2.GetCurrentSelection() == 2:
        hashTypeStr2 = 'SHA256'
    elif hashType2.GetCurrentSelection() == 3:
        hashTypeStr2 = 'SHA512'
    csvfile = open('RainbowTable.csv', 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(('Salt', 'Password', hashTypeStr2))
    writer.writerows(keyList)
    csvfile.close()


# 函数功能：遍历字符串查找重复项
def isUnique(str):
    a = list(str)
    n = len(a)
    for i in range(n):
        if str.count(a[i]) != 1:
            return False
    return True


# 函数功能：获取图像哈希
def GetImageHash(path1, path2):
    if PHAType.GetCurrentSelection() == -1 or PHAType.GetCurrentSelection() == 0:
        hash1 = imagehash.average_hash(PIL.Image.open(path1))
        hash2 = imagehash.average_hash(PIL.Image.open(path2))
    elif PHAType.GetCurrentSelection() == 1:
        hash1 = imagehash.phash(PIL.Image.open(path1))
        hash2 = imagehash.phash(PIL.Image.open(path2))
    elif PHAType.GetCurrentSelection() == 2:
        hash1 = imagehash.dhash(PIL.Image.open(path1))
        hash2 = imagehash.dhash(PIL.Image.open(path2))
    elif PHAType.GetCurrentSelection() == 3:
        hash1 = imagehash.whash(PIL.Image.open(path1))
        hash2 = imagehash.whash(PIL.Image.open(path2))
    return hash1, hash2


###############################################################################
# 布局函数

# 函数功能：文件夹选择
def OpenDir(event):
    dlg = wx.DirDialog(None, message="Select evidence folder", style=wx.DD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        dirPath.SetValue(dlg.GetPath())  # 文件夹路径
    dlg.Destroy()


# 函数功能：文件选择
def OpenMatch(event):
    wildcard = "CSV files (*.csv)|*.csv|" \
               "All files (*.*)|*.*"
    dlg = wx.FileDialog(None, message="Select match list",
                        defaultDir=os.getcwd(),
                        defaultFile="",
                        wildcard=wildcard,
                        style=wx.FD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        matchListPath.SetValue(dlg.GetPath())  # 文件路径
    dlg.Destroy()


# 函数功能：图片选择
def OpenImage1(event):
    wildcard = "JPG files (*.jpg)|*.jpg|" \
               "PNG files (*.png)|*.png|" \
               "All files (*.*)|*.*"
    dlg = wx.FileDialog(None, message="Select image",
                        defaultDir=os.getcwd(),
                        defaultFile="",
                        wildcard=wildcard,
                        style=wx.FD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        imgPath1.SetValue(dlg.GetPath())  # 文件路径
    dlg.Destroy()


def OpenImage2(event):
    wildcard = "JPG files (*.jpg)|*.jpg|" \
               "PNG files (*.png)|*.png|" \
               "All files (*.*)|*.*"
    dlg = wx.FileDialog(None, message="Select image",
                        defaultDir=os.getcwd(),
                        defaultFile="",
                        wildcard=wildcard,
                        style=wx.FD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        imgPath2.SetValue(dlg.GetPath())  # 文件路径
    dlg.Destroy()


# 函数功能：哈希固定器确认键响应
def Confirm(event):
    if dirPath.GetValue().upper() == 'RB':
        win.Destroy()
        win2.Center()
        win2.Show()
    elif dirPath.GetValue().upper() == 'PH':
        win.Destroy()
        win3.Center()
        win3.Show()
    elif dirPath.GetValue() == '' or not os.path.isdir(dirPath.GetValue()):
        wx.MessageBox("Please select the right folder！", "Warning", wx.OK | wx.ICON_WARNING)
        return
    else:
        if matchListPath.GetValue() != '' and not os.path.isfile(matchListPath.GetValue()):
            wx.MessageBox("Please select the right match list！", "Warning", wx.OK | wx.ICON_WARNING)
            return
        contents.AppendText("Mission start!\n\n")
        startTime = time.time()
        filespath = []
        for root, dirs, files in os.walk(dirPath.GetValue()):
            for file in files:
                filepath = os.path.join(root, file)
                filespath.append(filepath)
        corePool = gevent.pool.Pool(8)
        results = corePool.map(GetStat, filespath)
        CSVWriter(results)
        endTime = time.time()
        usedTime = endTime - startTime
        contents.AppendText('Time： ' + str(usedTime) + ' s\n')
        contents.AppendText("Mission complete! Please check Hash.csv\n\n")


# 函数功能：彩虹表生成器确认键响应
def Confirm_RB(event):
    if characters.GetValue() == '':
        wx.MessageBox("Please input the characters in the password！", "Warning", wx.OK | wx.ICON_WARNING)
        return
    elif not isUnique(characters.GetValue()):
        wx.MessageBox("Character repeat！", "Warning", wx.OK | wx.ICON_WARNING)
        return
    pwList = []
    keyList = []
    if low.GetValue() == '' or high.GetValue() == '':
        wx.MessageBox("Please input the length of the password！", "Warning", wx.OK | wx.ICON_WARNING)
        return
    if low.GetValue() < high.GetValue():
        contents2.AppendText("Mission start!\n\n")
        startTime = time.time()
        for r in range(int(low.GetValue()), int(high.GetValue()) + 1):
            for i in itertools.product(characters.GetValue(), repeat=r):
                pwList.append(''.join(i))
    elif low.GetValue() == high.GetValue():
        contents2.AppendText("Mission start!\n\n")
        startTime = time.time()
        for i in itertools.product(characters.GetValue(), repeat=int(low.GetValue())):
            pwList.append(''.join(i))
    elif low.GetValue() > high.GetValue():
        wx.MessageBox("Please input the right length of the password！", "Warning", wx.OK | wx.ICON_WARNING)
        return
    for password in pwList:
        keyList.append(GetHash_RB(salt.GetValue(), password))
    CSVWriter_RB(keyList)
    endTime = time.time()
    usedTime = endTime - startTime
    contents2.AppendText('\nTime： ' + str(usedTime) + ' s\n')
    contents2.AppendText('Password number： ' + str(len(pwList)) + '\n')
    contents2.AppendText("Mission complete! Please check RainbowTable.csv\n\n")


# 函数功能：图片对比确认键响应
def Confirm_PHA(event):
    if imgPath1.GetValue() == '' or imgPath2.GetValue() == '' or not os.path.isfile(imgPath1.GetValue()) or not os.path.isfile(imgPath2.GetValue()):
        wx.MessageBox("Please select the right images！", "Warning", wx.OK | wx.ICON_WARNING)
        return
    hash1, hash2 = GetImageHash(imgPath1.GetValue(), imgPath2.GetValue())
    dValue = hash1 - hash2
    contents3.AppendText("PHA of Image A： " + str(hash1) + '\n')
    contents3.AppendText("PHA of Image B： " + str(hash2) + '\n')
    contents3.AppendText("PHA Difference： " + str(dValue) + '\n')
    if dValue == 0:
        contents3.AppendText("Conclusion：The same" + '\n\n')
    elif dValue <= 5:
        contents3.AppendText("Conclusion：High similarity" + '\n\n')
    elif dValue <= 10:
        contents3.AppendText("Conclusion：Medium similarity" + '\n\n')
    else:
        contents3.AppendText("Conclusion：Low similarity" + '\n\n')


# 函数功能：关闭窗口提示
def OnClose(event):
    ret = wx.MessageBox('Close the program？', 'Confirm again', wx.OK | wx.CANCEL)
    if ret == wx.OK:
        wx.Exit()  # 保证进程关闭


###############################################################################

if __name__ == '__main__':
    app = wx.App()

    # 主窗口
    win = wx.Frame(None, title="HashGo", size=(500, 500))
    bkg = wx.Panel(win)

    dirPath = wx.TextCtrl(bkg)
    choiceButton = wx.Button(bkg, label="Evidence folder", size=(120, 26))
    choiceButton.Bind(wx.EVT_BUTTON, OpenDir)

    matchListPath = wx.TextCtrl(bkg)
    choiceButton2 = wx.Button(bkg, label="Match list", size=(120, 26))
    choiceButton2.Bind(wx.EVT_BUTTON, OpenMatch)

    sampleList = ['MD5', 'SHA1', 'SHA256', 'SHA512']
    staticText = wx.StaticText(bkg, label="Algorithm:")
    hashType = wx.Choice(bkg, size=(120, 26), choices=sampleList)

    choiceButton3 = wx.Button(bkg, label="Confirm")
    choiceButton3.Bind(wx.EVT_BUTTON, Confirm)

    contents = wx.TextCtrl(bkg, style=wx.TE_MULTILINE | wx.HSCROLL)

    hbox1 = wx.BoxSizer()
    hbox1.Add(dirPath, proportion=1, flag=wx.EXPAND, border=5)
    hbox1.Add(choiceButton, proportion=0, flag=wx.LEFT, border=5)

    hbox2 = wx.BoxSizer()
    hbox2.Add(matchListPath, proportion=1, flag=wx.EXPAND, border=5)
    hbox2.Add(choiceButton2, proportion=0, flag=wx.LEFT, border=5)

    hbox3 = wx.BoxSizer()
    hbox3.Add(staticText, proportion=0, flag=wx.LEFT, border=5)
    hbox3.Add(hashType, proportion=0, flag=wx.LEFT, border=10)

    vbox = wx.BoxSizer(wx.VERTICAL)
    vbox.Add(hbox1, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
    vbox.Add(hbox2, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
    vbox.Add(hbox3, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
    vbox.Add(choiceButton3, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)
    vbox.Add(contents, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

    bkg.SetSizer(vbox)

    # 彩虹表生成器窗口
    win2 = wx.Frame(None, title="HashGo - Rainbow Table", size=(500, 500))
    bkg2 = wx.Panel(win2)

    staticText2 = wx.StaticText(bkg2, label="Characters:")
    characters = wx.TextCtrl(bkg2, size=(278, 26))

    staticText3 = wx.StaticText(bkg2, label="Minimum Len:")
    low = wx.TextCtrl(bkg2)

    staticText4 = wx.StaticText(bkg2, label="Maximum Len:")
    high = wx.TextCtrl(bkg2)

    staticText5 = wx.StaticText(bkg2, label="Salt:")
    salt = wx.TextCtrl(bkg2, size=(303, 26))

    staticText6 = wx.StaticText(bkg2, label="Algorithm:")
    hashType2 = wx.Choice(bkg2, size=(120, 26), choices=sampleList)

    choiceButton4 = wx.Button(bkg2, label="Confirm")
    choiceButton4.Bind(wx.EVT_BUTTON, Confirm_RB)

    contents2 = wx.TextCtrl(bkg2, style=wx.TE_MULTILINE | wx.HSCROLL)

    hbox4 = wx.BoxSizer()
    hbox4.Add(staticText2, proportion=0, flag=wx.RIGHT, border=10)
    hbox4.Add(characters, proportion=0, flag=wx.RIGHT, border=5)

    hbox5 = wx.BoxSizer()
    hbox5.Add(staticText3, proportion=0, flag=wx.RIGHT, border=10)
    hbox5.Add(low, proportion=0, flag=wx.RIGHT, border=20)
    hbox5.Add(staticText4, proportion=0, flag=wx.RIGHT, border=10)
    hbox5.Add(high, proportion=0, flag=wx.RIGHT, border=5)

    hbox6 = wx.BoxSizer()
    hbox6.Add(staticText5, proportion=0, flag=wx.RIGHT, border=10)
    hbox6.Add(salt, proportion=0, flag=wx.RIGHT, border=5)

    hbox7 = wx.BoxSizer()
    hbox7.Add(staticText6, proportion=0, flag=wx.RIGHT, border=10)
    hbox7.Add(hashType2, proportion=1, flag=wx.EXPAND, border=5)

    vbox2 = wx.BoxSizer(wx.VERTICAL)
    vbox2.Add(hbox4, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
    vbox2.Add(hbox5, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
    vbox2.Add(hbox6, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
    vbox2.Add(hbox7, proportion=0, flag=wx.ALL, border=5)
    vbox2.Add(choiceButton4, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)
    vbox2.Add(contents2, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

    bkg2.SetSizer(vbox2)

    # 图片对比器窗口
    win3 = wx.Frame(None, title="HashGo - Perceptual Hash", size=(500, 500))
    bkg3 = wx.Panel(win3)

    imgPath1 = wx.TextCtrl(bkg3)
    choiceButton5 = wx.Button(bkg3, label="Image A", size=(120, 26))
    choiceButton5.Bind(wx.EVT_BUTTON, OpenImage1)

    imgPath2 = wx.TextCtrl(bkg3)
    choiceButton6 = wx.Button(bkg3, label="Image B", size=(120, 26))
    choiceButton6.Bind(wx.EVT_BUTTON, OpenImage2)

    sampleList2 = ['aHash', 'pHash', 'dHash', 'wHash']
    staticText7 = wx.StaticText(bkg3, label="Algorithm:")
    PHAType = wx.Choice(bkg3, size=(120, 26), choices=sampleList2)

    choiceButton7 = wx.Button(bkg3, label="Confirm")
    choiceButton7.Bind(wx.EVT_BUTTON, Confirm_PHA)

    contents3 = wx.TextCtrl(bkg3, style=wx.TE_MULTILINE | wx.HSCROLL)

    hbox8 = wx.BoxSizer()
    hbox8.Add(imgPath1, proportion=1, flag=wx.EXPAND, border=5)
    hbox8.Add(choiceButton5, proportion=0, flag=wx.LEFT, border=5)

    hbox9 = wx.BoxSizer()
    hbox9.Add(imgPath2, proportion=1, flag=wx.EXPAND, border=5)
    hbox9.Add(choiceButton6, proportion=0, flag=wx.LEFT, border=5)

    hbox10 = wx.BoxSizer()
    hbox10.Add(staticText7, proportion=0, flag=wx.LEFT, border=5)
    hbox10.Add(PHAType, proportion=0, flag=wx.LEFT, border=10)

    vbox3 = wx.BoxSizer(wx.VERTICAL)
    vbox3.Add(hbox8, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
    vbox3.Add(hbox9, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
    vbox3.Add(hbox10, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
    vbox3.Add(choiceButton7, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)
    vbox3.Add(contents3, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

    bkg3.SetSizer(vbox3)

    # 窗口初始化
    win.Center()
    win.Show()
    win.Bind(wx.EVT_CLOSE, OnClose)
    win2.Bind(wx.EVT_CLOSE, OnClose)
    win3.Bind(wx.EVT_CLOSE, OnClose)
    app.MainLoop()
