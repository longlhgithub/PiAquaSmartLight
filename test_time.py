from timing import *

x = Timer(fromFile='test.yaml')
print(x)
x.save_settings('test.yaml')