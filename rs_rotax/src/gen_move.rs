use std::collections::HashMap;

use crate::go_board::*;
use rand::seq::SliceRandom;

pub fn gen_move(board: &mut GoBoard) -> Option<GoBoard> {
    todo!()
}

pub fn gen_game(board: &mut GoBoard) {
    let mut rng = rand::thread_rng();
    let mut move_counter = 0;
    let mut allowed_searching_site_hashmap = HashMap::<[i32; 2], bool>::new();
    for i in 0..board.meta_data.size[0] {
        for j in 0..board.meta_data.size[1] {
            allowed_searching_site_hashmap.insert([i, j], true);
        }
    }

    board.board_state.consecutive_passes = 0; // indicator for the end of the game
    while board.board_state.consecutive_passes < 2 && move_counter < 20000 {
        // let mut test_board = board.clone();
        // test_board.board_state.consecutive_passes = 0;

        allowed_searching_site_hashmap =
            board.update_allowed_searching_site_hashmap(allowed_searching_site_hashmap);
        let n_allowed_site = allowed_searching_site_hashmap
            .iter()
            .filter(|(_, &value)| value)
            .map(|(&key, _)| key)
            .collect::<Vec<_>>()
            .len();
        println!(
            "Allowed sites for{}: {}",
            board.board_state.current_move_color, n_allowed_site
        );
        if n_allowed_site == 0 {
            board.pass_move();
            board.board_state.consecutive_passes += 1;
            move_counter += 1;
            println!("{}", board);
        } else {
            // when `n_allowed_site > 0`
            let seaching_site_list = allowed_searching_site_hashmap.keys().collect::<Vec<_>>();
            let test_move = seaching_site_list.choose(&mut rng).unwrap();

            // let mut ko_test_board = board.clone();
            // ko_test_board.try_place_stone_at(test_move);

            board.try_place_stone_at(test_move);

            board.board_state.consecutive_passes = 0; // succeess move needs to refresh the `consecutive_passes` counter
            move_counter += 1;
            println!(
                "{} is placed at {:?}",
                board.board_state.current_move_color.alternate(),
                test_move
            );
            println!("{}", board);
        }

        if board.board_state.consecutive_passes == 2 {
            println!("Consecutive Passes Detected!");
            println!("Game ENDs at move = {}", move_counter);
            println!("Final Board:");
            println!("{}", board);
            break;
        }
    }
}
