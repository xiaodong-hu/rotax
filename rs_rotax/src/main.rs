mod gen_move;
mod go_board;
mod go_stone;

use gen_move::*;
use go_board::*;
use go_stone::*;

use std::collections::HashMap;

fn main() {
    // let a = Stone::new(Color::Black, [2, 3]);
    // let b = Stone::new(Color::Black, [2, 4]);
    // println!("{}{}", a, b);

    // let mut A = GoBoard::new();
    // A.update_block_list(&a);
    // A.update_block_list(&b);
    // A.update_stone_pos_to_color_hashmap();
    // print!("{}\n{:?}\n\n", A, A.block_info.block_list);

    // dbg!(A.get_position_on_board(&[0, 0]));
    // dbg!(A.get_position_on_board(&[1, 2]));
    // dbg!(A.get_position_on_board(&[5, 0]));

    let mut A = GoBoard::new([19, 19]);
    gen_game(&mut A);
    // let mut allowed_searching_site_hashmap = HashMap::<[i32; 2], bool>::new();
    // for i in 0..A.meta_data.size[0] {
    //     for j in 0..A.meta_data.size[1] {
    //         allowed_searching_site_hashmap.insert([i, j], true);
    //     }
    // }

    // A.try_place_stone_at(&[2, 3]);
    // A.try_place_stone_at(&[2, 4]);
    // A.try_place_stone_at(&[3, 4]);
    // A.try_place_stone_at(&[2, 15]);
    // A.try_place_stone_at(&[2, 5]);

    // allowed_searching_site_hashmap =
    //     A.update_allowed_searching_site_hashmap(allowed_searching_site_hashmap);
    // let allowed_site_list_for_current_move = allowed_searching_site_hashmap
    //     .iter()
    //     .filter(|(_, &value)| value)
    //     .map(|(&key, _)| key)
    //     .collect::<Vec<_>>();
    // dbg!(allowed_site_list_for_current_move.len());

    // A.try_place_stone_at(&[16, 3]);
    // A.try_place_stone_at(&[1, 4]);
    // A.try_place_stone_at(&[2, 4]); // suicide
    println!("{}", A);
    // println!(
    //     "block list: {:?}\nblock liberty list: {:?}\nblock eye list: {:?}",
    //     A.block_info.block_list, A.block_info.block_liberty_list, A.block_info.block_eye_list
    // );
}
