from .stone import *
from .go_board import *
import random
from copy import copy, deepcopy
from functools import reduce
from operator import mul

# def gen_move_random(board: GoBoard, nstep: int) -> None:
#     (L1, L2) = board.size
#     full_site_list = [(i,j) for i in range(0,L1) for j in range(0,L2)]
    
#     count = 0
#     while count < nstep:
#         occupied_site_list = board.full_stone_to_color_map.keys()
#         empty_site_list = list(set(full_site_list).difference(set(occupied_site_list)))
#         empty_site_list_to_be_scanned = deepcopy(empty_site_list)
        
#         # board_test  = deepcopy(board)
#         # test_pos = random.choice(empty_site_list_to_be_scanned)
#         # _is_move_legal = board_test.place_stone_at(test_pos, show_board=False)

#         while len(empty_site_list_to_be_scanned) > 0:
#             board_test  = deepcopy(board)
#             test_pos = random.choice(empty_site_list_to_be_scanned)
#             _is_move_legal = board_test.place_stone_at(test_pos, show_board=False)
#             if _is_move_legal:
#                 board.place_stone_at(test_pos, show_board=True)
#                 count += 1
#                 continue
#             else:
#                 empty_site_list_to_be_scanned.remove(test_pos)
                
    
#         if len(empty_site_list_to_be_scanned) == 0: # _is_game_end(board_test, board) == 0:
#             print(f"Game end at i = {count}.")
#         break

def gen_move_random(board: GoBoard) -> None:
    (L1, L2) = board.size
    full_site_list = [(i,j) for i in range(0,L1) for j in range(0,L2)]
    
    consecutive_passes = 0
    count = 0

    
    count_truncation = reduce(mul, board.size)
    while consecutive_passes < 2:
        occupied_site_list = board.full_stone_to_color_map.keys()
        empty_site_list = list(set(full_site_list).difference(set(occupied_site_list)))
        empty_site_list_to_be_scanned = deepcopy(empty_site_list)
        
        if len(empty_site_list_to_be_scanned) == 0:
            # No legal moves left, increase the pass count
            consecutive_passes += 1
        else:
            consecutive_passes = 0  # Reset consecutive pass count if there are legal moves

        while len(empty_site_list_to_be_scanned) > 0:
            board_test  = deepcopy(board)
            test_pos = random.choice(empty_site_list_to_be_scanned)
            _is_move_legal = board_test.place_stone_at(test_pos, show_board=False)
            if _is_move_legal:
                print(f"gen move at {test_pos}")
                board.place_stone_at(test_pos, show_board=True)
                count += 1
                break
            else:
                empty_site_list_to_be_scanned.remove(test_pos)
        
        if consecutive_passes == 2:
            if count < count_truncation:
                # Both players passed consecutively, game ends
                print(f"Game ends at i = {count}.")
                break
            else:
                print(f"Game ends reaching due to the nstep limit.")
                break

    # You would add here the logic to calculate the final score based on both stone count and controlled territory.
    # ...



def _is_game_end(old_board: GoBoard, new_board: GoBoard) -> bool:
    return old_board.full_stone_to_color_map == new_board.full_stone_to_color_map
        

    