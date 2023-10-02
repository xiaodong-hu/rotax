from .go_board_fast import *


class GameTree:
    board_state_list: list[dict[tuple[int,int], Color]]

    def __init__(self, board_state_list: list[dict[tuple[int,int], Color]]) -> None:
        self.board_state_list = board_state_list

    def update_game_tree(self, board: GoBoard) -> None:
        self.board_state_list.append(deepcopy(board.full_stone_pos_to_color_hashmap))

    def _is_board_repeated(self, board: GoBoard) -> bool:
        "Check if a boad state is repeated"
        current_full_stone_to_co_color_map = board.full_stone_pos_to_color_hashmap
        if current_full_stone_to_co_color_map in self.board_state_list:
            return True
        else:
            return False



