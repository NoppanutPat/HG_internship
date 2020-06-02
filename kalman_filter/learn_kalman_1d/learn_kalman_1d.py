import matplotlib.pyplot as plt
import random

def f(x):
    return 32*(x)+10

class Kalman1D():

    def __init__(self):
        self.x0 = 10
        self.r0 = 0.01
        self.noise = 0.00001
        self.p0 = 1000
        self.result = []
        self.count = 0
        self.measure = []

    def predict(self):
        self.p0 = self.p0 + self.noise

    def measurement(self):

        self.z = f(self.count) + (random.random() * ((-10)**(random.randint(1,2))))
        self.measure.append(self.z)
        self.count += 1
        return self.measure
    
    def update(self):
        self.k = self.p0 / (self.p0 + self.r0)
        self.x0 = self.x0 + self.k*(self.z - self.x0)
        self.p0 = ( 1 - self.k)*self.p0
        self.result.append(self.x0)
        print(self.result)
        return self.result

real_data = [ f(i) for i in range(20) ]

print(real_data)

kalman = Kalman1D()

for i in range(20):

    kalman.predict()
    measure_data = kalman.measurement()
    result = kalman.update()
    
print(result)

plt.figure()
plt.plot(real_data,color="b")
plt.plot(result,color='r',marker=".")
plt.plot(measure_data,color='g',marker=".")
plt.show()