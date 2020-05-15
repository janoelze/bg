import threading
from threading import Thread
import random
import time

# check = threading.Condition()

GLOBSTATE = {
    'a': 1,
    'b': 1
}

def func1():
    while True:
        GLOBSTATE['a'] = random.randint(0,100)
        time.sleep(1)

def func2():
    while True:
        GLOBSTATE['b'] = random.randint(0,100)
        time.sleep(1)

def func3():
    while True:
        print(GLOBSTATE)
        time.sleep(1)

if __name__ == '__main__':
    Thread(target = func1).start()
    Thread(target = func2).start()
    Thread(target = func3).start()
