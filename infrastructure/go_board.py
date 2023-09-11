from .stone import *

# from dataclasses import dataclass


class GoBoard:
    size: tuple[int, int] = (19,19)
    current_state: dict[tuple[int,int], Color]
    
    def __init__(self, size: tuple[int, int]) -> None:
        """initlize the empty board"""
        GoBoard.size = size
        GoBoard.current_state: dict[tuple[int,int], Color] = {}
        for i in range(0,size[0]):
            for j in range(0,size[1]):
                GoBoard.current_state[(i,j)] = Color.Empty
        
    def __repr__(self) -> str:
        board_str = f" Board Size: {self.size}\n "
        for i in range(self.size[0]-1,-1,-1):
            for j in range(0,self.size[1]):
                board_str += f"{self.current_state[(j,i)]}" # print in the human-readable order
                if j == self.size[1]-1:
                    board_str += "\n "
        return board_str
    
    def gen_move(self, color: Color, pos: tuple[int,int])-> None:
        # todo! add basic logic here to check if the move is legal or not
        self.current_state[pos] = color
        print(self)
        print(f"gen move at {pos}\n")

        
class BoardAnalysis:
    block_list: list[list[list[int]]]
    block_liberty_list: list[int]