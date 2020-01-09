# -*- coding: utf-8 -*-
import sys,os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from os.path import exists
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from Ui_func import *
from PyQt5.Qt import *
from functools import partial
import win32con
from win32process import SuspendThread, ResumeThread
import numpy as np
import cv2
import random
import math
import time
import ctypes
import PyQt5.sip
import PIL.Image as Image
import re
from PIL import Image


# 增加了一个继承自QThread类的类，重新写了它的run()函数
# run()函数即是新线程需要执行的函数
class WorkThread(QThread):
    trigger = pyqtSignal(str)
    handle = -1

    def __init__(self, files_path):
        super(WorkThread, self).__init__()
        # self.files_path = files_path

    def run(self):
        try:
            self.handle = ctypes.windll.kernel32.OpenThread(  
                win32con.PROCESS_ALL_ACCESS, False, int(QThread.currentThreadId()))
        except Exception as e:
            print('get thread handle failed', e)
        print('thread id', int(QThread.currentThreadId()))
        # 循环发送信号
        for i in range(1, 6):
            QThread.sleep(1)
        self.trigger.emit('end')


# 重写QLabel类，添加鼠标点击，鼠标滑过功能显示
class MyLabel_1(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()
            self.setStyleSheet("background-color:rgb(51,51,51)")

    def enterEvent(self,event):
        if QEvent.Enter:
            self.setStyleSheet("color:rgb(255,0,0)")

    def leaveEvent(self,event):
        if  QEvent.Leave:
            self.setStyleSheet("color:rgb(255,255,255)")
            

class MyLabel_2(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()

    def enterEvent(self,event):
        if QEvent.Enter:
            self.setStyleSheet("color:rgb(255,0,0)")

    def leaveEvent(self,event):
        if  QEvent.Leave:
            self.setStyleSheet("color:rgb(51, 204, 0)")


# 重写Qlabel，在label中显示的图片可以放大缩小和拖动
class my_labelshow(QLabel):
    def __init__(self):
        super(my_labelshow,self).__init__()
        self.image = QImage()
        self.ZoomValue = 1.125    # 鼠标缩放值
        self.XPtInterval = 0    # 平移X轴的值
        self.YPtInterval = 0    # 平移Y轴的值
        self.OldPos = QPoint()  # 旧的鼠标位置
        self.Pressed = False    # 鼠标是否被摁压
        self.LocalFileName = ''

    def refresh(self):
        self.ZoomValue = 1.125   # 鼠标缩放值
        self.XPtInterval = 0    # 平移X轴的值
        self.YPtInterval = 0    # 平移Y轴的值
        self.OldPos = QPoint()  # 旧的鼠标位置
        self.Pressed = False    # 鼠标是否被摁压
        self.LocalFileName = ''

    def paintEvent(self,event:QPaintEvent):
        if self.LocalFileName == '':
            pass
        else:
            self.image.load(self.LocalFileName)
            painter = QPainter()
            painter.begin(self)
            width = min(self.image.width(),self.width())
            height = width * 1.0 / (self.image.width() * 1.0 / self.image.height())
            height = min(height,self.height())
            width = height * 1.0 * (self.image.width() *1.0 / self.image.height())
            painter.translate(self.width() / 2 + self.XPtInterval, self.height() / 2 + self.YPtInterval)
            painter.scale(self.ZoomValue,self.ZoomValue)

            ########################大小调整
            width = min(self.image.width(),self.width())
            # height = min(self.image.height(),self.height())
            #########################
            picRect = QRectF(-width / 2, -height / 2, width, height)
            painter.drawImage(picRect,self.image)



    def wheelEvent(self,event:QWheelEvent):
        value = event.angleDelta()
        value = value.y() / 8  
        if value > 0:
            self.OnZoomInImage()
        else:
            self.OnZoomOutImage()
        self.update()

    def mousePressEvent(self,event:QMouseEvent):
        self.OldPos = event.pos()
        self.Pressed = True

    def mouseMoveEvent(self,event:QMouseEvent):
        if not self.Pressed:
            return QWidget.mouseMoveEvent(event)

        self.setCursor(Qt.SizeAllCursor)
        pos = QPoint()
        pos = event.pos()
        xPtInterval = pos.x() - self.OldPos.x()
        yPtInterval = pos.y() - self.OldPos.y()

        self.XPtInterval += xPtInterval
        self.YPtInterval += yPtInterval
        self.OldPos = pos
        self.update()
        # update()

    def mouseReleaseEvent(self,event):
        self.Pressed = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
    
    def OnZoomInImage(self):
        self.ZoomValue += 0.05
        self.update()

    def OnZoomOutImage(self):
        self.ZoomValue -= 0.05
        if self.ZoomValue <= 0.8:
            self.ZoomValue = 0.8
            return        
        self.update()

    def OnPresetImage(self):
        self.ZoomValue = 1.125
        self.XPtInterval = 0
        self.YPtInterval = 0
        self.update()

'''
    各个控件对应的展示文本或者图片
    info_infile : 导入源文件的路径
    info_proc   ：看图进度（根据车次和车部位确认）
    info_out    ：生成结果文件的存储路径
    info_warn   ：检测结果表格显示
    label_pic   ：检测结果图片（带框）显示
    comboBox_setnum：车组号
    comboBox_railnum：车辆号
    图片显示路径  = 车辆路径 + 检测部位路径 + 检测序号
    self.cur_ImPath = self.out_folder + self.show_pic[0] + 图片id.jpg

'''


class Func_window(QtWidgets.QWidget,Ui_high_speed):
    def __init__(self):
        super(Func_window,self).__init__()
        self.setupUi(self)
        self.label_pic =  my_labelshow()
        self.label_pic.setText("结果显示")
        self.label_pic.setObjectName("label_pic")
        self.gridLayout.addWidget(self.label_pic, 3, 1, 1, 1)
        self.resize(1400, 950)
        self.setWindowIcon(QtGui.QIcon("./ico/title.ico"))
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框化

        # 自定义标题栏
        self.button_max.clicked.connect(self.ShowRestoreWindow)
        self.button_close.clicked.connect(self.CloseWindow)
        self.button_min.clicked.connect(self.ShowMininizedWindow)
        self.button_min.setObjectName('min_max')
        self.button_min.setIcon(QtGui.QIcon("./ico/min.ico"))
        self.button_max.setObjectName('min_max')
        self.button_max.setIcon(QtGui.QIcon("./ico/max.ico"))
        self.button_close.setObjectName('min_max')
        self.button_close.setIcon(QtGui.QIcon("./ico/close.ico"))
        self.label_title.setObjectName('title_style')

        self.setStyleSheet('Func_window{background-color:rgb(51,51,51)}')
        stylepath = os.getcwd() + '/software_static/func_style.qss'
        with open(stylepath, 'r') as f:
            qApp.setStyleSheet(f.read())

        # 对应于车辆号号和车组号
        self.comboBox_railnum.setObjectName('comboBox_show')
        self.comboBox_setnum.setObjectName('comboBox_show')
        self.comboBox_railnum.setView(QListView())
        self.comboBox_setnum.setView(QListView())

        # 将点击事件与对应的槽函数进行连接
        self.button_begin.setObjectName('func_button')
        self.button_end.setObjectName('func_button')
        self.button_pro.setObjectName('order_button')
        self.button_next.setObjectName('order_button')

        self.button_in.clicked.connect(self.import_file)  # 导入文件按钮
        self.button_begin.clicked.connect(self.begin_test)  # 开始按钮
        self.button_end.clicked.connect(self.end_test)  # 结束按钮
        self.button_next.clicked.connect(self.pic_next)  # 下一张按钮
        self.button_pro.clicked.connect(self.pic_pro)  # 上一张按钮
        self.button_out.clicked.connect(self.export_file)  # 导出功能按钮

        # 以下是对应的过车序号
        self.button_pass = QButtonGroup(self)
        self.button_pass.addButton(self.passseq_1, 1)
        self.button_pass.addButton(self.passseq_2, 2)
        self.button_pass.addButton(self.passseq_3, 3)
        self.button_pass.addButton(self.passseq_4, 4)
        self.button_pass.addButton(self.passseq_5, 5)
        self.button_pass.addButton(self.passseq_6, 6)
        self.button_pass.addButton(self.passseq_7, 7)
        self.button_pass.addButton(self.passseq_8, 8)
        self.button_pass.addButton(self.passseq_9, 9)
        self.button_pass.addButton(self.passseq_10, 10)
        self.button_pass.addButton(self.passseq_11, 11)
        self.button_pass.addButton(self.passseq_12, 12)
        self.button_pass.addButton(self.passseq_13, 13)
        self.button_pass.addButton(self.passseq_14, 14)
        self.button_pass.addButton(self.passseq_15, 15)
        self.button_pass.addButton(self.passseq_16, 16)

        self.button_pass.setExclusive(True)

        self.passseq_1.setObjectName('part_pass_button_leftEdge')
        self.passseq_2.setObjectName('part_pass_button')
        self.passseq_3.setObjectName('part_pass_button')
        self.passseq_4.setObjectName('part_pass_button')
        self.passseq_5.setObjectName('part_pass_button')
        self.passseq_6.setObjectName('part_pass_button')
        self.passseq_7.setObjectName('part_pass_button')
        self.passseq_8.setObjectName('part_pass_button_rightEdge')
        self.passseq_9.setObjectName('part_pass_button_leftEdge')
        self.passseq_10.setObjectName('part_pass_button')
        self.passseq_11.setObjectName('part_pass_button')
        self.passseq_12.setObjectName('part_pass_button')
        self.passseq_13.setObjectName('part_pass_button')
        self.passseq_14.setObjectName('part_pass_button')
        self.passseq_15.setObjectName('part_pass_button')
        self.passseq_16.setObjectName('part_pass_button_rightEdge')

        self.passseq_1.setCheckable(True)
        self.passseq_2.setCheckable(True)
        self.passseq_3.setCheckable(True)
        self.passseq_4.setCheckable(True)
        self.passseq_5.setCheckable(True)
        self.passseq_6.setCheckable(True)
        self.passseq_7.setCheckable(True)
        self.passseq_8.setCheckable(True)
        self.passseq_9.setCheckable(True)
        self.passseq_10.setCheckable(True)
        self.passseq_11.setCheckable(True)
        self.passseq_12.setCheckable(True)
        self.passseq_13.setCheckable(True)
        self.passseq_14.setCheckable(True)
        self.passseq_15.setCheckable(True)
        self.passseq_16.setCheckable(True)

        self.passseq_1.clicked.connect(partial(self.but_pass,1))
        self.passseq_2.clicked.connect(partial(self.but_pass,2))
        self.passseq_3.clicked.connect(partial(self.but_pass,3))
        self.passseq_4.clicked.connect(partial(self.but_pass,4))
        self.passseq_5.clicked.connect(partial(self.but_pass,5))
        self.passseq_6.clicked.connect(partial(self.but_pass,6))
        self.passseq_7.clicked.connect(partial(self.but_pass,7))
        self.passseq_8.clicked.connect(partial(self.but_pass,8))
        self.passseq_9.clicked.connect(partial(self.but_pass,9))
        self.passseq_10.clicked.connect(partial(self.but_pass,10))
        self.passseq_11.clicked.connect(partial(self.but_pass,11))
        self.passseq_12.clicked.connect(partial(self.but_pass,12))
        self.passseq_13.clicked.connect(partial(self.but_pass,13))
        self.passseq_14.clicked.connect(partial(self.but_pass,14))
        self.passseq_15.clicked.connect(partial(self.but_pass,15))
        self.passseq_16.clicked.connect(partial(self.but_pass,16))


        # # 以下是对应的监测部位序号
        self.button_part = QButtonGroup(self)
        self.button_part.addButton(self.button_rightdown, 1)
        self.button_part.addButton(self.button_rightup, 2)
        self.button_part.addButton(self.button_leftdown, 3)
        self.button_part.addButton(self.button_leftup, 4)
        self.button_part.addButton(self.button_basemid, 5)
        self.button_part.addButton(self.button_baseinright, 6)
        self.button_part.addButton(self.button_baseinleft, 7)
        self.button_part.addButton(self.button_baseoutright, 8)
        self.button_part.addButton(self.button_baseoutleft, 9)
        

        self.button_rightdown.setObjectName('part_pass_button')
        self.button_rightup.setObjectName('part_pass_button_leftEdge')
        self.button_leftdown.setObjectName('part_pass_button')
        self.button_leftup.setObjectName('part_pass_button')
        self.button_baseinleft.setObjectName('part_pass_button')
        self.button_baseinright.setObjectName('part_pass_button')
        self.button_baseoutleft.setObjectName('part_pass_button_rightEdge')
        self.button_baseoutright.setObjectName('part_pass_button')
        self.button_basemid.setObjectName('part_pass_button')
        

        self.button_rightdown.setCheckable(True)
        self.button_rightup.setCheckable(True)
        self.button_leftdown.setCheckable(True)
        self.button_leftup.setCheckable(True)
        self.button_basemid.setCheckable(True)
        self.button_baseoutright.setCheckable(True)
        self.button_baseoutleft.setCheckable(True)
        self.button_baseinleft.setCheckable(True)
        self.button_baseinright.setCheckable(True)
        
        self.button_rightdown.clicked.connect(partial(self.but_part,'rd'))
        self.button_rightup.clicked.connect(partial(self.but_part,'ru'))
        self.button_leftdown.clicked.connect(partial(self.but_part,'ld'))
        self.button_leftup.clicked.connect(partial(self.but_part,'lu'))
        self.button_baseinleft.clicked.connect(partial(self.but_part,'bil'))
        self.button_baseinright.clicked.connect(partial(self.but_part,'bir'))
        self.button_baseoutleft.clicked.connect(partial(self.but_part,'bol'))
        self.button_baseoutright.clicked.connect(partial(self.but_part,'bor'))
        self.button_basemid.clicked.connect(partial(self.but_part,'bm'))
        
        # 以下是对于的各种文字label标签
        self.label_pro.setObjectName('hint_label_deepdark')
        self.label_monitor.setObjectName('hint_label_deepdark')
        self.label_passrail.setObjectName('hint_label_deepdark')
        self.label_set.setObjectName('hint_label_deepdark')
        self.label_rail.setObjectName('hint_label_deepdark')
        self.label_out.setObjectName('hint_label')
        self.label_picin.setFrameShape(QFrame.Box)
        self.label_picin.setObjectName('hint_label_picin')
        self.info_proc.setObjectName('hint_label_deepred')
        
        # 对应于导入和导出文件
        self.info_out.setObjectName('file_label')
        self.info_infile.setObjectName('file_label')
        
        # 对应于导入导出功能按钮
        self.button_in.setObjectName('inout_button')
        self.button_out.setObjectName('inout_button')

        # 对应于操作状态提示
        self.label_state.setObjectName('state_label')

        # 对应于缺陷显示结果区域
        self.info_warn.setObjectName('show_warn')
        self.info_warn.horizontalHeader().setObjectName('header_show_warn')

        # 定义相关变量并且进行初始化
        self.info_warn_col = 5  # 缺陷检测结果列数（5）
        self.info_warn_row = 0  # 缺陷检测结果行数
        self.show_info = []
        
        self.import_filepath = ''
        self.out_folder = ''    # 结果图片的文件夹路径
        self.show_beg = 0
        self.show_end = 0
        self.show_pic = ['', '', '']   # 定义显示图片的存储为list，共有三个参数 list[0]: 车部位文件夹
                             #                                     list[1]: 开始查看的图片序号，共有33张图片
                             #                                     list[2]: 结束产看的图片序号
        self.cur_imageID = 0    # 当前浏览的图片id
        self.image_num = 32     # 去除最开始和最末尾的5张图片 总共256 / 8 = 32 每节车厢32张图片
        self.cur_ImPath = ''
        self.list_rail = []
        self.comboBox_railnum.clear()
        self.comboBox_setnum.clear()
        self.default_folder()
        self.info_out.clear()
        self.comboBox_railnum.activated.connect(self.change_folder)
        self.comboBox_setnum.activated.connect(self.change_folder)
        self.info_warn.verticalHeader().setVisible(False)
        self.info_warn.horizontalHeader().setVisible(False)

        self.button_begin.setCheckable(True)
        self.button_end.setCheckable(True)
        self.button_end.setChecked(True)


        self.button_next.setCheckable(True)
        self.button_pro.setCheckable(True)

    def refresh_all(self):
        self.show_pic = ['','','']
        self.setWindowTitle('高速列车车轮组件异常动态智能检测系统')
        self.label_pic.clear()
        self.label_pic.refresh()
        self.label_state.clear()
        self.info_proc.clear()
        self.info_warn.setRowCount(0)
        self.info_warn.setColumnCount(5)
        self.info_warn.clearContents()
        self.info_warn.clear()
        self.show_info = []
        self.show_beg = 0
        self.show_end = 0
        self.refresh_button()

    def refresh_button(self):
        self.button_pass.setExclusive(False)
        self.button_part.setExclusive(False)
        for button in self.button_pass.buttons():
            if button.isChecked():
                button.setCheckable(True)
                button.setChecked(False)
        for button in self.button_part.buttons():
            if button.isChecked():
                button.setCheckable(True)
                button.setChecked(False)
        self.button_pass.setExclusive(True)
        self.button_part.setExclusive(True)

    '''
        打开文件夹功能函数 open_file
        根据需要的文件类型修改打开方式
        这儿因为我们针对一个文件夹进行操作，所以设定 getExistingDirectory
        结果文件在当前导入的文件夹路径下的 /image_out 中
    '''   
    def import_file(self):
        import_filepath = QFileDialog.getExistingDirectory(None,'选择文件','\\home\\')
        self.info_infile.setText(import_filepath)
        if import_filepath == '':
            return
        # print('导入文件夹路径' + import_filepath)
        if self.import_filepath != import_filepath:
            self.refresh_all()

            self.import_filepath = import_filepath
            add_index = import_filepath.rindex('/')
            add_folder = import_filepath[add_index+1:]
            setnum = add_folder[:2]
            railnum = add_folder[2:]
            add_folder = setnum + railnum
            if add_folder not in self.list_rail:
                self.comboBox_setnum.addItem(setnum)
                self.comboBox_railnum.addItem(railnum)
                self.list_rail.append(add_folder)
            index = self.list_rail.index(add_folder)
            self.comboBox_setnum.setCurrentIndex(index)
            self.comboBox_railnum.setCurrentIndex(index)
            show_path = os.getcwd() + '/image_out/'
            self.out_folder = show_path + self.comboBox_setnum.currentText() + self.comboBox_railnum.currentText()
            # print('导入之后的当前图片显示文件夹路径' + self.out_folder)
        else:
            return

    '''
        设置车辆和车组号显示函数 default_folder
        默认读取的当前文件下的所有结果文件，并且写入路径
    '''   
    def default_folder(self):
        show_path = os.getcwd() + '/image_out'
        for fn in os.listdir(show_path):
            self.list_rail.append(fn)
        if self.list_rail:
            for list_rail in self.list_rail:
                self.comboBox_setnum.addItem(list_rail[:2])
                self.comboBox_railnum.addItem(list_rail[2:])
        self.comboBox_setnum.setCurrentIndex(-1)
        self.comboBox_railnum.setCurrentIndex(-1)

    '''
        函数 change_folder
        根据点选的索引号修改读取路径
    '''  
    def change_folder(self):
        # 车组号 车辆号 关系 不定 ？  
        self.out_folder = os.getcwd() +  '/image_out/' + self.comboBox_setnum.currentText() +  self.comboBox_railnum.currentText() 
        self.refresh_all()

    '''
        开始检测功能函数 begin_test 
        根据函数 import_file 中设定的文件夹路径：self.info_infile 
        执行缺陷检测功能函数，生成报警信息写入info_warn中
        当点击info_warn 中的
    ''' 
    def begin_test(self):
        self.begin_thread = WorkThread(self)
        self.begin_thread.finished.connect(self.begin_thread.deleteLater)

        self.button_begin.setEnabled(False)
        self.begin_thread.trigger.connect(self.end_test)
        self.button_end.setChecked(False)
        self.button_end.setEnabled(True)
        #启动线程
        self.begin_thread.start()


    '''
        结束检测功能函数 end_test 
        立即停止当前执行的检测，返回正常界面
    '''
    def end_test(self,msg='unnormal'):
        if self.begin_thread.isRunning():
            self.begin_thread.quit()
        self.button_begin.setEnabled(True)
        self.button_begin.setChecked(False)
        self.button_end.setEnabled(False)
        self.button_end.setChecked(True)

        ################################
        ret = ctypes.windll.kernel32.TerminateThread(self.begin_thread.handle, 0)
        self.button_end.setEnabled(False)
        if msg == 'end':
            del self.begin_thread
            QMessageBox.information(None,'执行结束提示','检测完毕，请点击相关区域查看')
        else:
            # self.begin_thread.stop()
            del self.begin_thread
            QMessageBox.information(None,'错误结束提示','检测可能未完成')

    '''
        缺陷检测结果显示函数 show_warn
        根据函数执行的结果，生成的对应文件，将结果显示在控件info_warn中
        点击对应的序号之后，调用矩形框绘制函数show_defect，在原图上绘制矩形框
    ''' 
    def show_warn(self, col, row):
        self.info_warn.setColumnCount(col)
        self.info_warn.setRowCount(row + 2)  # 根据生成的报警信息进行修改
        # 关键 ！！！ 因为要将前两行作为信息显示的行，所以要首先多生成两行以存放足够的报警信息，避免缺失
        self.info_warn.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        info_warn_col = col
        info_warn_row = row
        QTableWidget.resizeColumnsToContents(self.info_warn)
        QTableWidget.resizeRowsToContents(self.info_warn)
        self.info_warn.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        # 根据实际状况逐行显示数据到info_warn
        # 在单元格内放置控件
        
        self.info_warn.setSpan(0, 0, 1, 5)
        newTitle = QLabel()
        newTitle.setText('自动报警信息')
        newTitle.setStyleSheet('color:rgb(255, 204, 0);font-size:15px;font-weight:bold')
        newTitle.setAlignment(Qt.AlignCenter)
        self.info_warn.setCellWidget(0,0,newTitle)

        newHeader = QLabel()
        newHeader.setStyleSheet('color:rgb(255, 255,255);font-weight:bold')
        newHeader.setAlignment(Qt.AlignCenter)
        newHeader.setText('序号')
        self.info_warn.setCellWidget(1,0,newHeader)

        newHeader_1 = QLabel()
        newHeader_1.setStyleSheet('color:rgb(255, 255,255);font-weight:bold')
        newHeader_1.setAlignment(Qt.AlignCenter)
        newHeader_1.setText('状态')
        self.info_warn.setCellWidget(1,1,newHeader_1)

        newHeader_2 = QLabel()
        newHeader_2.setStyleSheet('color:rgb(255, 255,255);font-weight:bold')
        newHeader_2.setAlignment(Qt.AlignCenter)
        newHeader_2.setText('确认状态')
        self.info_warn.setCellWidget(1,2,newHeader_2)

        newHeader_3 = QLabel()
        newHeader_3.setStyleSheet('color:rgb(255, 255,255);font-weight:bold')
        newHeader_3.setAlignment(Qt.AlignCenter)
        newHeader_3.setText('缺陷零部件')
        self.info_warn.setCellWidget(1,3,newHeader_3)

        newHeader_4 = QLabel()
        newHeader_4.setStyleSheet('color:rgb(255, 255,255);font-weight:bold')
        newHeader_4.setAlignment(Qt.AlignCenter)
        newHeader_4.setText('报警描述')
        self.info_warn.setCellWidget(1,4,newHeader_4)
        
        for i in range(info_warn_row):
            if len(self.show_info[i]) == 8:
                self.label_seqwarn = MyLabel_1()
                self.label_seqwarn.setObjectName('label_seqwarn')
                self.label_confirm =QtWidgets.QLabel()
                self.label_part = QtWidgets.QLabel()
                self.label_des = QtWidgets.QLabel()

                self.label_seqwarn.setText('<u>' + str(i+1) + '</u>')
                self.label_seqwarn.setStyleSheet('color:rgb(255,255,255)')
                self.label_seqwarn.setFont(QFont("宋体",10,QFont.Bold))
                self.label_seqwarn.setAlignment(Qt.AlignCenter)
                self.label_seqwarn.clicked.connect(partial(self.show_defect,i,'confirmed'))
                self.info_warn.setCellWidget(i+2,0,self.label_seqwarn)
                
                self.label_sta = QtWidgets.QLabel()
                self.label_sta.setText('报警')
                self.label_sta.setStyleSheet('color:rgb(255,255,255)')
                self.label_sta.setFont(QFont("宋体",9))
                self.label_sta.setAlignment(Qt.AlignCenter)
                self.info_warn.setCellWidget(i+2,1,self.label_sta)
                
                self.label_confirm.setText('已确认')
                self.label_confirm.setStyleSheet('color:rgb(255, 0, 0)')
                self.label_confirm.setFont(QFont("宋体",10,QFont.Bold))
                self.label_confirm.setAlignment(Qt.AlignCenter)
                # self.label_confirm.clicked.connect(partial(self.delete_defect,i))
                self.info_warn.setCellWidget(i+2,2,self.label_confirm)

                self.label_part = QtWidgets.QLabel()
                self.label_part.setText(self.show_info[i][1])
                self.label_part.setStyleSheet('color:rgb(255,204,0)')
                self.label_part.setFont(QFont("宋体",8,QFont.Bold))
                self.label_part.setAlignment(Qt.AlignCenter)
                self.info_warn.setCellWidget(i+2,3,self.label_part)

                self.label_des = QtWidgets.QLabel()
                self.label_des.setText('存在异常')
                self.label_des.setStyleSheet('color:rgb(255,255,255)')
                self.label_des.setFont(QFont("宋体",9))
                self.label_des.setAlignment(Qt.AlignCenter)
                self.info_warn.setCellWidget(i+2,4,self.label_des)
            else:
                self.label_seqwarn = MyLabel_1()
                # self.label_seqwarn = QLabel()
                self.label_seqwarn.setObjectName('label_seqwarn')
                self.label_confirm = MyLabel_2()
                self.label_part = QtWidgets.QLabel()
                self.label_des = QtWidgets.QLabel()

                self.label_seqwarn.setText('<u>' + str(i+1) + '</u>')
                self.label_seqwarn.setStyleSheet('color:rgb(255,255,255)')
                self.label_seqwarn.setFont(QFont("宋体",10,QFont.Bold))
                self.label_seqwarn.setAlignment(Qt.AlignCenter)
                self.label_seqwarn.clicked.connect(partial(self.show_defect,i,'unconfirmed'))
                self.info_warn.setCellWidget(i+2,0,self.label_seqwarn)
                
                self.label_sta = QtWidgets.QLabel()
                self.label_sta.setText('报警')
                self.label_sta.setStyleSheet('color:rgb(255,255,255)')
                self.label_sta.setFont(QFont("宋体",9))
                self.label_sta.setAlignment(Qt.AlignCenter)
                self.info_warn.setCellWidget(i+2,1,self.label_sta)
                
                self.label_confirm.setText('待确认')
                self.label_confirm.setStyleSheet('color:rgb(51, 204, 0)')
                self.label_confirm.setFont(QFont("宋体",10,QFont.Bold))
                self.label_confirm.setAlignment(Qt.AlignCenter)
                self.label_confirm.clicked.connect(partial(self.delete_defect,i))
                self.info_warn.setCellWidget(i+2,2,self.label_confirm)

                self.label_part = QtWidgets.QLabel()
                self.label_part.setText(self.show_info[i][1])
                self.label_part.setStyleSheet('color:rgb(255,204,0)')
                self.label_part.setFont(QFont("宋体",8,QFont.Bold))
                self.label_part.setAlignment(Qt.AlignCenter)
                self.info_warn.setCellWidget(i+2,3,self.label_part)

                self.label_des = QtWidgets.QLabel()
                self.label_des.setText('存在异常')
                self.label_des.setStyleSheet('color:rgb(255,255,255)')
                self.label_des.setFont(QFont("宋体",9))
                self.label_des.setAlignment(Qt.AlignCenter)
                self.info_warn.setCellWidget(i+2,4,self.label_des)

    def cv_imread(self,filePath):
        cv_img=cv2.imdecode(np.fromfile(filePath,dtype=np.uint8),-1)
        return cv_img

    '''
        缺陷检测矩形框绘制显示函数 show_defect
        根据缺陷检测.txt文件中的对应部位，在原图对应位置绘制矩形框
    '''
    def show_defect(self,index,state='unconfirmed'):
        frame_path = self.show_pic[0] + '/' + self.show_info[index][0]
        frame_pos = []
        frame_pos.append((self.show_info[index][3]))
        frame_pos.append((self.show_info[index][4]))
        frame_pos.append((self.show_info[index][5]))
        frame_pos.append((self.show_info[index][6]))
        x1 = int(frame_pos[0])
        y1 = int(frame_pos[1])
        x2 = int(frame_pos[2])
        y2 = int(frame_pos[3])
        self.frame_img = self.cv_imread(frame_path)
        if state == 'confirmed':
            cv2.rectangle(self.frame_img,(x1,y1),(x2,y2),(0,0,255),10)
        else:
            cv2.rectangle(self.frame_img,(x1,y1),(x2,y2),(15,185,255),10)
        self.height,self.width = self.frame_img.shape[0:2]  #获取原图像的水平方向尺寸和垂直方向尺寸
        self.test_index = index
        img = self.show_info[index][0]
       
        cv2.namedWindow(img, 0)
        cv2.moveWindow(img, 100, 40)
        self.win_h, self.win_w = 900, 1400  # 窗口高宽
        self.wx, self.wy = 0,0  # 窗口相对于原图的坐标
        self.wheel_step, self.zoom = 0.05, 1  # 缩放系数， 缩放值
        self.zoom_w, self.zoom_h = self.width, self.height  # 缩放图宽高
        self.img_zoom = self.frame_img.copy()  # 缩放图片
        self.flag, self.flag_har, self.flag_var = 0, 0, 0  # 鼠标操作类型
        self.move_w, self.move_h = 0, 0  # 鼠标移动坐标
        self.show_x1, self.show_y1, self.show_x2, self.show_y2 = 0, 0, 0, 0  # 中间变量
        cv2.resizeWindow(img, self.win_w, self.win_h)
        self.dst = self.frame_img[self.wy:self.wy + self.win_h, self.wx: self.wx + self.win_w]
        cv2.setMouseCallback(img, self.mouse)
        if self.width > self.win_w:
            self.flag_har = 1
        if self.height > self.win_h:
            self.flag_var = 1

    '''
        鼠标拖动事件 mouse 
        实现通过鼠标滚轮放大缩小图片，左键抓取拖动图片
    '''    
    def mouse(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
            if self.flag == 0:
                self.flag = 1
                self.show_x1, self.show_y1, self.show_x2, self.show_y2 = x, y, self.wx, self.wy  # 使鼠标移动距离都是相对于初始点击位置，而不是相对于上一位置
        elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
            if self.flag == 1:
                self.move_w, self.move_h = self.show_x1 - x, self.show_y1 - y  # 鼠标拖拽移动的宽高
                if self.flag_har and self.flag_var:  # 当窗口宽高大于图片宽高
                    self.wx = self.show_x2 + self.move_w  # 窗口在大图的横坐标
                    if self.wx < 0:  # 矫正位置
                        self.wx = 0
                    elif self.wx + self.win_w > self.zoom_w:
                        self.wx = self.zoom_w - self.win_w
                    self.wy = self.show_y2 + self.move_h  # 窗口在大图的总坐标
                    if self.wy < 0:
                        self.wy = 0
                    elif self.wy + self.win_h > self.zoom_h:
                        self.wy = self.zoom_h - self.win_h
                    self.dst = self.img_zoom[self.wy:self.wy + self.win_h, self.wx: self.wx + self.win_w]  # 截取窗口显示区域
                elif self.flag_har and self.flag_var == 0:  # 当窗口宽度大于图片宽度
                    self.wx = self.show_x2 + self.move_w
                    if self.wx < 0:
                        self.wx = 0
                    elif self.wx + self.win_w > self.zoom_w:
                        self.wx = self.zoom_w - self.win_w
                    self.dst = self.img_zoom[0:self.zoom_h, self.wx: self.wx + self.win_w]
                elif self.flag_har == 0 and self.flag_var:  # 当窗口高度大于图片高度
                    self.wy = self.show_y2 + self.move_h
                    if self.wy < 0:
                        self.wy = 0
                    elif self.wy + self.win_h > self.zoom_h:
                        self.wy = self.zoom_h - self.win_h
                    self.dst = self.img_zoom[self.wy:self.wy + self.win_h, 0: self.zoom_w]
        elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
            self.flag = 0
            self.show_x1, self.show_y1, self.show_x2, self.show_y2 = 0, 0, 0, 0
        elif event == cv2.EVENT_MOUSEWHEEL:  # 滚轮
            z = self.zoom
            if flags > 0:  # 滚轮上移
                self.zoom += self.wheel_step
                if self.zoom > 1 + self.wheel_step * 20:  # 缩放倍数调整
                    self.zoom = 1 + self.wheel_step * 20
            else:  # 滚轮下移
                self.zoom -= self.wheel_step
                if self.zoom < 0.5:  # 缩放倍数调整
                    self.zoom = 0.5
            self.zoom = round(self.zoom, 2)  # 取2位有效数字
            self.zoom_w, self.zoom_h = int(self.width * self.zoom), int(self.height * self.zoom)
            self.wx, self.wy = int((self.wx + x) * self.zoom / z - x), int((self.wy + y) * self.zoom / z - y)  # 缩放后鼠标在原图的坐标
            # print(z, self.zoom, x, y, self.wx, self.wy)
            if self.wx < 0:
                self.wx = 0
            elif self.wx + self.win_w > self.zoom_w:
                self.wx = self.zoom_w - self.win_w
            if self.wy < 0:
                self.wy = 0
            elif self.wy + self.win_h > self.zoom_h:
                self.wy = self.zoom_h - self.win_h
            self.img_zoom = cv2.resize(self.frame_img, (self.zoom_w, self.zoom_h), interpolation=cv2.INTER_AREA)  # 图片缩放
            if self.zoom_w <= self.win_w and self.zoom_h <= self.win_h:  # 缩放后图片宽度小于窗口宽度
                self.flag_har, self.flag_var = 0, 0
                self.dst = self.img_zoom
            elif self.zoom_w <= self.win_w and self.zoom_h > self.win_h:  # 缩放后图片宽度小于窗口宽度
                self.flag_har, self.flag_var = 0, 1
                self.dst = self.img_zoom[self.wy:self.wy + self.win_h, 0:self.zoom_w]
            elif self.zoom_w > self.win_w and self.zoom_h <= self.win_h:  # 缩放后图片高度大于窗口高度
                self.flag_har, self.flag_var = 1, 0
                self.dst = self.img_zoom[0:self.zoom_h, self.wx:self.wx + self.win_w]
            else:  # 缩放后图片宽高大于于窗口宽高
                self.flag_har, self.flag_var = 1, 1
                self.dst = self.img_zoom[self.wy:self.wy + self.win_h, self.wx:self.wx + self.win_w]
        cv2.imshow(self.show_info[self.test_index][0], self.dst)
        self.info_warn.setStyleSheet('background-color:rgb(51,51,51)')

    '''
        缺陷检测误报函数 delete_defect
        删除对应行的缺陷检测文件数据
    '''
    def delete_defect(self,index):
        delete_path = self.show_pic[0] + self.show_info[index][0]
        del self.show_info[index]
        self.info_warn.setStyleSheet('background-color:rgb(51,51,51)')
        self.show_warn(self.info_warn_col,len(self.show_info))

    '''
        查看结果文件下一张函数 pic_next 
        根据过车序号和监测部位确定的cur_folder，打开对应的文件夹查看下一张结果文件图片
    '''
    def pic_next(self):
        if os.path.exists(self.cur_ImPath) == False:
            self.refresh_button()
            QMessageBox.warning(None,'错误操作提示','请先确定路径')
            return
        cur_imageID = self.cur_imageID
        cur_imgindex1 = self.show_pic[0].rindex('/')
        cur_imgindex2 = self.show_pic[0].rindex('_')
        tmp_curpath = self.show_pic[0][cur_imgindex1 + 1 : cur_imgindex2]
        if (cur_imageID < self.image_num - 1 ): # 不可以循环看图
            cur_imageID = cur_imageID + 1
            self.cur_ImPath = self.show_pic[0] + '/' + tmp_curpath + '-' + str(self.show_pic[1] + cur_imageID) + '.jpg'
            if os.path.exists(self.cur_ImPath) == False:
                QMessageBox.warning(None,'错误操作提示','文件可能不存在')
                return
            self.label_pic.refresh()
            self.label_pic.LocalFileName = self.cur_ImPath
            self.update()

            self.info_proc.setText(str(cur_imageID + 1) + '/' + str(self.image_num))
            self.cur_imageID = cur_imageID
            self.label_state.setText('图片序号      ' + self.cur_ImPath)

            #########画框##############
            self.load_image(self.cur_imageID)
            ########################### 

            # self.setWindowTitle(self.cur_ImPath)
        else:
            self.refresh_button()
            QMessageBox.warning(None,'错误操作提示','已经是最后一张！')

    '''
        查看结果文件上一张函数 pic_pro
        根据过车序号和监测部位确定的cur_folder，打开对应的文件夹查看上一张结果文件图片
    '''
    def pic_pro(self):
        if not exists(self.cur_ImPath):
            self.refresh_button()
            QMessageBox.warning(None,'错误操作提示','请先确定路径')
            return
        cur_imageID = self.cur_imageID
        cur_imgindex1 = self.show_pic[0].rindex('/')
        cur_imgindex2 = self.show_pic[0].rindex('_')
        tmp_curpath = self.show_pic[0][cur_imgindex1 + 1 : cur_imgindex2]
        if (cur_imageID >= 1): # 不可以循环看图
            cur_imageID = cur_imageID - 1
            self.cur_ImPath = self.show_pic[0] + '/' + tmp_curpath + '-' + str(self.show_pic[1] + cur_imageID) + '.jpg'
            self.label_pic.refresh()
            self.label_pic.LocalFileName = self.cur_ImPath
            self.update()

            self.info_proc.setText(str(cur_imageID + 1) + '/' + str(self.image_num))
            self.cur_imageID = cur_imageID
            self.label_state.setText('  图片名称      ' + self.cur_ImPath)

            #########画框##############
            self.load_image(self.cur_imageID)
            ########################### 

            # self.setWindowTitle(self.cur_ImPath)
        else:
            self.refresh_button()
            QMessageBox.warning(None,'错误操作提示','已经是第一张！')

    '''
        检测结果导出函数 export_file 
        自定义存储路径，将结果文件(.txt)存储到对应文件
    '''
    def export_file(self):
        # 目前结果文件为.txt格式
        try:
            tmp_outindex = self.show_pic[0].rindex('/')
            default_name = './' + self.show_pic[0][tmp_outindex + 1 :] + '.txt'
            export_filepath = QFileDialog.getSaveFileName(self,("检测结果文件"),default_name, ("文本文件 (*.txt)"))
        except:
            QMessageBox.warning(None,'错误操作提示','相关文件或路径不存在！')
            return
        try:
            file = open(export_filepath[0],'w')
        except:
            return
        for i in self.show_info:
            file.write(' '.join(i) + str('\n'))
        file.close()
        self.info_out.setText(export_filepath[0])
        QMessageBox.information(self,'文件保存成功提示','文件已保存到' + export_filepath[0])

    '''
        查看结果文件中的对应车序号文件夹函数 but_pass
        必须结合车部位函数确认唯一的result folder，否则路径会报错
    '''
    def but_pass(self,seq):
        self.show_beg = (seq - 1)*32 + 5
        self.show_end = seq * 32 + 5 
        self.show_pic[1] = self.show_beg
        self.show_pic[2] = self.show_end
        self.cur_imageID = 0
        tmp_curpath = ''
        if self.show_pic[0]:
            cur_imgindex1 = self.show_pic[0].rindex('/')
            cur_imgindex2 = self.show_pic[0].rindex('_')
            tmp_curpath = self.show_pic[0][cur_imgindex1 + 1:cur_imgindex2]  

            #######合并图片#######
            self.joint_pic(self.cur_file)
            #####################

        self.cur_ImPath = self.show_pic[0] + '/' + tmp_curpath + '-' + str(self.show_pic[1]) + '.jpg'

        if not exists(self.cur_ImPath):
            return 
        self.label_pic.refresh()
        self.label_pic.LocalFileName = self.cur_ImPath
        self.update()

        #########画框##############
        self.load_image(self.cur_imageID)
        ########################### 

        self.label_state.setText('  图片名称      ' + self.cur_ImPath)
        self.info_proc.setText(str(self.cur_imageID + 1) + '/' + str(self.image_num))

    '''
        查看结果文件中的对应车部位文件夹函数 but_part
        必须结合车序号函数确认唯一的result folder，否则路径会报错
        左侧上：button_leftup --> lu 28
        左侧下：button_leftdown --> lr 27
        右侧上：button_rightup --> rd 20
        右侧下：button_rightdown -- >ru 21
        底中：button_basemid --> bm 24
        底内左：button_baseinleft --> bil 25
        底内右：button_baseinright --> bir 23  
        底外左：button_baseoutleft --> bol 26
        底外右：button_baseoutright --> bor 22 
    '''
    def but_part(self,part):
        if not exists(self.out_folder):
            self.refresh_button()
            self.label_pic.clear()
            self.label_pic.refresh()
            self.label_picall.clear()
            QMessageBox.warning(None,'错误路径提示','当前路径不存在，请检查')
            return
        if part == 'ru':
            self.show_pic[0] = self.out_folder + '/20_result'
            self.cur_ImPath = self.show_pic[0] + '/20-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '20'
        elif part == 'rd':
            self.show_pic[0] = self.out_folder + '/21_result'
            self.cur_ImPath = self.show_pic[0] + '/21-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '21'
        elif part == 'bor':
            self.show_pic[0] = self.out_folder + '/22_result'
            self.cur_ImPath = self.show_pic[0] + '/22-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '22'
        elif part == 'bir':
            self.show_pic[0] = self.out_folder + '/23_result'
            self.cur_ImPath = self.show_pic[0] + '/23-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '23'
        elif part == 'bm':
            self.show_pic[0] = self.out_folder + '/24_result'
            self.cur_ImPath = self.show_pic[0] + '/24-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '24'
        elif part == 'bil':
            self.show_pic[0] = self.out_folder + '/25_result'
            self.cur_ImPath = self.show_pic[0] + '/25-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '25'
        elif part == 'bol':
            self.show_pic[0] = self.out_folder + '/26_result'
            self.cur_ImPath = self.show_pic[0] + '/26-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '26'
        elif part == 'ld':
            self.show_pic[0] = self.out_folder + '/27_result'
            self.cur_ImPath = self.show_pic[0] + '/27-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '27'
        elif part == 'lu':
            self.show_pic[0] = self.out_folder + '/28_result'
            self.cur_ImPath = self.show_pic[0] + '/28-' + str(self.show_pic[1]) + '.jpg'
            self.cur_file = '28'
        # print('当前应该显示的图片结果' + self.cur_ImPath)
        if len(os.listdir(self.show_pic[0])) == 266:
            self.button_pass.setExclusive(False)

            self.passseq_9.setEnabled(False)
            self.passseq_10.setEnabled(False)
            self.passseq_11.setEnabled(False)
            self.passseq_12.setEnabled(False)
            self.passseq_13.setEnabled(False)
            self.passseq_14.setEnabled(False)
            self.passseq_15.setEnabled(False)
            self.passseq_16.setEnabled(False)

            self.button_pass.setExclusive(True)
        else:
            self.button_pass.setExclusive(False)

            self.passseq_9.setEnabled(True)
            self.passseq_10.setEnabled(True)
            self.passseq_11.setEnabled(True)
            self.passseq_12.setEnabled(True)
            self.passseq_13.setEnabled(True)
            self.passseq_14.setEnabled(True)
            self.passseq_15.setEnabled(True)
            self.passseq_16.setEnabled(True)

            self.button_pass.setExclusive(True)
        if exists(self.show_pic[0]):
            self.show_info = []
            dir_warn = self.out_folder + '/'+ self.cur_file + '_label.txt'
            try:
                with open(dir_warn, 'r') as file_to_read:
                    while True:
                        line = file_to_read.readline()
                        if not line:
                            break
                        line = line.strip('\n')
                        self.show_info.append(line.split())
                self.show_warn(self.info_warn_col,len(self.show_info))
            except:
                pass
        else:
            self.refresh_button()
            self.label_pic.clear()
            self.label_pic.refresh()
            self.label_picall.clear()          
            QMessageBox.warning(None,'错误路径提示','当前路径不存在，请检查')
            return
        if not self.show_pic[1]:
            return
        else:
            if not exists(self.cur_ImPath):
                self.refresh_button()
                self.label_pic.clear()
                self.label_pic.refresh()
                self.label_picall.clear()             
                self.update()
                QMessageBox.warning(None,'错误路径提示','当前路径不存在，请检查')
                return
            #######合并图片#######
            self.joint_pic(self.cur_file)
            #####################

        #########画框##############
        self.cur_imageID = 0
        self.load_image(self.cur_imageID)
        ########################### 


        # print('当前图片的名字' + self.cur_ImPath)
        self.label_pic.refresh()
        self.label_pic.LocalFileName = self.cur_ImPath
        self.update()
        self.label_state.setText('图片序号      ' + self.cur_ImPath)
        self.info_proc.setText(str(self.cur_imageID + 1) + '/' + str(self.image_num))

    '''
        拼接图片
    '''
    def joint_pic(self, cur_file):
        dir_root = self.show_pic[0] 
        files = os.listdir(dir_root)
        toImage = Image.new('RGB', (512, 350 * self.image_num))  # 构造图片的宽和高
        count = 0
        seq = (self.show_pic[1] - 5 ) / 32
        self.picall_save = self.out_folder + '/' + cur_file + '_jointPic'
        pic_root = self.picall_save + '/' + self.cur_file + '_' + str(int(seq)) + '_picall.jpg'
        if os.path.exists(pic_root):
            return
        for j in range(self.show_pic[1], self.show_pic[2]):
            filename = dir_root + '/' + cur_file + '-' + str(j) + '.jpg'
            # print(filename)
            fromImage = Image.open(filename)
            fromImage = fromImage.resize((512, 350))
            toImage.paste(fromImage, (0, count*350))
            count += 1
            ##########旋转角度#################
            changeImage = toImage.rotate(90, expand = 1)
            ##################################
            if not os.path.exists(self.picall_save):
                os.mkdir(self.picall_save)
            outfile = os.path.join(self.picall_save, cur_file + '_' + str(int(seq)) + '_picall.jpg')
            changeImage.save(outfile)


    '''
        读取图片文件并且显示在对应位置
    '''
    def load_image(self, point):
        seq = (self.show_pic[1] - 5 ) / 32
        bgr_image = self.cv_imread(self.picall_save + '/' + self.cur_file + '_' + str(int(seq)) + '_picall.jpg')
        if len(bgr_image.shape) == 2:  # 若是灰度图则转为三通道
            print("Warning:gray image", self.path)
            bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_GRAY2BGR)
        size = (int(self.label_picall.width()), int(self.label_picall.height()))
        bgr_image = cv2.resize(bgr_image, size, interpolation=cv2.INTER_AREA)
        rgb_img = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)  # 将BGR转为RGB
        point1 = (int(size[0] / self.image_num) * point   ,0)
        point2 = (int(size[0] / self.image_num) * (point + 1) , size[1])
        # print(point1, point2)
        cv2.rectangle(rgb_img, point1, point2, (0,0,255), 2)
        QImg = QImage(rgb_img.data, rgb_img.shape[1], rgb_img.shape[0], rgb_img.shape[1]*3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        self.label_picall.setPixmap(pixmap)
        self.label_picall.setScaledContents(True)




    def ShowMininizedWindow(self):
        self.showMinimized()

    def ShowMaximizedWindow(self):
        self.ShowMaximizedWindow()
        # self.window.showMaximized()

    def ShowRestoreWindow(self):
        if self.isMaximized():
            self.button_max.setIcon(QtGui.QIcon("./ico/max.ico"))
            self.showNormal()
        else:
            self.showMaximized()
            self.button_max.setIcon(QtGui.QIcon("./ico/mid.ico"))

    def CloseWindow(self):
        ####################################
        ####################################
        self.close()

    def mouseDoubleClickEvent(self, event):
        self.ShowRestoreWindow()
        return QWidget().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        self.isPressed = True
        self.startPos = event.globalPos()
        return QWidget().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.isPressed = False
        return QWidget().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        try:
            if self.isPressed:
                if self.isMaximized:
                    self.showNormal()
                movePos = event.globalPos() - self.startPos
                self.startPos = event.globalPos()
                self.move(self.pos() + movePos)
        except:
            pass
        return QWidget().mouseMoveEvent(event)

    '''
        关闭软件二次确认功能函数 closeEvent
        弹出提示框进行操作确认
    '''
    def closeEvent(self,QCloseEvent):
        try:
            if self.begin_thread.isRunning():
                self.begin_thread.quit()
        except:
            pass
        reply = QMessageBox.question(self,'高速列车车轮组件异常动态智能检测系统',
                                    '是否退出应用程序',
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

# 主界面，运行显示功能窗口


if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    func_window = Func_window()
    func_window.move((app.desktop().width() - func_window.width()) / 2, (app.desktop().height() - func_window.height()) / 4)
    func_window.show()
    sys.exit(app.exec_())
