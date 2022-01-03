import csv
import sys
import numpy as np

def read_csv(inp):
    f = open(inp, "r")
    reader = csv.reader(f, delimiter = ',')
    readerlist = list(reader)
    f.close()
    y = []
    x = []
    for line in readerlist:
      y.append(line.pop(0))
      line.insert(0, 1)
      x.append(line)
    y = np.array(y, dtype = float)
    x = np.array(x, dtype = float)
    return x,y

def train(x,y, hidden, num_epoch, learning_rate, xval, yval, init_flag):
    if init_flag == 1:
        alpha = np.random.uniform( low=-0.1, high=0.1, size=(hidden, len(x[0])))
        alpha[:,0] = 0.0
        beta = np.random.uniform( low=-0.1, high=0.1, size=(4, hidden+1))
        beta[:,0] = 0.0
    else:
        alpha = np.zeros( (hidden, len(x[0])), dtype = float)
        beta = np.zeros( (4, hidden+1), dtype = float)
    s1 = np.zeros(alpha.shape, dtype = float)
    s2 = np.zeros(beta.shape, dtype = float)
    Jtrain_all = []
    Jtest_all = []
    for e in range(num_epoch):
        print("epoch", e)
        yhat_total = []
        for i in range(len(y)):
            a, b, z, yhat, J = NNforward(x[i], y[i], alpha, beta)
            yhat_total.append(yhat)
            galpha, gbeta = NNbackward(x[i], y[i] ,alpha, beta, a, b, z, yhat)
            #update adagrad
            s1 += np.square(galpha)
            s2 += np.square(gbeta)
            alpha -= (learning_rate / np.sqrt(s1 + 0.00001)) * galpha
            beta -= (learning_rate / np.sqrt(s2 + 0.00001)) * gbeta


        Jtrain = 0.0
        for i in range(len(y)):
            a, b, z, yhat, J = NNforward(x[i], y[i], alpha, beta)
            Jtrain += J
        Jtrain = Jtrain / float(len(y))
        Jtrain_all.append(Jtrain)

        Jtest = 0.0
        for i in range(len(yval)):
            a, b, z, yhat, J = NNforward(x[i], yval[i], alpha, beta)
            print(J)
            Jtest += J
        Jtest = Jtest / float(len(yval))
        Jtest_all.append(Jtest)
    return alpha, beta, Jtrain_all, Jtest_all

def NNforward(x, y, alpha, beta):
    a = np.zeros(len(alpha), dtype = float)
    for j in range(len(a)):
        a[j] = np.dot(alpha[j], x)
    z = np.zeros(len(x)+1, dtype = float)
    z = np.array( 1 / (1 + np.exp(-a)))
    z = np.insert(z, 0, 1., axis=0)
    b = np.zeros(len(beta), dtype = float)
    for k in range(len(b)):
        b[k] = np.dot(beta[k], z)
    yhat = np.zeros(4,dtype = float)
    for k in range(len(yhat)):
        yhat[k] = np.exp(b[k]) / sum(np.exp(b)) 
    y1 = np.zeros(4, dtype=float)
    y1[int(y)] = 1
    J = -np.dot(y1, np.log(yhat))
    return a, b, z, yhat, J

def NNbackward(x, y ,alpha, beta, a, b, z, yhat):
    gJ = 1
    gb = np.array(yhat)
    gb[int(y)] -= 1
    gbeta = np.outer(gb, z)
    beta = np.delete(beta,0,1)
    gz = np.dot(gb, beta)
    z = np.delete(z,0)
    ga = gz * z*(1-z)
    galpha = np.outer(ga, x)
    return galpha, gbeta


def predict(x, y, alpha, beta, out):
    error = 0
    prediction = []
    for i in range(len(x)):
        a = np.zeros(len(alpha), dtype = float)
        for j in range(len(a)):
            a[j] = np.dot(alpha[j], x[i])
        z = np.zeros(len(x[i]+1), dtype = float)
        z = np.array( 1 / (1 + np.exp(-a)))
        z = np.insert(z, 0, 1., axis=0)
        b = np.zeros(len(beta), dtype = float)
        for k in range(len(b)):
            b[k] = np.dot(beta[k], z)
        yhat = np.zeros(4,dtype = float)
        for k in range(len(yhat)):
            yhat[k] = np.exp(b[k]) / sum(np.exp(b)) 
        prediction.append(int(np.argmax(yhat)))
        if int(y[i]) != int(np.argmax(yhat)):
            error += 1

    f = open(out, "w")
    writer = csv.writer(f)
    for e in prediction:
      f.write(str(e) + '\n')
    f.close()

    return float(error) / float(len(y))
    



def output(out, tmce, vmce, train_error, valid_error, num_epoch):
    f = open(out, "w")
    writer = csv.writer(f)
    print(len(tmce), len(vmce))
    for i in range(num_epoch):
        f.write("epoch=" + str(i+1) + " crossentropy(train): " + str(tmce[i]) + "\n")
        f.write("epoch=" + str(i+1) + " crossentropy(validation): " + str(vmce[i]) + "\n")
    
    f.write("error(train): " + str(train_error) + "\n")
    f.write("error(test): " + str(valid_error))
    f.close()

if (__name__ == '__main__'):
  train_input = sys.argv[1]
  valid_input = sys.argv[2]
  train_out = sys.argv[3]
  valid_out = sys.argv[4]
  metrics_out = sys.argv[5]
  num_epoch = int(sys.argv[6])
  hidden = int(sys.argv[7])
  init = int(sys.argv[8])
  learning_rate = float(sys.argv[9])
  x,y = read_csv(train_input)
  xval, yval = read_csv(valid_input)
  alpha, beta, tmce, vmce = train(x,y, hidden, num_epoch, learning_rate, xval, yval, init)
  train_error = predict(x, y, alpha, beta, train_out)
  valid_error = predict(xval, yval, alpha, beta, valid_out)
  output(metrics_out, tmce, vmce, train_error, valid_error, num_epoch)


