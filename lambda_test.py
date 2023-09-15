
def wut():
  print("wut")


x = [[1,2,lambda : print('Hello World')],[1,2,lambda : print('potato')],[1,2,wut]]

x[1][2]()
x[0][2]()
x[2][2]()