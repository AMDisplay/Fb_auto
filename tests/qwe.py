
class A():
    def __init__(self, size, max_n) -> None:
        self.size = size,
        self.max_n = max_n

    def push_back(self,x):
        try:
            self.size == self.max_n
            print('ne ok')
        except:
            raise Exception('error')
        self.__queue[self.__tail] = x
        self.__tail = (self.__tail + 1) % self.__max_n
        self.size += 1 
        print('OK')

A(size=1,max_n=2)