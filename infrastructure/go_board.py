from .stone import *

from random import randint, seed
import numpy as np


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
    - `last_move_color` store the color of the last move. It will be used for generataion of the next move with the alternating rule
    - `block_list` stores the black/white block of stones for current state on board
    - `full_stone_to_color_map` stores the splashed information of stones' positions and colors as a dict

    Note: we set black first by default, initialize the board with `black_first=False` to switch this
    ```"""
    size: tuple[int, int] = (19,19)
    last_move_color: Color # alternating color for each move
    block_list: list[StoneBlock]
    full_stone_to_color_map: dict[tuple[int, int], Color] = {}
    block_nearest_neighbor_list: list[tuple[int, int]]
    block_liberty_list: list[int]

    
    def __init__(self, size: tuple[int, int], black_first: bool = True) -> None:
        self.size = size
        self.last_move_color = Color.White if black_first else Color.Black
        self.block_list: list[StoneBlock] = []
        self.full_stone_to_color_map: dict[tuple[int, int], Color] = {}
        self.block_nearest_neighbor_list: list[tuple[int, int]] = []
        self.block_liberty_list: list[int] = []
        
        
    def __repr__(self) -> str:
        board_str = f" Board Size: {self.size}\n "
        for i in range(self.size[0]-1,-1,-1):
            for j in range(0,self.size[1]):
                pos = (j,i)
                if pos in self.full_stone_to_color_map:
                    board_str += f"{self.full_stone_to_color_map[pos]}"
                else:
                    board_str += " +"
                if j == self.size[1]-1:
                    board_str += "\n "
        return board_str
    
        
        
    def update_full_stone_to_color_map(self) -> None:
        """```
        generate the full dict of stones `map<pos,color>` by splashing all block information
        ```"""
        self.full_stone_to_color_map: dict[tuple[int,int], Color] = {}
        for stone_block in self.block_list:
            for stone in stone_block.stone_list:
                self.full_stone_to_color_map[stone.pos] = stone_block.block_color
    
    

    
    
    def update_block_list(self, new_stone: Stone) -> None:
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



def get_distance(pos1: tuple[int,int], pos2: tuple[int,int]) -> np.floating:
    pos1_vec = np.array(pos1)
    pos2_vec = np.array(pos2)
    return np.linalg.norm(pos1_vec-pos2_vec)    







































    
    # def update_nearest_neighbor_list(self) -> None:
    #     # reinitlize the `nearest_neighbor_list`
    #     self.block_nearest_neighbor_list: list[StoneBlock] = []
    #     for (i, stone_block) in enumerate(self.block_list):
    #         current_nearest_neighbor: list[tuple[int, int]] = []
    #         for pos in stone_block.stone_list:
    #             nearest_nearby_sites_for_current_stone: list[tuple[int,int]] = []
    #             match self.get_board_position(pos):
    #                 case BoardPosition.Bulk:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
    #                 case BoardPosition.Left:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x+1,y), (x,y+1), (x,y-1)]
    #                 case BoardPosition.Right:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x-1,y), (x,y+1), (x,y-1)]
    #                 case BoardPosition.Bottom:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x+1,y), (x-1,y), (x,y+1)]
    #                 case BoardPosition.Top:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x+1,y), (x-1,y), (x,y-1)]
    #                 case BoardPosition.BottomLeftCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x+1,y), (x,y+1)]
    #                 case BoardPosition.BottomRightCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x-1,y), (x,y+1)]
    #                 case BoardPosition.TopLeftCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites_for_current_stone = [(x+1,y), (x,y-1)]
    #                 case BoardPosition.TopRightCorner:
    #                     (x,y) = pos
    #                     nearest_nearby_sites = [(x-1,y), (x,y-1)]
                
    #             # check if the site is occupied by other stones
    #             for test_site in nearest_nearby_sites_for_current_stone:
    #                 if test_site in self.full_stone_to_color_map:
    #                     nearest_nearby_sites_for_current_stone.remove(test_site)
                
    #         current_nearest_neighbor.extend(nearest_nearby_sites_for_current_stone)
    #         current_nearest_neighbor = list(set(current_nearest_neighbor))
            
    #         self.block_nearest_neighbor_list.extend(current_nearest_neighbor)


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
    #                 # if site in self.full_stone_to_color_map and self.last_move_color.alternate_color() == 
    #         self.block_liberty_list.append(current_liberty)

            
    # def get_board_position(self, pos: tuple[int, int]) -> BoardPosition:
    #     """for rectangular board only"""
    #     (N1, N2) = self.size
    #     (N1, N2) = (N1-1, N2-1)
    #     assert 0 <= pos[0] <= N1 and 0 <= pos[1] <= N2
    #     if pos == (0, 0):
    #         return BoardPosition.BottomLeftCorner
    #     elif pos == (N1, 0):
    #         return BoardPosition.BottomRightCorner
    #     elif pos == (0, N2):
    #         return BoardPosition.TopLeftCorner
    #     elif pos == (N1, N2): 
    #         return BoardPosition.TopRightCorner
    #     elif pos[0] == 0:
    #         return BoardPosition.Left
    #     elif pos[0] == N1:
    #         return BoardPosition.Right
    #     elif pos[1] == 0:
    #         return BoardPosition.Bottom
    #     elif pos[1] == N2:
    #         return BoardPosition.Top
    #     else:
    #         return BoardPosition.Bulk
        
    
    # def merge_single_stone_to_block(self, block_id: int, new_stone: StoneBlock) -> None:
    #     assert len(new_stone.stone_list) == 1
    #     self.block_list[i].append(new_stone)
        
        
    # def gen_move_at(self, pos: tuple[int,int])-> None:
    #     (N1, N2) = self.size
    #     assert 0 <= pos[0] <= N1-1 and 0 <= pos[1] <= N2-1
        
    #     # todo! add basic logic here to check if the move is legal or not
    #     current_move_color = self.last_move_color.alternate_color()
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