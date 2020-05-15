import sys, time, random

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from threading import Thread

STATE = {
    'bpm': 120
}

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(400, 300)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.draw_something()
        # while True:
        #     self.draw_something()
            # time.sleep(0.1)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.draw_something)
        self.timer.start(100)

    def draw_something(self):
        painter = QtGui.QPainter(self.label.pixmap())

        def drawTracks(painter):
            x = random.randint(0,100)
            y = random.randint(0,100)
            

            width = 40
            y = 0
            for n in range(0,4):
                for x in range(0,8):
                    painter.drawImage(
                        QtCore.QRect(x*width, y, width, width),
                        QtGui.QImage("waveforms/Abletunes TSD Snare 27.gif")
                    )
                y = y + width

            # image = QtGui.QImage('waveforms/Abletunes TSD Snare 27.gif')
            # output = QtGui.QImage(image.size(), QtGui.QImage.Format_ARGB32)
            # output.fill(QtCore.Qt.transparent)
            # # painter = QtGui.QPainter(output)

            # points = [(444, 203), (623, 243), (691, 177), (581, 26), (482, 42)]
            # polygon = QtGui.QPolygonF([QtCore.QPointF(*point) for point in points])

            # path = QtGui.QPainterPath()
            # path.addPolygon(polygon)
            # painter.setClipPath(path)
            # painter.drawImage(QtCore.QPoint(), image)
            # painter.end()
            # output.save('out.png')

        def drawCursor(painter):
            pen = QPen(Qt.white, 3)
            painter.setPen(pen)
            painter.drawLine(random.randint(0,100), random.randint(0,100), random.randint(0,100), random.randint(0,100))

        def drawText(painter):
            # bpm
            painter.drawText(random.randint(0,100), random.randint(0,100), str(STATE['bpm']))

        drawTracks(painter)
        drawCursor(painter)
        drawText(painter)
        
        painter.end()
        self.update()

def audioManager():
    while True:
        STATE['bpm'] = random.randint(0,1000)
        print('a')
        time.sleep(1)

if __name__ == '__main__':
    Thread(target = audioManager).start()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
