from .go_board import *


class GameTree:
    state_list: list[dict[tuple[int,int], Color]]

    def __init__(self, state_list: list[dict[tuple[int,int], Color]]) -> None:
        self.state_list = state_list

    def update_game_tree(self, board: GoBoard) -> None:
        self.state_list.append(deepcopy(board.full_stone_to_color_map))

    def _is_board_repeated(self, board: GoBoard) -> bool:
        "Check if a boad state is repeated"
        current_full_stone_to_co_color_map = board.full_stone_to_color_map
        if current_full_stone_to_co_color_map in self.state_list:
            return True
        else:
            return False



