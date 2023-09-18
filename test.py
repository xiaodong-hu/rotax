from infrastructure.stone import *
from infrastructure.go_board import *
from infrastructure.gen_move import *

def goboard_class_construction_test():
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
    A.update_nearest_neighbor_list_and_liberty_list_and_eye_list()
    print(A)
    print(A.block_list)
    print(A.full_stone_to_color_map)
    print(A.block_nearest_neighbor_list)
    print(A.block_liberty_list)
    

def place_stone_test():
    A = GoBoard((19,19))
    
    # alternative move
    A.try_place_stone_at((3,2))
    A.try_place_stone_at((16,16))
    A.try_place_stone_at((3,16))
    A.try_place_stone_at((2,2))
    A.try_place_stone_at((15,3))
    A.pass_move() # pass to switch color

    # force move
    A.try_place_stone_with_color_at((2,3), Color.Black)
    A.try_place_stone_with_color_at((3,3), Color.Black)
    A.try_place_stone_with_color_at((2,1), Color.Black)
    print(A.block_list, A.block_liberty_list)

    # single-stone capture occurs
    A.try_place_stone_with_color_at((1,2), Color.Black)
    print(A.block_list, A.block_liberty_list)




if __name__ == "__main__":
    # goboard_class_construction_test()
    # place_stone_test()
    # suicide_forbidden_test()

    A = GoBoard((3,3))
    gen_move_random(A)

    


