import sys
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from Ui_login import Ui_Form
from Ui_func import *
from function import *
from PyQt5 import QtCore, QtGui, QtWidgets,Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
import PyQt5.sip


class Login_window(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(Login_window,self).__init__()
        self.setupUi(self)
        self.resize(1150,700)
        self.setWindowIcon(QtGui.QIcon("./ico/title.ico"))
        self.setWindowFlags(Qt.FramelessWindowHint) # 无边框化
        self.setWindowFlags(Qt.WindowCloseButtonHint)   # 添加关闭按钮
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)  # 固定窗口大小
        self.label_account.setMinimumSize(QtCore.QSize(30, 30))
        self.label_pas.setMinimumSize(QtCore.QSize(30, 30))
        self.label_pas.setStyleSheet("image: url(./software_images/pas.jpg);")
        self.label_account.setStyleSheet("image: url(./software_images/user.jpg);")

        ## 进行qss设计
        self.info_coor.setStyleSheet('font-size:15px')
        self.button_login.setText('登    录')
        self.label_title.setStyleSheet('font-size:25px')
        self.button_login.setCheckable(True)
        self.button_login.setObjectName("button_login")
        self.button_login.setStyleSheet(
        '#button_login{font-size:18px;color:rgb(255,255,255);border-radius:3px;background-color:rgb(55, 125, 186)}'
        '#button_login:hover{background-color:rgb(16, 58, 248);padding-top:5px}'
        )
        self.input_account.setStyleSheet('font-size:15px')
        self.input_pas.setStyleSheet('font-size:15px')
        #将点击事件与槽函数进行连接
        self.button_login.clicked.connect(self.login_func)
        self.button_login.setShortcut(QtCore.Qt.Key_Return)
        self.account = "admin"
        self.password = "test123"


    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap("./software_images/background.png")
        painter.drawPixmap(self.rect(), pixmap)
        
    # 登录按钮，函数
    def login_func(self):
        # 获取用户的输入账号和密码
        account = self.input_account.text()
        password = self.input_pas.text()
        if account == "" or password == "":
            reply = QMessageBox.warning(self,"警告","账号或者密码不能为空！")
            return 
        # 因为本软件不需要进行数据库连接 所以进行默认设置
        if account== self.account and  password == self.password:
            func_window.show()
            self.close()
        else:
            reply = QMessageBox.warning(self,"警告","账号或者密码输入错误！")
        

if __name__ == '__main__':
# def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Login_window() #生成一个实例
    func_window = Func_window()
    func_window.move((app.desktop().width() - func_window.width()) / 2, (app.desktop().height() - func_window.height()) / 4)
    window.move((app.desktop().width() - window.width()) / 2 , (app.desktop().height() - window.height()) / 2 )
    window.show()
    sys.exit(app.exec_())

 
