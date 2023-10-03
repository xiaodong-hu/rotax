import random

from .go_board_fast import *
from .game_tree import *
from .game_score import *

def gen_move_random(go_board: GoBoard, game_tree: GameTree) -> Union[tuple[int,int], None]:
    allowed_searching_site_list = list(game_tree.generate_allowed_searching_site_hashset(go_board))
    allowed_searching_site_length = len(allowed_searching_site_list)
    print(f"\n\nallowed sites for{go_board.current_move_color} : {allowed_searching_site_length}")
    if allowed_searching_site_length < 10:
        print(f"\t `allowed_searching_site_hashset` (when < 10) = {allowed_searching_site_list}")

    if allowed_searching_site_length == 0:
        return None
    else:
        return random.choice(allowed_searching_site_list)


def gen_game_random(go_board: GoBoard):
    # initialize the game tree
    game_tree = GameTree(go_board)

    go_board.consecutive_passes = 0
    n_move = 0
    while go_board.consecutive_passes < 2 and n_move < 2000:
        trial_move = gen_move_random(go_board, game_tree)
        match trial_move:
            case None:
                go_board.pass_move()
                game_tree.update_game_tree(go_board.full_stone_pos_to_color_hashmap)
                
                go_board.consecutive_passes += 1
                # n_move += 1
            case _:
                print(f"move{go_board.current_move_color} is placed at {trial_move}")
                go_board.place_stone_at(trial_move, show_board=True)
                game_tree.update_game_tree(go_board.full_stone_pos_to_color_hashmap)
                
                go_board.consecutive_passes = 0
                n_move += 1

        if go_board.consecutive_passes == 2:
            # Both players passed consecutively, game ends
            print(f"\n\033[1mConsecutive Passes Detected!\033[0m")
            print(f"\t\033[1mGame Ends at n_move = {n_move}.\033[0m\n")
            break

    score_board(go_board)
    