import time

from infrastructure.stone import *
# from infrastructure.go_board import *
from infrastructure.gen_move import *
from infrastructure.game_tree import *
from infrastructure.go_board_fast import *


if __name__ == "__main__":

    A = GoBoard((19,19))

    init_time = time.time()
    gen_game_random(A)
    end_time = time.time()
    print(f"\nTime [s] for game generation: \n\033[1m{end_time-init_time}\n\033[0m")
    

    


