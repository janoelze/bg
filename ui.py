# http://anh.cs.luc.edu/handsonPythonTutorial/graphics.html

from graphics import *

# pt = Point(100, 50)
# pt.draw(win)

class UIManager(object):
    def __init__(self):

        self.win = GraphWin('',300,300)
    def update(self, state):
        # rect = makeRect(Point(20, 50), 250, 200)
        flowerImage = Image(Point(100,100), "waveforms/HiHat 17.png")
        # rect = Rectangle(Point(200, 90), Point(220, 100))
        # rect.setFill("blue")
        # rect.draw(self.win)
        flowerImage.draw(self.win)

        # rect.draw(self.win)
        # self.win = GraphWin()
