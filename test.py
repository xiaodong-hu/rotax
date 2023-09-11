from infrastructure.stone import *
from infrastructure.go_board import *

if __name__ == "__main__":
    # a = Color(1)
    # print(a)
    
    # a = Stone(Color(1),(1,2))
    # c = Stone(Color(-1),(1,2))
    # b = Stone(Color(0),(1,2))
    # print(a,b,c)
    
    A = GoBoard((19,19))
    A.gen_move(Color.Black, (2,3))