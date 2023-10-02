from infrastructure.stone import *
# from infrastructure.go_board import *
from infrastructure.gen_move import *
from infrastructure.go_board_fast import *



if __name__ == "__main__":

    A = GoBoard((19,19))
    gen_game_random(A)
    print(A)

    


