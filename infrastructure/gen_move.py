from numpy import full
from .stone import *
from .go_board_fast import *
from .game_state import *

import random
from copy import copy, deepcopy
from functools import reduce
from operator import mul  



def generate_allowed_searching_site_hashset(go_board: GoBoard, game_tree: GameTree) -> set[tuple[int,int]]:
    full_searching_site_hashset = set([(i,j) for i in range(0, go_board.size[0]) for j in range(0, go_board.size[1])])
    allowed_searching_site_hashset = full_searching_site_hashset.difference(go_board.full_stone_pos_to_color_hashmap.keys())
    allowed_searching_site_hashset_copy = deepcopy(allowed_searching_site_hashset)

    for site in allowed_searching_site_hashset_copy:
        nearby_site_list = go_board.get_nearby_sites_for_position(site)

        # first, check is the site is fully surrounded by other stones (if not, allow to move)
        adjacent_count = 0
        for pos in nearby_site_list:
            if pos in go_board.full_stone_pos_to_color_hashmap:
                adjacent_count += 1

        # now the site is fully surrounded
        if adjacent_count == len(nearby_site_list): 
            # if the site is surrounded by different colors
            if not go_board._is_single_eye(site):
                nearby_block_id_list = go_board.full_site_to_nearby_block_id_list_hashmap[site]
                # _is_pure_suicide = True
                block_counter_of_current_move_color_with_one_liberty = 0
                block_counter_of_opponent_color_with_one_liberty = 0
                for block_id in nearby_block_id_list:
                    if len(go_board.block_id_to_block_liberty_site_hashset_hashmap[block_id]) == 1:
                        block_color = go_board.block_id_to_stone_block_hashmap[block_id].block_color
                        if block_color == go_board.current_move_color.alternate():
                            # _is_pure_suicide = False
                            # break
                            block_counter_of_opponent_color_with_one_liberty += 1
                        if block_color == go_board.current_move_color:
                            block_counter_of_current_move_color_with_one_liberty += 1

                # the site will be pure suicide
                if block_counter_of_current_move_color_with_one_liberty >= 1 and block_counter_of_opponent_color_with_one_liberty == 0:
                    # print for debug
                    # print(f"searching site set found suicide at {site} !\n")
                    if site in allowed_searching_site_hashset:
                        allowed_searching_site_hashset.remove(site)
                        
            # if the site is surrounded by the same colors
            if go_board._is_single_eye(site):
                single_eye_color = go_board._single_eye_color(site)
                
                # if is opponent's single eye
                if single_eye_color == go_board.current_move_color.alternate():
                    nearby_block_id_list = go_board.full_site_to_nearby_block_id_list_hashmap[site]
                    block_counter_of_opponent_color_with_one_liberty = 0
                    block_counter_of_opponent_color_with_one_liberty_and_one_stone = 0
                    _is_pure_suicide = True
                    for block_id in nearby_block_id_list:
                        if len(go_board.block_id_to_block_liberty_site_hashset_hashmap[block_id]) == 1:
                            _is_pure_suicide = False # capture occurs for current move to place here
                            block_counter_of_opponent_color_with_one_liberty += 1
                            if len(go_board.block_id_to_stone_block_hashmap[block_id].stone_pos_hashset) == 1:
                                block_counter_of_opponent_color_with_one_liberty_and_one_stone += 1
                            
                    if _is_pure_suicide:
                        # illegal for current player to place a move
                        if site in allowed_searching_site_hashset:
                            allowed_searching_site_hashset.remove(site)
                    if not _is_pure_suicide:
                        # even if the site is not suicide, it can still be a ko here!
                        if block_counter_of_opponent_color_with_one_liberty == block_counter_of_opponent_color_with_one_liberty_and_one_stone == 1:
                            ko_test_go_board = deepcopy(go_board)
                            ko_test_go_board.place_stone_at(site, show_board=False)
                            if game_tree._is_board_repeated(ko_test_go_board):
                                # strictly refuse such move!
                                continue

                # if is current player's single eye
                if single_eye_color == go_board.current_move_color:
                    nearby_block_id_list = go_board.full_site_to_nearby_block_id_list_hashmap[site]
                    block_counter_of_current_move_color_with_one_liberty = 0
                    for block_id in nearby_block_id_list:
                        if len(go_board.block_id_to_block_liberty_site_hashset_hashmap[block_id]) == 1:
                            block_counter_of_current_move_color_with_one_liberty += 1
                    if block_counter_of_current_move_color_with_one_liberty == len(nearby_block_id_list):
                        # only one liberty is left for all nearby block of current move color, so the site will be pure suicide (and certainly legal for the opponent to place a move)
                        if site in allowed_searching_site_hashset:
                            allowed_searching_site_hashset.remove(site)

                    # now the site is illegal for the opponent to place a move
                    test_board = deepcopy(go_board)
                    # before the test move
                    bool_indicator_list_for_containing_suicide_block = [
                        len(block_single_eye_site_hashset) == 2 
                        for block_single_eye_site_hashset in go_board.block_id_to_block_single_eye_site_hashset_hashmap.items()
                    ]
                    if any(bool_indicator_list_for_containing_suicide_block):
                        test_board.place_stone_at(site, show_board=False)
                        merged_block_id_list = test_board.full_site_to_nearby_block_id_list_hashmap.get(site, [])
                        if len(merged_block_id_list) > 0:
                            merged_block_id = merged_block_id_list[0] # must be only one block left if is a suicide move
                            merged_block_liberty = len(test_board.block_id_to_block_liberty_site_hashset_hashmap[merged_block_id])
                            merged_block_single_eye = len(test_board.block_id_to_block_single_eye_site_hashset_hashmap[merged_block_id])
                            
                            if merged_block_liberty < 2 and merged_block_single_eye < 2:
                                # print for debug
                                # print(f"{go_board.current_move_color} found site {site} is suicide so ignore it! (liberty and eye after merge: ({merged_block_liberty}, {merged_block_single_eye}))")
                                if site in allowed_searching_site_hashset:
                                    allowed_searching_site_hashset.remove(site)

    return allowed_searching_site_hashset



def gen_game_random(go_board: GoBoard) -> None:
    # Create initial game state with the starting board
    game_tree = GameTree([go_board.full_stone_pos_to_color_hashmap])

    n_move = 0
    go_board.consecutive_passes = 0 # serve as the indicator for the end of the game
    while go_board.consecutive_passes < 2 and n_move < 3000:
        # loop += 1
        # allowed_searching_site_hashset = go_board.generate_allowed_site_list(full_site_hashset)
        
        allowed_searching_site_hashset = generate_allowed_searching_site_hashset(go_board, game_tree)
        print(f"\n\nallowed sites for{go_board.current_move_color} : {len(allowed_searching_site_hashset)}")
        if len(allowed_searching_site_hashset) < 10:
            print(f"\t `allowed_searching_site_hashset` (when < 10) = {allowed_searching_site_hashset}")

        if len(allowed_searching_site_hashset) == 0:
            go_board.pass_move()
            game_tree.update_game_tree(go_board)
            
            go_board.consecutive_passes += 1
            n_move += 1
        else:
            test_pos = random.choice(list(allowed_searching_site_hashset))
            
            print(f"move{go_board.current_move_color} is placed at {test_pos}")
            go_board.place_stone_at(test_pos, show_board=True)
            game_tree.update_game_tree(go_board)
            
            go_board.consecutive_passes = 0
            n_move += 1

        if go_board.consecutive_passes == 2:
            # Both players passed consecutively, game ends
            print(f"\n\033[1mConsecutive Passes Detected!\033[0m")
            print(f"\t\033[1mGame Ends at n_move = {n_move}.\033[0m\n")
            break

    board_score = score_board(go_board)
    print(f"\033[1mBoard Score: {board_score}\033[0m")
    ((_, black_score), (_, white_score)) = board_score
    score_diff = black_score - go_board.komi - white_score
    if score_diff > 0:
        print(f"\033[1mBlack Win by {score_diff}\033[0m (with komi {go_board.komi})")
    else:
        print(f"\033[1mWhite Win by {-score_diff}\033[0m (with komi {go_board.komi})")



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

