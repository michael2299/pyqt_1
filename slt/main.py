from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtWidgets
from slt import Ui_Form

import sys
import time
import logging
from logging.handlers import RotatingFileHandler

import configparser

import subprocess

'''
# 自适应窗口修改，参照文件 https://blog.csdn.net/CSDNlgx/article/details/115440559
# centos8.2 运行环境安装 dnf install python3-qt5
'''

# 配置日志信息
logger = logging.getLogger('sltgui')
logger.setLevel(logging.DEBUG)

log_file = "./sltgui.log"
#file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024,
                                 backupCount=10, encoding='utf-8', delay=0)
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M')
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)

logger.info("--------------------------------------------")

class Ui_MainWindow(QMainWindow, Ui_Form):
    def __init__(self, site_list, site_to_test):
        super().__init__()
        #self.ui = Ui_Form()
        self.setupUi(self)
        self.retranslateUi(self)

        self.site_list = site_list
        self.site_to_test = site_to_test
        self.site_process_id = []

    # manually setup additional widget info
    def setupinfo(self):
        self.radioButton.setChecked(True)
        self.lineEdit.setEnabled(False)
        self.comboBox_2.setEnabled(False)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checktask)

        # init site list
        _translate = QtCore.QCoreApplication.translate
        # add all sites option
        self.comboBox.addItem("")
        self.comboBox.setItemText(0, _translate("Form", 'all sites'))
        # add site list
        i = 0
        while i < len(self.site_list):
            index = i+1
            self.comboBox.addItem("")
            self.comboBox.setItemText(index, _translate("Form", self.site_list[i]))
            i+=1
        # output site to textbrowser
        if len(self.site_to_test) > 0 :
            for site in self.site_to_test :
                self.textBrowser.append(site)
    def checktask(self):
        '''
        check slt process status alive or dead
        :return:
        '''
        for site in site_to_test :
            cmd = ""
            logger.info("timeout")

    def start_case(self):
        t1 = time.asctime()

        if self.radioButton_2.isChecked() :
            mode = self.comboBox_2.currentText()
            sn = self.lineEdit.text()
            if not sn :
                self.textBrowser_2.append("请输入批次号")
                return
            self.textBrowser_2.append("量产模式：mode({}),批次({})".format(mode, sn))
            logger.info("开始量产模式：mode({}),批次({})".format(mode, sn))
        else :
            logger.info("开启工程模式")
        self.textBrowser_2.append( t1 + ": start run test case")
        if len(self.site_process_id) != 0 :
            self.textBrowser_2.append("后台已有任务在跑，请检查环境")
            return

        # 在多个site开启并发任务
        for site in self.site_to_test :
            cmd = ""
            p = subprocess.Popen("sleep 120", shell=True)
            self.site_process_id.append(p.pid)
            logger.info("start process id {} on site {}".format(p.pid, site))
            self.textBrowser_2.append("启动进程pid({}) on site {}".format(p.pid,site))
        self.pushButton.setEnabled(False)
        print(self.site_process_id)

        # 启动定时器，监测后台程序
        self.timer.start(30000)

    def stop_case(self):
        t2 = time.asctime()
        # 停止计时器
        self.timer.stop()
        self.pushButton.setEnabled(True)

        self.textBrowser_2.append( t2 + ": end run test case")
        for pid in self.site_process_id:
            cmd = "kill -9 {}".format(pid)
            subprocess.Popen(cmd, shell=True)
            self.textBrowser_2.append("kill pid {}".format(pid))
        self.site_process_id.clear()

    def collect_log(self):
        t3 = time.asctime()
        self.textBrowser_2.append( t3 + ": collect test log")

    def delete_site(self):
        site_to_del = self.comboBox.currentText()
        if site_to_del == 'all sites':
            self.textBrowser.clear()
            self.site_to_test.clear()
            return
        if site_to_del in self.site_to_test :
            self.site_to_test.remove(site_to_del)
            self.textBrowser.clear()
            for site in self.site_to_test:
                self.textBrowser.append(site)
            print("del {}".format(site_to_del))
        else:
            print("{} not in site to test".format(site_to_del))
            return

    def add_site(self):
        site_to_add = self.comboBox.currentText()
        if site_to_add == 'all sites':
            self.textBrowser.clear()
            for site in self.site_list:
                self.textBrowser.append(site)
            #  错误用法 self.site_to_test = self.site_list[:]
            self.site_to_test.extend(self.site_list)
            return
        if site_to_add in self.site_to_test :
            # already in test list
            print("{} already in the test list".format(site_to_add))
            return
        self.site_to_test.append(site_to_add)
        self.textBrowser.clear()
        for site in self.site_to_test :
            self.textBrowser.append(site)
        print("add {}".format(site_to_add))

    def enable_input(self):
        self.lineEdit.setEnabled(True)
        self.comboBox_2.setEnabled(True)

    def disable_input(self):
        self.lineEdit.setEnabled(False)
        self.comboBox_2.setEnabled(False)

if __name__ == "__main__":
    site_list = []
    site_to_test = []
    # read configure file
    cfp = configparser.ConfigParser()
    cfp.read("site.ini")

    options = cfp.options("allsites")
    if len(options) > 0:
        for site in options:
            value = cfp.get("allsites", site)
            site_list.append(site + "   " + value)

    options = cfp.options("site2test")
    if len(options) > 0:
        for site in options:
            value = cfp.get("site2test", site)
            site_to_test.append(site + "   " + value)

    # Start GUI
    # app = QApplication(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    window = QWidget()
    ui = Ui_MainWindow(site_list, site_to_test)
    #ui.show()
    ui.setupUi(window)
    ui.setupinfo()
    window.show()
    sys.exit(app.exec_())