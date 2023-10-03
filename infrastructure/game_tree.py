
from .go_board_fast import *


class GameTree:
    current_go_board: GoBoard
    game_tree: list[dict[tuple[int,int], Color]]
    full_searching_site_hashset: set[tuple[int,int]]

    def __init__(self, current_go_board: GoBoard) -> None:
        self.current_go_board = current_go_board
        self.game_tree = [current_go_board.full_stone_pos_to_color_hashmap]
        self.full_searching_site_hashset = set([(i,j) for i in range(0, current_go_board.size[0]) for j in range(0, current_go_board.size[1])])

    def update_game_tree(self, board_state_hashmap: dict[tuple[int,int], Color]) -> None:
        self.game_tree.append(board_state_hashmap)

    def _is_board_repeated(self, board_state_hashmap: dict[tuple[int,int], Color]) -> bool:
        "Check if a boad state is repeated"
        current_board_state = str(board_state_hashmap)
        if current_board_state in self.game_tree:
            return True
        else:
            return False


    def generate_allowed_searching_site_hashset(self, go_board: GoBoard) -> set[tuple[int,int]]:
        allowed_searching_site_hashset = self.full_searching_site_hashset.difference(go_board.full_stone_pos_to_color_hashmap.keys())
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
                (_is_single_eye, single_eye_color) = go_board._is_single_eye(site)
                if not _is_single_eye:
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
                if _is_single_eye:
                    # if is opponent's single eye
                    if single_eye_color == go_board.current_move_color.alternate():
                        nearby_block_id_list = go_board.full_site_to_nearby_block_id_list_hashmap[site]
                        block_counter_of_opponent_color_with_one_liberty = 0
                        block_counter_of_opponent_color_with_one_liberty_and_one_stone = 0
                        stone_pos_of_opponent_color_with_one_liberty_and_one_stone: tuple[int,int] = (0,0)
                        _is_pure_suicide = True
                        for block_id in nearby_block_id_list:
                            if len(go_board.block_id_to_block_liberty_site_hashset_hashmap[block_id]) == 1:
                                _is_pure_suicide = False # capture occurs for current move to place here
                                block_counter_of_opponent_color_with_one_liberty += 1
                                if len(go_board.block_id_to_stone_block_hashmap[block_id].stone_pos_hashset) == 1:
                                    block_counter_of_opponent_color_with_one_liberty_and_one_stone += 1

                                    stone_pos_of_opponent_color_with_one_liberty_and_one_stone = go_board.block_id_to_stone_block_hashmap[block_id].stone_pos_hashset.pop()

                        if _is_pure_suicide:
                            # illegal for current player to place a move
                            if site in allowed_searching_site_hashset:
                                allowed_searching_site_hashset.remove(site)
                        if not _is_pure_suicide:
                            # even if the site is not suicide, it can still be a ko here!
                            if block_counter_of_opponent_color_with_one_liberty == block_counter_of_opponent_color_with_one_liberty_and_one_stone == 1:
                                # avoid deepcopy for `ko_board_state_hashmap`, just modify it locally
                                
                                # add a trial stone and remove the opponent's single stone
                                go_board.full_stone_pos_to_color_hashmap[site] = go_board.current_move_color
                                del go_board.full_stone_pos_to_color_hashmap[stone_pos_of_opponent_color_with_one_liberty_and_one_stone]
                                # strictly refuse the move that repeat the board !
                                if self._is_board_repeated(go_board.full_stone_pos_to_color_hashmap):
                                    # recover the original `ko_board_state_hashmap`
                                    del go_board.full_stone_pos_to_color_hashmap[site]
                                    go_board.full_stone_pos_to_color_hashmap[stone_pos_of_opponent_color_with_one_liberty_and_one_stone] = go_board.current_move_color.alternate()
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
