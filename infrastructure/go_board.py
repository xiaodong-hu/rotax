from typing import Union
from .stone import *
import numpy as np
from copy import copy, deepcopy

class StoneBlock:
    """ ```
    ### Block of Stones
    > `block_color` is useful for stone-block or block-block merge
    > `stone_list` stores all positions of the stones of *the same* color
    ```"""
    block_color: Color
    stone_list: list[Stone]
    
    def __init__(self, block_color: Color, stone_list: list[Stone]) -> None:
        """initlize the empty block of stones"""
        self.block_color = block_color
        self.stone_list = stone_list
        
    def __repr__(self) -> str:
        block_str = f"{self.block_color} "
        block_str += f"{self.stone_list[0]}..."        
        return block_str


class BoardPosition(Enum):
    Bulk = 0
    Left = 1
    Right = 2
    Bottom = 3
    Top = 4
    BottomLeftCorner = 5
    BottomRightCorner = 6
    TopLeftCorner = 7
    TopRightCorner = 8
    

class GoBoard:
    """```
    ### Go Board Class
    - `size` tells the board shape
    - `current_move_color` stores the color of stone to be place. It will be used for generataion of the next move with the alternating rule
    - `block_list` serves as the most fundamental structure describing the current state on board
    - `full_stone_to_color_map` stores the splashed information of stones' positions and colors as a dict
    - `block_liberty_list` stores the liberties for each bloch. This is necessary to determine the legitimacy of each generation of move, as well as taking dead stones from the board
    - 

    Note: we set black first by default, initialize the board with `black_first=False` to switch this
    ```"""
    size: tuple[int, int]
    komi: float
    consecutive_passes: int
    current_move_color: Color # alternating color for each move
    block_list: list[StoneBlock]
    full_stone_to_color_map: dict[tuple[int, int], Color]
    # block_nearest_neighbor_list: list[list[tuple[int, int]]]
    site_to_nearest_nearby_block_index_map: dict[tuple[int, int], int]
    block_liberty_list: list[int]
    block_eye_list: list[int]

    
    def __init__(self, size: tuple[int, int] = (19,19), black_first: bool = True) -> None:
        self.size = size
        self.komi = 7.5
        self.consecutive_passes = 0
        self.current_move_color = Color.Black if black_first else Color.White
        self.block_list: list[StoneBlock] = []
        self.full_stone_to_color_map: dict[tuple[int, int], Color] = {}
        # self.block_nearest_neighbor_list: list[list[tuple[int, int]]] = []
        self.site_to_nearest_nearby_block_index_map: dict[tuple[int, int], int] = {}
        self.block_liberty_list: list[int] = []
        self.block_eye_list: list[int] = []
        

    def __repr__(self) -> str:
        board_str = f"current board: (board size: {self.size})\n"
        for i in range(self.size[0],-1,-1):
            for j in range(0,self.size[1]+1):
                pos = (j,i)
                if pos in self.full_stone_to_color_map:
                    board_str += f" {self.full_stone_to_color_map[pos]}"
                elif j <= self.size[1]-1 and i < self.size[0] and i != -1:
                    board_str += "  +"

                if j == self.size[1]-1:
                    board_str += "\n "
                if j == self.size[1] and i-1 >= 0:
                    board_str += f"{i-1:2d}"

        board_str += "   "
        for x in range(0,self.size[1]):
            board_str += f"{x:2d} "
        board_str += "\n"

        return board_str
    

    def update_block_list(self, new_stone: Stone) -> None:
        """```
        ### Update the StoneBlock Information with Consideration of Stone-Block and Block-Block Merges
        ```"""
        matching_block_indices: list[int] = []
        
        # Find the indices of blocks that can be merged
        for (i, stone_block) in enumerate(self.block_list):
            if stone_block.block_color == new_stone.color:
                for stone in stone_block.stone_list:
                    if abs(get_distance_of_two_sites(stone.pos, new_stone.pos) - 1.0) < 1.0E-8:
                        matching_block_indices.append(i)
                        break  # We only need to check once for each block

        # If no matching block is found, create a new single-stone block
        if len(matching_block_indices) == 0:
            new_single_stone_block = StoneBlock(new_stone.color, [new_stone])
            self.block_list.append(new_single_stone_block)
            return None

        # If a single matching block found, add the stone to that block
        if len(matching_block_indices) == 1:
            self.block_list[matching_block_indices[0]].stone_list.append(new_stone)
            return None

        # If multiple matching blocks found, merge them into one block
        if len(matching_block_indices) > 1:
            new_merged_block = StoneBlock(new_stone.color, [new_stone]) # huge merged block grown from the `new_stone`
            for block_ind in reversed(matching_block_indices):  # Reverse the order to avoid index issues when removing
                block_to_merge = self.block_list.pop(block_ind)
                new_merged_block.stone_list.extend(block_to_merge.stone_list)

            self.block_list.append(new_merged_block)
            return None


    def update_full_stone_to_color_map(self) -> None:
        """```
        generate the full dict of stones `map<pos,color>` by splashing all block information
        ```"""
        self.full_stone_to_color_map: dict[tuple[int,int], Color] = {} # reinitialize the dict
        for stone_block in self.block_list:
            for stone in stone_block.stone_list:
                self.full_stone_to_color_map[stone.pos] = stone_block.block_color
    
    
    def get_board_position(self, pos: tuple[int, int]) -> BoardPosition:
        """for rectangular board only"""
        (N1, N2) = self.size
        (N1, N2) = (N1-1, N2-1)
        # (i, j) = pos
        assert 0 <= pos[0] <= N1 and 0 <= pos[1] <= N2
        match pos:
            case (0, 0): return BoardPosition.BottomLeftCorner
            case (i, 0) if i == N1: return BoardPosition.BottomRightCorner
            case (0, j) if j == N2: return BoardPosition.TopLeftCorner
            case (i, j) if i == N1 and j == N2: return BoardPosition.TopRightCorner
            case (0, j) if j > 0: return BoardPosition.Left
            case (i, j) if i == N1 and j > 0: return BoardPosition.Right
            case (i, 0) if i > 0: return BoardPosition.Bottom
            case (i, j) if i > 0 and j == N2: return BoardPosition.Top
            case _: return BoardPosition.Bulk


    def get_nearest_nearby_sites_for_position(self, pos: tuple[int, int]) -> list[tuple[int,int]]:
        (x,y) = pos
        match self.get_board_position(pos):
            case BoardPosition.Bulk: return [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
            case BoardPosition.Left: return [(x+1,y), (x,y+1), (x,y-1)]
            case BoardPosition.Right: return [(x-1,y), (x,y+1), (x,y-1)]
            case BoardPosition.Bottom: return [(x+1,y), (x-1,y), (x,y+1)]
            case BoardPosition.Top: return [(x+1,y), (x-1,y), (x,y-1)]
            case BoardPosition.BottomLeftCorner: return [(x+1,y), (x,y+1)]
            case BoardPosition.BottomRightCorner: return [(x-1,y), (x,y+1)]
            case BoardPosition.TopLeftCorner: return [(x+1,y), (x,y-1)]
            case BoardPosition.TopRightCorner: return [(x-1,y), (x,y-1)]



    def find_nearby_block_index_list_of_specific_color(self, site: tuple[int, int], color: Color) -> list[int]:
        "find nearest blocks for arbitrary position on board (it can be already occupied)"
        nearest_nearby_block_ind_list: list[int] = []
        for (block_ind, stone_block) in enumerate(self.block_list):
            if stone_block.block_color == color:
                for stone in stone_block.stone_list:
                    if abs(np.linalg.norm(np.array(site,dtype=np.int32) - np.array(stone.pos,dtype=np.int32))-1.0) < 1.0E-8:
                        nearest_nearby_block_ind_list.append(block_ind)
                        break

        return nearest_nearby_block_ind_list


    # def update_site_to_nearest_nearby_block_index_map(self) -> None:
    #     self.
    #     full_site_list = [(i,j) for i in range(0, self.size[0]) for j in range(0, self.size[1])]
    #     empty_site_set = set(full_site_list).difference(set(self.full_stone_to_color_map.keys()))
    #     for site in empty_site_set:
    #         nearest_nearby_sites = self.get_nearest_nearby_sites_for_position(site)



    def _is_eye(self, pos: tuple[int,int]) -> bool:
        "here eye can be fake: a site is defined as eye if the left/right/up/down are of the same color"
        nearest_neighbor_sites = self.get_nearest_nearby_sites_for_position(pos)
        nearest_neighbor_sites_color_list: list[Color] = []
        for pos in nearest_neighbor_sites:
            res_color = self.full_stone_to_color_map.get(pos)
            if res_color is None:
                return False
            else: 
                nearest_neighbor_sites_color_list.append(res_color)

        if len(set(nearest_neighbor_sites_color_list)) == 1:
            # if all nearest nearby sites are of the same color
            return True
        else:
            return False


    def update_nearest_neighbor_list_and_liberty_list_and_eye_list(self) -> None:
        """```
        ### Use auxiliary `nearest_neighbor_sites_for_current_block` to count block liberties
        > The boundary condition is taken into account
        ```"""
        # self.block_nearest_neighbor_list: list[list[tuple[int,int]]] = [] # reinitlize the auxiliary list
        self.block_liberty_list: list[int] = [] # reinitialize the liberty list
        self.block_eye_list: list[int] = []
        for stone_block in self.block_list:
            nearest_neighbor_sites_for_current_block: list[tuple[int, int]] = []
            for stone in stone_block.stone_list:
                nearest_neighbor_sites = self.get_nearest_nearby_sites_for_position(stone.pos) 
                nearest_neighbor_sites_for_current_block.extend(nearest_neighbor_sites)

            # Remove the repeated counting sites
            nearest_neighbor_sites_for_current_block = list(set(nearest_neighbor_sites_for_current_block))

            # Check if the site within `nearest_neighbor_sites_for_current_stone` is already occupied by other stones
            for pos in self.full_stone_to_color_map:
                if pos in nearest_neighbor_sites_for_current_block:
                    nearest_neighbor_sites_for_current_block.remove(pos)
    
            # self.block_nearest_neighbor_list.append(nearest_neighbor_sites_for_current_block)
            self.block_liberty_list.append(len(nearest_neighbor_sites_for_current_block))

            eye_counter_for_current_block = 0
            for site in nearest_neighbor_sites_for_current_block:
                if self._is_eye(site):
                    eye_counter_for_current_block += 1

            self.block_eye_list.append(eye_counter_for_current_block)


    def pass_move(self) -> None:
        "switch color"
        print(f"MOVE{self.current_move_color} PASSED!!!")
        self.current_move_color = self.current_move_color.alternate()
        print(self)
        


    def _is_capture_move(self, test_board: Self) -> bool:
        "input an updated board to check if capture occurs for the test move by checking the liberty condition, without mutating the test_board-board"
        test_move_color = self.current_move_color
        for(block_ind, stone_block) in enumerate(test_board.block_list):
            block_liberty = test_board.block_liberty_list[block_ind]
            if stone_block.block_color != test_move_color and block_liberty == 0:
                return True
        return False


    def _is_suicide_move(self, test_board: Self) -> bool:
        "input an updated board to check if suicide occurs for the test move by checking the liberty condition, without mutating the test_board-board"
        test_move_color = self.current_move_color
        for(block_ind, stone_block) in enumerate(test_board.block_list):
            block_liberty = test_board.block_liberty_list[block_ind]
            if stone_block.block_color == test_move_color and block_liberty == 0:
                return True
        return False


    def try_place_stone_at(self, pos: tuple[int,int], show_board: bool=True) -> bool:
        test_board = deepcopy(self)
        test_move_color = self.current_move_color # double alternating = unchanged
        test_board.current_move_color = test_move_color.alternate()
        test_board.update_block_list(Stone(test_move_color, pos))
        test_board.update_full_stone_to_color_map()
        test_board.update_nearest_neighbor_list_and_liberty_list_and_eye_list()

        _is_capture = self._is_capture_move(test_board)
        _is_suicide = self._is_suicide_move(test_board)
        _is_normal_move = True if (not _is_capture) and (not _is_suicide) else False
        match (_is_normal_move, _is_capture, _is_suicide):
            case (True, False, False): # normal move: legal
                pass
            case (False, True, _): # simply capture or capture with suicide: legal
                block_ind_list_to_be_captured: list[int] = []
                for (block_ind, stone_block) in enumerate(test_board.block_list):
                    block_liberty = test_board.block_liberty_list[block_ind]
                    if block_liberty == 0 and stone_block.block_color != test_move_color:
                        block_ind_list_to_be_captured.append(block_ind)
                for block_ind in reversed(block_ind_list_to_be_captured):
                    test_board.block_list.pop(block_ind)

                # update `test_board`
                test_board.update_full_stone_to_color_map()
                test_board.update_nearest_neighbor_list_and_liberty_list_and_eye_list()
            case (False, False, True): # pure suidice: illegal!
                return False
            case _: pass
        
        # if move is legal, update self-board with `test_board`
        self.current_move_color = test_board.current_move_color
        self.block_list = test_board.block_list
        self.full_stone_to_color_map = test_board.full_stone_to_color_map
        # self.block_nearest_neighbor_list = test_board.block_nearest_neighbor_list
        self.block_liberty_list = test_board.block_liberty_list
        self.block_eye_list = test_board.block_eye_list
        # self = deepcopy(test_board)

        if show_board:
            print(f"\033[1mgen move at:\033[0m{test_move_color} {pos}\n\033[1mnext turn:\033[0m{test_move_color.alternate()}\n")
            print(self)            

        return True


    def try_place_stone_with_color_at(self, pos: tuple[int,int], color: Color, show_board: bool=True) -> bool:
        "ignore the alternating-color rule and place stone with specific color on board"
        self.current_move_color = color # change `current_move_color`
        _is_move_legal = self.try_place_stone_at(pos, show_board=show_board)
        return _is_move_legal





    def _is_illegal_move_for_opponent(self, pos: tuple[int,int]) -> bool:
        """```
        ### Auxiliary Function to Determine Whether the Empty Site is Illegal for the Opponent
        > If is true, then self-occupy of that site should be cautious --- it can be occupation of the crucial true eye of the block
        ```"""
        assert pos not in self.full_stone_to_color_map

        # Swich the color for a test move to see if the empty site `pos` is an illegal point
        opponent_color = copy(self.current_move_color.alternate())
        test_board = deepcopy(self)
        if test_board.try_place_stone_with_color_at(pos, opponent_color, show_board=False):
            # if the trial move is allowed for the opponent
            return False
        else: 
            return True


    def update_ignored_site_list(self, ignored_site_list: set[tuple[int,int]], pos: tuple[int,int]) -> None:
        test_board = deepcopy(self)
        if pos in ignored_site_list:
            return None

        if not test_board.try_place_stone_at(pos, show_board=False):
            # if is illegal for current player, ignore the site
            if pos not in ignored_site_list:
                ignored_site_list.add(pos)
        else:
            # if is OK for current player        
            test_board = deepcopy(self)
            _is_site_illegal_for_opponent = test_board._is_illegal_move_for_opponent(pos)
            if _is_site_illegal_for_opponent:
                current_move_color = self.current_move_color
                
                # before the test move
                nearby_block_ind_list = self.find_nearby_block_index_list_of_specific_color(pos, current_move_color)
                # block_liberty_list = [self.block_liberty_list[block_ind] for block_ind in nearby_block_ind_list]
                block_eye_list = [self.block_eye_list[block_ind] for block_ind in nearby_block_ind_list]

                # below for test only
                # print(f"{current_move_color} found site {pos} illegal for{current_move_color.alternate()}")
                # block_list = [self.block_list[block_ind] for block_ind in nearby_block_ind_list]
                # for test only
                # print(f"\t{pos} nearby block list before trial move: {block_list}")
                # print(f"\t{pos} nearby block liberty list before trial move: {block_liberty_list}")
                # print(f"\t{pos} nearby block # of eyes before trial move: {block_eye_list}")

                suicide_indicator_list = [block_eye_list[i] == 2 for (i,_) in enumerate(nearby_block_ind_list)]
                if any(suicide_indicator_list):
                    # for (i, _) in enumerate(nearby_block_ind_list):
                    # test move
                    test_board.try_place_stone_at(pos, show_board=False)
                    
                    merged_block_ind = test_board.find_nearby_block_index_list_of_specific_color(pos, current_move_color)[0]
                    merged_block_liberty = test_board.block_liberty_list[merged_block_ind]
                    merged_block_eye = test_board.block_eye_list[merged_block_ind]
                    
                    if merged_block_liberty < 2 or merged_block_eye < 2:
                        # ignore suicide 
                        print(f"{current_move_color} found site {pos} is suicide so ignore it! (liberty and eye after merge: ({merged_block_liberty}, {merged_block_eye}))")
                        
                        if pos not in ignored_site_list:
                            ignored_site_list.add(pos)
                    
    # def update_ignored_site_list(self, ignored_site_list: set[tuple[int, int]], pos: tuple[int, int]) -> None:
    #     if pos in ignored_site_list:
    #         return

    #     test_board = deepcopy(self)
    #     if not test_board.try_place_stone_at(pos, show_board=False):
    #         ignored_site_list.add(pos)
    #     else:
    #         current_move_color = test_board.current_move_color

    #         nearby_block_ind_list = test_board.find_nearby_block_index_list_of_specific_color(pos, current_move_color)
    #         block_eye_list = [test_board.block_eye_list[block_ind] for block_ind in nearby_block_ind_list]
    #         suicide_indicator_list = [block_eye == 2 for block_eye in block_eye_list]

    #         if any(suicide_indicator_list):
    #             test_board.try_place_stone_at(pos, show_board=False)
    #             merged_block_ind = test_board.find_nearby_block_index_list_of_specific_color(pos, current_move_color)[0]
    #             merged_block_liberty = test_board.block_liberty_list[merged_block_ind]
    #             merged_block_eye = test_board.block_eye_list[merged_block_ind]

    #             if merged_block_liberty < 2 or merged_block_eye < 2:
    #                 ignored_site_list.add(pos)
    #                 print(f"{current_move_color} found site {pos} is suicide, so it is ignored! (liberty and eye after merge: ({merged_block_liberty}, {merged_block_eye}))")


    def generate_allowed_site_list(self, full_site_list: list[tuple[int,int]]) -> list[tuple[int,int]]:
        empty_site_set = set(full_site_list).difference(set(self.full_stone_to_color_map.keys()))

        ignored_site_list: set[tuple[int,int]] = set([])
        allowed_search_site_list = list(empty_site_set.difference(set(ignored_site_list)))
        for site in allowed_search_site_list:
            self.update_ignored_site_list(ignored_site_list, site)
            allowed_search_site_list = list(empty_site_set.difference(set(ignored_site_list)))
        return allowed_search_site_list


    def score_board(self) -> tuple[tuple[Color,int], tuple[Color,int]]:
        # count Black
        black_score = 0
        white_score = 0
        for stone_block in self.block_list:
            match stone_block.block_color:
                case Color.Black: black_score += len(stone_block.stone_list)
                case Color.White: white_score += len(stone_block.stone_list)
        
        return ((Color.Black, black_score), (Color.White, white_score))



def get_distance_of_two_sites(pos1: tuple[int,int], pos2: tuple[int,int]) -> np.floating:
    pos1_vec = np.array(pos1)
    pos2_vec = np.array(pos2)
    return np.linalg.norm(pos1_vec-pos2_vec)


def get_minimal_distance_of_site_and_block(pos: tuple[int, int], stone_block:StoneBlock) -> np.floating:
    pos_vec = np.array(pos)
    stone_vec_list = [np.array(stone.pos) for stone in stone_block.stone_list]
    distance_list = [np.linalg.norm(pos_vec-site_vec) for site_vec in stone_vec_list]
    return np.min(distance_list)
            

