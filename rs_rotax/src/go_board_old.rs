use crate::go_stone::*;
use std::{collections::hash_map::HashMap, fmt};

const ERROR: f32 = 1.0E-8;

#[derive(Clone)]
struct StoneBlock {
    block_color: Color,
    stone_list: Vec<Stone>,
}
impl fmt::Display for StoneBlock {
    fn fmt(&self, io: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.stone_list.len() {
            0 => write!(io, ""), // write nothing,
            _ => write!(io, "{}{}", self.block_color, self.stone_list[0]),
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub enum BoardPosition {
    Bulk,
    Left,
    Right,
    Top,
    Bottom,
    TopLeftCorner,
    TopRightCorner,
    BottomLeftCorner,
    BottomRightCorner,
}

struct BlockInfo {}

#[derive(Clone)]
pub struct GoBoard {
    size: [i32; 2],
    komi: f32,
    consecutive_passes: i32,
    current_move_color: Color,
    block_list: Vec<StoneBlock>,
    block_liberty_list: Vec<i32>,
    block_eye_list: Vec<i32>,
    pos_to_color_hashmap: HashMap<[i32; 2], Color>,
    pos_to_nearby_block_index_hashmap: HashMap<[i32; 2], Vec<usize>>, // for each site, find the block index for the nearby sites if exists
}

impl GoBoard {
    pub fn new() -> Self {
        GoBoard {
            size: [19, 19],
            komi: 7.5,
            consecutive_passes: 0,
            current_move_color: Color::Black,
            block_list: vec![],
            block_liberty_list: vec![],
            block_eye_list: vec![],
            pos_to_color_hashmap: HashMap::<[i32; 2], Color>::new(),
            pos_to_nearby_block_index_hashmap: HashMap::<[i32; 2], Vec<usize>>::new(),
        }
    }

    pub fn update_block_list(&mut self, new_stone: &Stone) {
        // first, find the block indices that need to be merged
        let mut matching_block_indices = Vec::<usize>::new();
        for (block_ind, stone_block) in self.block_list.iter().enumerate() {
            if stone_block.block_color == new_stone.color {
                for stone in stone_block.stone_list.iter() {
                    if distance(&stone, &new_stone) < ERROR {
                        matching_block_indices.push(block_ind);
                        break;
                    }
                }
            }
        }
        match matching_block_indices.len() {
            // if no matching block is found, create a new single-stone block
            0 => {
                let new_single_stone_block = StoneBlock {
                    block_color: new_stone.color,
                    stone_list: vec![new_stone.clone()],
                };
                self.block_list.push(new_single_stone_block);
            }
            // if multiple blocks are found, merge them into a new large block (and delete the old ones)
            _ => {
                let mut new_merged_block = StoneBlock {
                    block_color: new_stone.color,
                    stone_list: vec![new_stone.clone()],
                };
                for &block_ind in matching_block_indices.iter() {
                    let stone_block_to_merge = self.block_list.remove(block_ind);
                    new_merged_block
                        .stone_list
                        .extend(stone_block_to_merge.stone_list.iter())
                }

                self.block_list.push(new_merged_block);
            }
        }
    }

    pub fn update_pos_to_color_map(&mut self) {
        self.pos_to_color_hashmap = HashMap::<[i32; 2], Color>::new();
        for stone_block in self.block_list.iter() {
            for stone in &stone_block.stone_list {
                self.pos_to_color_hashmap
                    .insert(stone.pos, stone_block.block_color);
            }
        }
    }

    pub fn get_board_position(&self, pos: [i32; 2]) -> BoardPosition {
        let [L1, L2] = self.size;
        use BoardPosition::*;
        match pos {
            [0, 0] => BottomLeftCorner,
            [x, 0] if x == L1 => BottomRightCorner,
            [0, y] if y == L2 => TopLeftCorner,
            [x, y] if x == L1 && y == L2 => TopRightCorner,
            [x, 0] if x > 0 && x < L1 => Bottom,
            [x, y] if x > 0 && x < L1 && y == L2 => Top,
            [0, y] if y > 0 && y < L2 => Left,
            [x, y] if y > 0 && y < L2 && x == L1 => Right,
            _ => Bulk,
        }
    }

    fn get_nearest_nearby_sites(&self, site: [i32; 2]) -> Vec<[i32; 2]> {
        use BoardPosition::*;
        let [x, y] = site;
        match self.get_board_position(site) {
            Bulk => vec![[x - 1, y], [x + 1, y], [x, y + 1], [x, y - 1]],
            Bottom => vec![[x - 1, y], [x + 1, y], [x, y + 1]],
            Top => vec![[x - 1, y], [x + 1, y], [x, y - 1]],
            Left => vec![[x + 1, y], [x, y + 1], [x, y - 1]],
            Right => vec![[x - 1, y], [x, y + 1], [x, y - 1]],
            BottomLeftCorner => vec![[x + 1, y], [x, y + 1]],
            BottomRightCorner => vec![[x - 1, y], [x, y + 1]],
            TopLeftCorner => vec![[x + 1, y], [x, y - 1]],
            TopRightCorner => vec![[x - 1, y], [x, y - 1]],
        }
    }

    pub fn update_nearby_block_indices(&mut self) {
        self.pos_to_nearby_block_index_hashmap.clear();
        for (block_index, stone_block) in self.block_list.iter().enumerate() {
            for stone in &stone_block.stone_list {
                let nearby_sites = self.get_nearest_nearby_sites(stone.pos);
                for site in nearby_sites {
                    if !self.pos_to_color_hashmap.contains_key(&site) {
                        self.pos_to_nearby_block_index_hashmap
                            .entry(site)
                            .or_insert_with(|| Vec::new())
                            .push(block_index)
                        // a neat way to add key values of vector type (after pushing block indices)
                    }
                }
            }
        }
    }
}

impl fmt::Display for GoBoard {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let [L1, L2] = self.size;
        let mut board_string = format!("current board: (board size: {:?})  ", self.size);
        // board_string.push_str("current board: (board size: {self.size}")
        for i in (0..=L1).rev() {
            for j in 0..=L2 {
                let pos = [j, i];
                match self.pos_to_color_hashmap.get(&pos) {
                    None => {
                        if j <= L1 - 1 && i < L2 {
                            board_string += " +"
                        }
                    }
                    Some(&color) => board_string += &format!("{}", color),
                }
                if j == L1 - 1 && i >= 0 {
                    board_string += "\n"
                }
                if j == L1 && i > 0 {
                    board_string += &format!("{:2}", i - 1)
                };
            }
        }
        board_string += "  ";
        for i in 0..L1 {
            board_string += &format!("{:2}", i)
        }
        board_string += "\n";
        write!(f, "{}", board_string)
    }
}

pub struct BoardInfo {}

fn distance(s1: &Stone, s2: &Stone) -> f32 {
    let delta_x = (s1.pos[0] - s2.pos[0]) as f32;
    let delta_y = (s1.pos[1] - s2.pos[1]) as f32;
    (delta_x * delta_x + delta_y * delta_y).sqrt()
}
