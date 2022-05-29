import numpy as np 

def sigmoid(x): 
    return 1/(1+np.exp(-x))

def mse_loss(y_true, y_pred):
    return ((y_true-y_pred)**2).mean()



class Neuron: 
    def __init__(self,weights,bias):
        self.weights = weights 
        self.bias = bias 


    def feedforward(self,inputs): 
        total = np.dot(self.weights,inputs) + self.bias 
        return sigmoid(total)

weights = np.array([0,1]) #w1 = 0, w2 = 1 
bias = 4
n = Neuron(weights,bias)

x = np.array([2,3]) #x1 = 2, x2 = 3 
print(n.feedforward(x))


class SampleNeuralNetwork:
    '''
    A neural network with:
        - 2 inputs
        - a hidden layer with 2 neurons (h1, h2)
        - an output layer with 1 neuron (o1)
    Each neuron has the same weights, bias and activation function:
        - w = [0, 1]
        - b = 0
    '''
    def __init__(self, weights,bias):
        self.h1 = Neuron(weights,bias)
        self.h2 = Neuron(weights,bias)
        self.o1 = Neuron(weights,bias)

    def feedforward(self, x):
        o1_input = np.array([self.h1.feedforward(x), self.h2.feedforward(x)])
        print(o1_input)
        return self.o1.feedforward(o1_input)

nn = SampleNeuralNetwork(weights,0)
print(nn.feedforward(x))


y_true = np.array([1, 0, 0, 1])
y_pred = np.array([0, 0, 0, 0])
print(mse_loss(y_true, y_pred)) # 0.5