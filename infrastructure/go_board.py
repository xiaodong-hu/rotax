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
        for stone in self.stone_list:
            block_str += f"{stone}"
        
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
    - `last_move_color` stores the color of the last move. It will be used for generataion of the next move with the alternating rule
    - `block_list` serves as the most fundamental structure describing the current state on board
    - `full_stone_to_color_map` stores the splashed information of stones' positions and colors as a dict
    - `block_nearest_neighbor_list` stores all nearest nearby empty sites for each block. This is helpful for counting the liberty and fight
    - `block_liberty_list` stores the liberties for each bloch. This is necessary to determine the legitimacy of each generation of move, as well as taking dead stones from the board

    Note: we set black first by default, initialize the board with `black_first=False` to switch this
    ```"""
    size: tuple[int, int]
    last_move_color: Color # alternating color for each move
    block_list: list[StoneBlock]
    full_stone_to_color_map: dict[tuple[int, int], Color]
    block_nearest_neighbor_list: list[list[tuple[int, int]]]
    block_liberty_list: list[int]

    
    def __init__(self, size: tuple[int, int] = (19,19), black_first: bool = True) -> None:
        self.size = size
        self.last_move_color = Color.White if black_first else Color.Black
        self.block_list: list[StoneBlock] = []
        self.full_stone_to_color_map: dict[tuple[int, int], Color] = {}
        self.block_nearest_neighbor_list: list[list[tuple[int, int]]] = []
        self.block_liberty_list: list[int] = []
        
        
    def __repr__(self) -> str:
        board_str = ""
        board_str += f"\033[1mBoard Size: {self.size}\033[0m"
        board_str += f"\tCurrent turn: \033[1m{self.last_move_color.alternate()}\033[0m"
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
        assert new_stone.pos not in self.full_stone_to_color_map # exclude illegal move

        matching_block_indices: list[int] = []
        
        # Find the indices of blocks that can be merged
        for (i, stone_block) in enumerate(self.block_list):
            if stone_block.block_color == new_stone.color:
                for stone in stone_block.stone_list:
                    if abs(get_distance(stone.pos, new_stone.pos) - 1.0) < 1.0E-8:
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
        assert 0 <= pos[0] <= N1 and 0 <= pos[1] <= N2
        if pos == (0, 0):
            return BoardPosition.BottomLeftCorner
        elif pos == (N1, 0):
            return BoardPosition.BottomRightCorner
        elif pos == (0, N2):
            return BoardPosition.TopLeftCorner
        elif pos == (N1, N2): 
            return BoardPosition.TopRightCorner
        elif pos[0] == 0:
            return BoardPosition.Left
        elif pos[0] == N1:
            return BoardPosition.Right
        elif pos[1] == 0:
            return BoardPosition.Bottom
        elif pos[1] == N2:
            return BoardPosition.Top
        else:
            return BoardPosition.Bulk


    def update_block_nearest_neighbor_list_and_liberty_list(self) -> None:
        """```
        ### Find All Nearest Nearby Empty Sites for Each Block.
        > The boundary condition is taken into account
        ```"""
        self.block_nearest_neighbor_list: list[list[tuple[int,int]]] = [] # reinitlize the list
        self.block_liberty_list: list[int] = [] # reinitialize the liberty list
        for (i, stone_block) in enumerate(self.block_list):
            nearest_nearby_sites_for_current_block: list[tuple[int, int]] = []
            for stone in stone_block.stone_list:
                nearest_nearby_sites_for_current_stone: list[tuple[int,int]] = []
                match self.get_board_position(stone.pos):
                    case BoardPosition.Bulk:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
                    case BoardPosition.Left:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x+1,y), (x,y+1), (x,y-1)]
                    case BoardPosition.Right:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x-1,y), (x,y+1), (x,y-1)]
                    case BoardPosition.Bottom:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x+1,y), (x-1,y), (x,y+1)]
                    case BoardPosition.Top:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x+1,y), (x-1,y), (x,y-1)]
                    case BoardPosition.BottomLeftCorner:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x+1,y), (x,y+1)]
                    case BoardPosition.BottomRightCorner:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x-1,y), (x,y+1)]
                    case BoardPosition.TopLeftCorner:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x+1,y), (x,y-1)]
                    case BoardPosition.TopRightCorner:
                        (x,y) = stone.pos
                        nearest_nearby_sites_for_current_stone = [(x-1,y), (x,y-1)]
                
                nearest_nearby_sites_for_current_block.extend(nearest_nearby_sites_for_current_stone)

            # Remove the potential repeated nearest nearby sites
            nearest_nearby_sites_for_current_block = list(set(nearest_nearby_sites_for_current_block))

            # Check if the site within `nearest_nearby_sites_for_current_stone` is already occupied by other stones
            for pos in self.full_stone_to_color_map.keys():
                if pos in nearest_nearby_sites_for_current_block:
                    nearest_nearby_sites_for_current_block.remove(pos)
    
            self.block_nearest_neighbor_list.append(nearest_nearby_sites_for_current_block)
            self.block_liberty_list.append(len(nearest_nearby_sites_for_current_block))


    def pass_move(self) -> None:
        "to switch color"
        self.last_move_color = self.last_move_color.alternate()


    def place_stone_at(self, pos: tuple[int,int], show_board: bool=True) -> bool:
        if pos in self.full_stone_to_color_map:
            return False # already occupied

        stone_color = self.last_move_color.alternate()
        self.last_move_color = stone_color
        stone = Stone(stone_color, pos)
        
        # Check if any blocks have 0 liberties after the trial move
        test_board = deepcopy(self)
        test_board.update_block_list(stone)
        test_board.update_full_stone_to_color_map()
        test_board.update_block_nearest_neighbor_list_and_liberty_list()
        zero_liberty_blocks: list[StoneBlock] = []
        zero_liberty_blocks_of_current_color: list[StoneBlock] = []
        for (block_ind, liberty) in enumerate(test_board.block_liberty_list):
            if liberty == 0:
                current_block = test_board.block_list[block_ind]
                if current_block.block_color != self.last_move_color:
                    zero_liberty_blocks.append(current_block)
                else: # current_block.block_color == self.last_move_color:
                    zero_liberty_blocks.append(current_block)
                    zero_liberty_blocks_of_current_color.append(current_block)


        _is_move_legal = False
        _is_simple_capture = False
        _is_suicide_capture = False
        assert set(zero_liberty_blocks_of_current_color).issubset(set(zero_liberty_blocks))
        if len(zero_liberty_blocks) == len(zero_liberty_blocks_of_current_color) == 0: 
            # normal move
            _is_move_legal = True
            _is_simple_capture = False
            _is_suicide_capture = False
        elif len(zero_liberty_blocks) != 0 and len(zero_liberty_blocks_of_current_color) == 0: 
            # simple capture
            _is_move_legal = True
            _is_simple_capture = True
            _is_suicide_capture = False
        else: # len(zero_liberty_blocks) != 0 and len(zero_liberty_blocks_of_current_color) != 0:
            if len(zero_liberty_blocks) == len(zero_liberty_blocks_of_current_color):
                # pure suicide, namely is a forbidden point
                _is_move_legal = False
                _is_simple_capture = False
                _is_suicide_capture = False
            else: # len(zero_liberty_blocks) > len(zero_liberty_blocks_of_current_color):
                # suicide capture
                _is_move_legal = True
                _is_simple_capture = False
                _is_suicide_capture = True

        match (_is_move_legal, _is_simple_capture, _is_suicide_capture):
            case (True, False, False):
                pass
            case (True, True, False):
                for block in zero_liberty_blocks:
                    test_board.block_list.remove(block)
                    test_board.update_full_stone_to_color_map()
                    test_board.update_block_nearest_neighbor_list_and_liberty_list()
            case (True, False, True):
                blocks_to_remove = list(set(zero_liberty_blocks).difference(set(zero_liberty_blocks_of_current_color)))
                for block in blocks_to_remove:
                    test_board.block_list.remove(block)
                    test_board.update_full_stone_to_color_map()
                    test_board.update_block_nearest_neighbor_list_and_liberty_list()
            case _:
                self.last_move_color = self.last_move_color.alternate()
                return False

        # if move is legal
        self.block_list = test_board.block_list
        self.full_stone_to_color_map = test_board.full_stone_to_color_map
        self.block_nearest_neighbor_list = test_board.block_nearest_neighbor_list
        self.block_liberty_list = test_board.block_liberty_list
        if show_board:
            print(self) 

        return True

    def place_stone_with_color_at(self, pos: tuple[int,int], color: Color) -> bool:
        "ignore the alternating-color rule and place stone with specific color on board"
        self.last_move_color = color.alternate() # change last move color to ensure the current move to have a correct color
        _is_move_legal = self.place_stone_at(pos)
        return _is_move_legal






def get_distance(pos1: tuple[int,int], pos2: tuple[int,int]) -> np.floating:
    pos1_vec = np.array(pos1)
    pos2_vec = np.array(pos2)
    return np.linalg.norm(pos1_vec-pos2_vec)    



            

    

























    


    # def update_liberty_list(self) -> None:
    #     # reinitlize the `liberty_list`
    #     self.block_liberty_list: list[int] = []
    #     for (i, stone_block) in enumerate(self.block_list):
    #         current_liberty = 0
    #         for pos in stone_block.stone_list:
    #             nearest_nearby_sites: list[tuple[int,int]] = []
    #             match self.get_position(pos):
    #                 case BoardPosition.Bulk:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]  
    #                 case BoardPosition.Left:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x+1,y), (x,y+1), (x,y-1)]
    #                 case BoardPosition.Right:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x-1,y), (x,y+1), (x,y-1)]
    #                 case BoardPosition.Bottom:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x+1,y), (x-1,y), (x,y+1)]
    #                 case BoardPosition.Top:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x+1,y), (x-1,y), (x,y-1)]
    #                 case BoardPosition.BottomLeftCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x+1,y), (x,y+1)]
    #                 case BoardPosition.BottomRightCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x-1,y), (x,y+1)]
    #                 case BoardPosition.TopLeftCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x+1,y), (x,y-1)]
    #                 case BoardPosition.TopRightCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x-1,y), (x,y-1)]
                              
    #             for site in nearest_nearby_sites:
    #                 if site not in self.full_stone_to_color_map: # if unoccupied
    #                     current_liberty += 1
    #                 # if site in self.full_stone_to_color_map and self.last_move_color.alternate() == 
    #         self.block_liberty_list.append(current_liberty)

 
    
    # def merge_single_stone_to_block(self, block_id: int, new_stone: StoneBlock) -> None:
    #     assert len(new_stone.stone_list) == 1
    #     self.block_list[i].append(new_stone)
        
        
    # def gen_move_at(self, pos: tuple[int,int])-> None:
    #     (N1, N2) = self.size
    #     assert 0 <= pos[0] <= N1-1 and 0 <= pos[1] <= N2-1
        
    #     # todo! add basic logic here to check if the move is legal or not
    #     current_move_color = self.last_move_color.alternate()
    #     if len(self.block_list) == 0:
    #         new_singlet_block = StoneBlock(current_move_color, [pos])
    #         self.block_list.append(new_singlet_block)
    #     else:
    #         for (i, nearest_nearby_sites) in enumerate(self.block_nearest_neighbor_list):
    #             if pos in nearest_nearby_sites and current_move_color == self.block_list[i].block_color:
    #                 self.block_list[i].stone_list.append(pos)
    #             else:
    #                 new_singlet_block = StoneBlock(current_move_color, [pos])
    #                 self.block_list.append(new_singlet_block)
                
    #     # update all information with the new `block_nearest_neighbor_list`
    #     self.update_full_stone_to_color_map()
    #     self.update_nearest_neighbor_list()
    #     self.update_liberty_list()
        
    #     print(self.block_list)
    #     print(self.full_stone_to_color_map)
    #     print(self.block_nearest_neighbor_list)
    #     print(self.block_liberty_list)
    #     print(self)
    #     print(f"gen move at {pos}\n")

        
# class BoardAnalysis:
#     block_list: list[list[list[int]]]
#     block_liberty_list: list[int]