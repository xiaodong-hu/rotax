from infrastructure.stone import *
from infrastructure.go_board import *

if __name__ == "__main__":
    
    a = Stone(Color.White, (1,2))
    b = Stone(Color.White, (3,2))
    c = Stone(Color.Black, (4,2))
    d = Stone(Color.White, (2,2))
    
    A = GoBoard((19,19))
    
    A.update_block_list(a)
    A.update_block_list(b)
    A.update_block_list(c)
    A.update_block_list(d)
    A.update_full_stone_to_color_map()
    A.update_block_nearest_neighbor_list_and_liberty_list()
    print(A)
    print(A.block_list)
    print(A.full_stone_to_color_map)
    print(A.block_nearest_neighbor_list)
    print(A.block_liberty_list)