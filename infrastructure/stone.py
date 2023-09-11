from enum import Enum
from dataclasses import dataclass

class Color(Enum):
    White = 1
    Black = -1
    Empty = 0

    # customize outputs of stone colors
    def __str__(self):
        from colorama import Fore, Style
        return { 
            Color.White: f"{Fore.GREEN} ●{Style.RESET_ALL}",
            Color.Black: f"{Fore.BLUE} ●{Style.RESET_ALL}",
            Color.Empty: " +",
        }[self] # a trick to return a local dict for dispath match


@dataclass
class Stone:
    color: Color
    pos: tuple[int,int]
    
    # inherit outputs of colors to stones
    def __repr__(self)->str:
        return {
            Color.White: f"{Color.White}",
            Color.Black: f"{Color.Black}",
            Color.Empty: f"{Color.Empty}",
        }[self.color]