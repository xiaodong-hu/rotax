from enum import Enum
from typing import Self


class Color(Enum):
    White = 1
    Black = -1

    # customize outputs of stone colors
    def __str__(self):
        from colorama import Fore, Style
        return { 
            Color.White: f"{Fore.LIGHTBLUE_EX} ⬤{Style.RESET_ALL}",
            Color.Black: f"{Fore.LIGHTRED_EX} ⬤{Style.RESET_ALL}",
        }[self] # a trick to return a local dict for dispath match

    def alternate(self) -> Self: # syntax sugar for optional type like rust
        """useful for generation of move under the alternating rule of colors"""
        match self:
            case Color.White: return Color.Black
            case Color.Black: return Color.White


class Stone:
    color: Color
    pos: tuple[int,int]
    
    
    def __init__(self, color: Color, pos: tuple[int, int]) -> None:
        self.color = color
        self.pos = pos
    
    
    def __repr__(self)->str:
        "show `pos` only for stone"
        # match self.color:
        #     case Color.White: return f"{self.pos}"
        #     case Color.Black: return f"{self.pos}"
        return f"{self.pos}"