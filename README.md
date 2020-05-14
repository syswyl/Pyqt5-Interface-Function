# Pyqt5 
综述：利用python的pyqt库实现一个简洁的pyqt5界面，代码在本地测试通过，其中功能实现部分代码写的粗糙，仅为了实现功能，所以可扩展性较差，可能需要反复阅读源码才可以了解不同功能间的衔接关系，如有问题可以和我联系

因为项目中所用到的图片数据并不开放，所以只提供部分数据保证能正常运行
在image_out中给出了车辆右侧下的图片，考虑到下载可能缓慢，给出baidu云链接，这个数据集好像也不公开，还是算了吧，想要的可以私聊我</br>
前期图像处理：高铁车身采集图像（分为很多个部分，如右上，右下，车底中等），对图象进行目标识别和分类，绘制对应目标框，对每个目标进行缺陷识别。</br>
软件功能：导入已有的检测结果文件，对图片进行显示，对缺陷结果进行二次确认，并写入本地文档保存。在Demonstration.rar中是整个软件的演示视频。</br>


## 上手指南
以下指南将帮助你在本地机器上安装和运行该项目，进行开发和测试。

### 运行要求
以下环境为必须项
- python 3 环境
- 安装必要的依赖PyQt 5包，注意PyQt 4 和PyQt 5有许多差异，本项目基于PyQt 5环境，无法在4环境中正常运行
- 安装其他python库
安装步骤不做赘述，自行搜索解决

### 界面介绍
界面中主要控件通过安装PyQt 之后自带的软件拖动生成，安装完成之后在你的python环境下的scripts中有直接运行的.exe软件。

关于软件的使用请自行解决，最好实际设计一个界面，然后花时间去探索各个控件的实际作用和使用方法。

软件主体为两个界面，login界面和function界面，其中的美化及详细的界面跳转和功能实现在之后详细介绍。

![登录界面](https://github.com/syswyl/Pyqt5-Interface-Function/blob/master/readme_images/login.jpg)

![功能界面](https://github.com/syswyl/Pyqt5-Interface-Function/blob/master/readme_images/function.jpg)

### 实现步骤

1. 代码生成

  这里我使用的是vscode进行代码编写，配置完成相关环境之后，可以直接右键相关.ui文件，就可以直接转化为python代码
![直接生成python代码](https://github.com/syswyl/Pyqt5-Interface-Function/blob/master/readme_images/ui_to_python.jpg)
也可以使用命令行指令：
> pyuic5  -o  ui_window.ui  py_window.py

（没有测试过，来源于CSDN）</br>
利用此方法生成的py文件如果我们重新修改界面后再次生成时，其中自己编写的功能函数都不会被保存，这在其生成代码中也给出了相应警告

> `WARNING! All changes made in this file will be lost!`

所以在这里，我们通过再再新建一个py文件方式解决这个问题，因为使用QtDesigner程序(即安装pyqt之后自带的图形化软件)只是对界面进行简单的初步生成，所以我们可以新建一个my_Window的类，继承来自ui文件生成的类。这样，我们一切的修改都在子类中进行，最后也直接运行子类，从而保证自己修改和添加的功能不会遗失。

2. 实例化代码介绍

    首先我们对类和函数及衔接进行简单介绍:
- PyQt5是一个大的模块，是Qt在Python中的桥梁。
- QtWidgets是PyQt5下面的一个模块，包含了用于构建界面的一系列UI元素组件。
- QApplication是QtWidgets模块下面的一个类。

QApplication用法

```python
app = QApplication(sys.argv)   # 实例化一个应用对象
w = QWidget()   # 窗口界面的基本控件，它提供了基本的应用构造器。默认情况下，构造器是没有父级的，没有父级的构造器被称为窗口（window）。
w.show()   # 让控件在桌面上显示出来。控件在内存里创建，之后才能在显示器上显示出来。
sys.exit(app.exec_())   # 确保主循环安全退出
```

任何一个窗体建设中都会有这么类似的4句。</br>
sys.argv是一组命令行参数的列表。Python可以在shell里运行，这个参数提供对脚本控制的功能。
[PyQT5.QtWidgets.QApplication结构及用法](https://blog.csdn.net/The_Time_Runner/article/details/89282988)

3. 登录界面及功能

- 界面

   登录界面比较简单，因为背景比较复杂，不具有模块性，所以通过直接插入一张背景图的方式解决。在qt中画图的方式有多种，在这里使用paintEvent函数，它是QWidget类中的虚函数，用于ui的绘制，会在多种情况下被其他函数自动调用。</br>
当然还有其他很多绘制方式，请自行实践解决（QPixmap/QImage/QPicture）

```python
def paintEvent(self, event):
    painter = QPainter(self)
    pixmap = QPixmap("./software_images/background.png")
    painter.drawPixmap(self.rect(), pixmap)
```

- 功能

    登录是通过 QPushButton 控件实现的，这里不要求对密码进行自动填充（1），也不进行后台数据库判断（2），只是简单的进行本地程序检查。以上所描述功能（1）（2）都可以实现，需要的可自行百度解决。
```python
# 将点击事件与槽函数进行连接
    self.button_login.clicked.connect(self.login_func)
    self.button_login.setShortcut(QtCore.Qt.Key_Return)
    self.account = "admin"
    self.password = "test123"
...
# 省略

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
```

- 窗口切换

利用QWidget类中的show()函数，可以实现窗口的显示，在正确判定之后，关闭当前login窗口，同时显示function窗口，这里所用到的move()函数设置窗口的左上角坐标，为了让窗口在屏幕上显示位置恒定居中一点。
```python
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Login_window() #生成一个实例
    func_window = Func_window()
    func_window.move((app.desktop().width() - func_window.width()) / 2, (app.desktop().height() - func_window.height()) / 4)
    window.move((app.desktop().width() - window.width()) / 2 , (app.desktop().height() - window.height()) / 2 )
    window.show()
    sys.exit(app.exec_())
```

4. 功能界面展示

由于功能界面比较复杂，不进行一一解释，我尽量在注释中描述比较清晰，如果想详细了解的请阅读代码function.py。</br>
界面主要有以下几个关键部分</br>
-	缺陷图片显示及切换
-	缺陷部位信息
-	导入导出
-	缩放关闭和软件名字

![演示功能](https://github.com/syswyl/Pyqt5-Interface-Function/blob/master/readme_images/function_part.jpg)

- 缺陷图片显示及切换

软件中有两处图片，上面的图片是整个部分的完整图片显示，用于用户在浏览时候能够准确知道当前的车身位置，类似于缩略图方式。（由多张图片拼接而成，划分区域的外边框是通过获取整个图片大小然后根据当前图片序号进行坐标定位的，所以可能会有稍微偏移）</br>
下面的部分是当前的缺陷图片，原图像是2048*1400的大小，在软件中通过适当的处理，可以实现鼠标滚轮缩放和左键点击拖动。
- 缺陷部位信息

这一部分展示了当前车部位的所有可能存在缺陷，点击对应的序号可以弹出存在缺陷的图片（可缩放查看），进行二次确认。

- 导入导出

导入功能主要用于导入现有的文件夹，因为软件不实现检测功能（耗时较久，需要开多线程），所以开始按钮其实并无实际作用，这里采取延时几秒进行模拟仿真；导出主要是将确认后的缺陷结果写入本地文档中进行保存，可自己选择路径和命名。

- 缩放关闭和软件名字

程序自带的缩放区域按钮较丑，所以自己实现了一个标题栏，将原来的边框进行隐藏，用到的方法是选择自己的图片，然后将对应的点击事件与槽函数进行衔接即可。


