
from .stone import *
from .go_board_fast import *


def score_board(go_board: GoBoard):
    black_stone = 0
    white_stone = 0
    black_block_penalty = 0
    white_block_penalty = 0
    
    for stone_block in go_board.block_id_to_stone_block_hashmap.values():
        match stone_block.block_color:
            case Color.Black: 
                black_stone += len(stone_block.stone_pos_hashset)
                black_block_penalty += 1
            case Color.White: 
                white_stone += len(stone_block.stone_pos_hashset)
                white_block_penalty += 1
    
    print(f"{go_board.block_id_to_stone_block_hashmap.keys()}")
    print(f"block liberties: {go_board.block_id_to_block_liberty_site_hashset_hashmap}")
    print(f"block eyes: {go_board.block_id_to_block_single_eye_site_hashset_hashmap}")

    print(f"\033[1mBoard Stones Count: {Color.Black} {black_stone}, {Color.White} {white_stone}\033[0m")
    print(f"\033[1mBlock Penalty: {Color.Black} {black_block_penalty}, {Color.White} {white_block_penalty}\033[0m")

    total_score_diff = (black_stone - black_block_penalty) - (white_stone - white_block_penalty) - go_board.komi
    if total_score_diff > 0:
        print(f"\033[1mBlack Win by {total_score_diff}\033[0m (with komi {go_board.komi})")
    else:
        print(f"\033[1mWhite Win by {-total_score_diff}\033[0m (with komi {go_board.komi})")


