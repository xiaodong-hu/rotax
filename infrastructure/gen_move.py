from numpy import full
from .stone import *
from .go_board import *
from .game_state import *

import random
from copy import copy, deepcopy
from functools import reduce
from operator import mul  


def gen_game_random(board: GoBoard) -> None:
    # Create initial game state with the starting board
    game_tree = GameTree([deepcopy(board.full_stone_to_color_map)])

    step = 0
    # step_truncation = reduce(mul, board.size)
    full_site_list = [(i,j) for i in range(0,board.size[0]) for j in range(0,board.size[1])]
    
    loop = 0
    board.consecutive_passes = 0 # serve as the indicator for the end of the game
    while board.consecutive_passes < 2 and loop < 5000:
        loop += 1
        test_board = deepcopy(board)
        allowed_site_list_for_current_move = test_board.generate_allowed_site_list(full_site_list)\
        # allowed_site_list_for_current_move = list(set(full_site_list).difference(set(board.full_stone_to_color_map.keys())))
        print(f"\n\nallowed sites for{test_board.current_move_color} : {len(allowed_site_list_for_current_move)}")
        if len(allowed_site_list_for_current_move) == 0:
            board.pass_move()
            game_tree.update_game_tree(board)
            
            board.consecutive_passes += 1
            step += 1
        else:
            test_pos = random.choice(allowed_site_list_for_current_move)
            ko_test_board = deepcopy(board)
            ko_test_board.try_place_stone_at(test_pos, show_board=False)
            if game_tree._is_board_repeated(ko_test_board):
                # strictly refuse such move!
                continue
            else:
                board.try_place_stone_at(test_pos, show_board=True)
                board.consecutive_passes = 0
                step += 1

        if board.consecutive_passes == 2:
            # Both players passed consecutively, game ends
            print(f"\n\033[1mConsecutive Passes Detected!\033[0m")
            print(f"\t\033[1mGame Ends at step = {step}.\033[0m\n")
            break

    board_score = board.score_board()
    print(f"\033[1mBoard Score: {board_score}\033[0m")
    ((_, black_score), (_, white_score)) = board_score
    score_diff = black_score - board.komi - white_score
    if score_diff > 0:
        print(f"\033[1mBlack Win by {score_diff}\033[0m (with komi {board.komi})")
    else:
        print(f"\033[1mWhite Win by {-score_diff}\033[0m (with komi {board.komi})")



# def gen_move_random(game_tree: GameTree) -> GameTree:
#     board = game_tree.state_list[-1]
#     while board.consecutive_passes < 2:
#         test_board = deepcopy(board)
#         allowed_site_list_for_current_move = test_board.generate_allowed_site_list(full_site_list)
#         print(f"\n\nallowed sites for{test_board.current_move_color} : {len(allowed_site_list_for_current_move)}")
#         if len(allowed_site_list_for_current_move) == 0:
#             board.pass_move()
#             board.consecutive_passes += 1
            
#         else:
#             test_pos = random.choice(allowed_site_list_for_current_move)
#             ko_test_board = deepcopy(board)
#             ko_test_board.try_place_stone_at(test_pos, show_board=False)
#             if game_tree._is_board_repeated(ko_test_board):
#                 # strictly refuse such move!
#                 continue
#             else:
#                 board.try_place_stone_at(test_pos, show_board=True)
#                 board.consecutive_passes = 0
                

#         if board.consecutive_passes == 2:
#             # Both players passed consecutively, game ends
#             print(f"\n\033[1mConsecutive Passes Detected!\033[0m")
#             print(f"\t\033[1mGame Ends at step = {step}.\033[0m\n")
#             break

