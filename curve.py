import random

import numpy as np
import scipy.interpolate as si

# import matplotlib.pyplot as plt
number_for_random = [4,5,6,7,8,9,10]

def pointer(first_x, first_y, last_coord):
    cv = np.array([[ first_x,  first_y],
#    [ random.randrange(200,400), random.randrange(200,400) ],
#    [ 50.,  10.],
#    [ 57.,   2.],
#    [ 40.,   4.],
   [ last_coord['x'] + random.choice(number_for_random), last_coord['y'] + random.choice(number_for_random)]]) # Создание массива из известных точек, узлов
    return scipy_bspline(cv, n=100, degree=3, periodic=False)



def scipy_bspline(cv, n=100, degree=3, periodic=False): # Контрольные точки, выборка, степень кривой, 
    """ Calculate n samples on a bspline

        cv :      Контрольные точки
        n  :      Number of samples to return Число возвращаемой выборки
        degree:   Степерь кривой
        periodic: True - Закрытая кривая
    """



    cv = np.asarray(cv) # Преобразование в массив
    count = cv.shape[0] # Количество точек

    # Closed curve
    if periodic:
        kv = np.arange(-degree,count+degree+1)
        factor, fraction = divmod(count+degree+1, count)
        cv = np.roll(np.concatenate((cv,) * factor + (cv[:fraction],)),-1,axis=0)
        degree = np.clip(degree,1,degree)

    # Opened curve
    else:
        degree = np.clip(degree,1,count-1)
        kv = np.clip(np.arange(count+degree+1)-degree,0,count-degree)

    # Return samples
    max_param = count - (degree * (1-periodic))
    spl = si.BSpline(kv, cv, degree) # Узлы, коэффициенты сплайна
    return spl(np.linspace(0,max_param,n))

# colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k') # Цвета сплайнов


# plt.plot(cv[:,0],cv[:,1], 'o-', label='Control Points') # Отрисовка контрольных точек 

# for d in range(1,3):
#     p = scipy_bspline(cv,n=100,degree=d,periodic=True)
#     x,y = p.T
#     plt.plot(x,y,'k-',label='Degree %s'%d,color=colors[d%len(colors)]) # Отрисовка сплайнов

# plt.minorticks_on()
# plt.legend()
# plt.xlabel('x')
# plt.ylabel('y')
# plt.xlim(35, 70)
# plt.ylim(0, 30)
# plt.gca().set_aspect('equal', adjustable='box')
# plt.show()


# p2 = scipy_bspline(cv) # 1 million samples: 0.0789 sec
