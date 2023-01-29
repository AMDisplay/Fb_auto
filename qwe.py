# получить текущее имя потока
import threading
threading.current_thread().name

def qwe():
    print(f'Привет {threading.current_thread().name}')

q1 = threading.Thread(target=qwe)
q2= threading.Thread(target=qwe)
q3 =threading.Thread(target=qwe)
q4 = threading.Thread(target=qwe)
q1.start()
q2.start()
q3.start()
q4.start()