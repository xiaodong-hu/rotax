mod go_board;
mod go_stone;

use go_board::*;
use go_stone::*;

fn main() {
    let a = Stone::new(Color::Black, [2, 3]);
    let b = Stone::new(Color::White, [4, 5]);
    // println!("{}{}", a, b);

    let mut A = GoBoard::new();
    A.update_block_list(&a);
    A.update_block_list(&b);
    A.update_pos_to_color_map();
    print!("{}", A);
}
