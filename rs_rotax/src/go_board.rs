use crate::go_stone::*;

use std::{
    collections::{hash_map::HashMap, HashSet},
    fmt,
};

const ERROR: f32 = 1.0E-8;

#[derive(Clone, Copy)]
pub struct MetaData {
    pub size: [i32; 2],
    pub komi: f32,
}

#[derive(Clone)]
pub struct BoardState {
    pub consecutive_passes: i32,
    pub current_move_color: Color,
    pub stone_pos_to_color_hashmap: HashMap<[i32; 2], Color>,
}

#[derive(Clone, Debug)]
pub struct StoneBlock {
    pub block_color: Color,
    pub stone_list: Vec<Stone>,
}
impl fmt::Display for StoneBlock {
    fn fmt(&self, io: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.stone_list.len() {
            0 => write!(io, ""), // write nothing,
            _ => write!(io, "{}{}", self.block_color, self.stone_list[0]),
        }
    }
}

#[derive(Clone, Debug)]
pub struct BlockInfo {
    pub block_list: Vec<StoneBlock>,
    pub block_liberty_list: Vec<usize>,
    pub block_eye_list: Vec<usize>,
    pub site_to_nearby_block_index_hashmap: HashMap<[i32; 2], Vec<usize>>, // for each site, find the block index for the nearby sites if exists
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

#[derive(Clone)]
pub struct GoBoard {
    pub meta_data: MetaData,
    pub board_state: BoardState,
    pub block_info: BlockInfo,
}
impl fmt::Display for GoBoard {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let [l1, l2] = self.meta_data.size;
        let mut board_string = format!("current board: (board size: {:?})  ", self.meta_data.size);
        // board_string.push_str("current board: (board size: {self.size}")
        for i in (0..=l1).rev() {
            for j in 0..=l2 {
                let pos = [j, i];
                match self.board_state.stone_pos_to_color_hashmap.get(&pos) {
                    None => {
                        if j <= l1 - 1 && i < l2 {
                            board_string += " +"
                        }
                    }
                    Some(&color) => board_string += &format!("{}", color),
                }
                if j == l1 - 1 && i >= 0 {
                    board_string += "\n"
                }
                if j == l1 && i > 0 {
                    board_string += &format!("{:2}", i - 1)
                };
            }
        }
        board_string += "  ";
        for i in 0..l1 {
            board_string += &format!("{:2}", i)
        }
        board_string += "\n";
        write!(f, "{}", board_string)
    }
}
impl GoBoard {
    pub fn new(size: [i32; 2]) -> Self {
        let meta_data = MetaData {
            size: size,
            komi: 7.5,
        };
        let board_state = BoardState {
            consecutive_passes: 0,
            current_move_color: Color::Black,
            stone_pos_to_color_hashmap: HashMap::<[i32; 2], Color>::new(),
        };
        let mut block_info = BlockInfo {
            block_list: Vec::<StoneBlock>::new(),
            block_liberty_list: Vec::<usize>::new(),
            block_eye_list: Vec::<usize>::new(),
            site_to_nearby_block_index_hashmap: HashMap::<[i32; 2], Vec<usize>>::new(),
        };
        for i in 0..size[0] {
            for j in 0..size[1] {
                block_info
                    .site_to_nearby_block_index_hashmap
                    .insert([i, j], Vec::<usize>::new());
            }
        }
        GoBoard {
            meta_data: meta_data,
            board_state: board_state,
            block_info: block_info,
        }
    }

    pub fn get_position_on_board(&self, pos: [i32; 2]) -> BoardPosition {
        let [l1, l2] = self.meta_data.size;
        use BoardPosition::*;
        match pos {
            [0, 0] => BottomLeftCorner,
            [x, 0] if x == l1 - 1 => BottomRightCorner,
            [0, y] if y == l2 - 1 => TopLeftCorner,
            [x, y] if x == l1 - 1 && y == l2 - 1 => TopRightCorner,
            [x, 0] if x > 0 && x < l1 - 1 => Bottom,
            [x, y] if x > 0 && x < l1 - 1 && y == l2 - 1 => Top,
            [0, y] if y > 0 && y < l2 - 1 => Left,
            [x, y] if y > 0 && y < l2 - 1 && x == l1 - 1 => Right,
            _ => Bulk,
        }
    }

    fn get_nearby_site_list(&self, &site: &[i32; 2]) -> Vec<[i32; 2]> {
        use BoardPosition::*;
        let [x, y] = site;
        match self.get_position_on_board(site) {
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

    /// This function handle block-merge only. The move legitimacy or stone capture event are left for further method
    pub fn update_block_list(&mut self, new_stone: &Stone) {
        // first, find the block indices that need to be merged
        let mut matching_block_indices = Vec::<usize>::new();
        for (block_ind, stone_block) in self.block_info.block_list.iter().enumerate() {
            if stone_block.block_color == new_stone.color {
                for stone in stone_block.stone_list.iter() {
                    if (distance(&stone, &new_stone) - 1.0) < ERROR {
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
                self.block_info.block_list.push(new_single_stone_block);
            }
            // if multiple blocks are found, merge them into a new large block (and delete the old ones)
            _ => {
                // start with a single-stone block, and then collected the matching ones
                let mut new_merged_block = StoneBlock {
                    block_color: new_stone.color,
                    stone_list: vec![new_stone.clone()],
                };
                for &block_ind in matching_block_indices.iter().rev() {
                    let stone_block_to_merge = self.block_info.block_list.remove(block_ind);

                    new_merged_block
                        .stone_list
                        .extend(stone_block_to_merge.stone_list.iter())
                }
                self.block_info.block_list.push(new_merged_block);
            }
        }
    }

    pub fn update_stone_pos_to_color_hashmap(&mut self) {
        self.board_state.stone_pos_to_color_hashmap.clear();
        for stone_block in self.block_info.block_list.iter() {
            for stone in &stone_block.stone_list {
                self.board_state
                    .stone_pos_to_color_hashmap
                    .insert(stone.pos, stone_block.block_color);
            }
        }
    }

    /// a site is defined to be an eye if the nearby sites are of the same color
    fn _is_eye(&self, &site: &[i32; 2]) -> bool {
        if self
            .board_state
            .stone_pos_to_color_hashmap
            .contains_key(&site)
        {
            let nearby_sites = self.get_nearby_site_list(&site);
            let mut black_count: usize = 0;
            let mut white_count: usize = 0;
            for &site in nearby_sites.iter() {
                use Color::*;
                match self.board_state.stone_pos_to_color_hashmap[&site] {
                    White => white_count += 1,
                    Black => black_count += 1,
                }
            }
            if black_count == nearby_sites.len() || white_count == nearby_sites.len() {
                return true;
            }
        }
        return false;
    }

    pub fn update_block_liberty_list_and_block_eye_list(&mut self) {
        self.block_info.block_liberty_list = Vec::<usize>::new();
        self.block_info.block_eye_list = Vec::<usize>::new();
        for stone_block in &self.block_info.block_list {
            let mut nearby_site_list_for_current_block = Vec::<[i32; 2]>::new();
            for stone in &stone_block.stone_list {
                nearby_site_list_for_current_block.extend(self.get_nearby_site_list(&stone.pos))
            }
            let unique_nearby_sites_set_for_current_block = nearby_site_list_for_current_block
                .into_iter()
                .collect::<HashSet<[i32; 2]>>();
            let mut unique_nearby_site_list_for_current_block =
                unique_nearby_sites_set_for_current_block
                    .iter()
                    .collect::<Vec<_>>();
            for (pos, _) in &self.board_state.stone_pos_to_color_hashmap {
                if unique_nearby_site_list_for_current_block.contains(&pos) {
                    unique_nearby_site_list_for_current_block.retain(|&x| x != pos)
                }
            }

            self.block_info
                .block_liberty_list
                .push(unique_nearby_site_list_for_current_block.len());

            let mut eye_count_for_current_block: usize = 0;
            for site in unique_nearby_site_list_for_current_block.iter() {
                if self._is_eye(site) {
                    eye_count_for_current_block += 1;
                }
            }
            self.block_info
                .block_eye_list
                .push(eye_count_for_current_block);
        }
    }

    fn get_nearby_block_ind_list(&self, site: &[i32; 2]) -> Vec<usize> {
        let nearby_site_list = self.get_nearby_site_list(site);
        let mut nearby_block_ind_list = Vec::<usize>::new();
        for &nearby_site in nearby_site_list.iter() {
            if self
                .board_state
                .stone_pos_to_color_hashmap
                .contains_key(&nearby_site)
            {
                'block_search_loop: for (block_ind, stone_block) in
                    self.block_info.block_list.iter().enumerate()
                {
                    for stone in stone_block.stone_list.iter() {
                        if stone.pos == nearby_site {
                            nearby_block_ind_list.push(block_ind);
                            break 'block_search_loop; // break this level of for loop
                        }
                    }
                }
            }
        }
        // we only store the unique block indices
        nearby_block_ind_list = nearby_block_ind_list
            .into_iter()
            .collect::<HashSet<_>>()
            .into_iter()
            .collect::<Vec<_>>();
        return nearby_block_ind_list;
    }

    pub fn update_site_to_nearby_block_index_hashmap(&mut self) {
        self.block_info.site_to_nearby_block_index_hashmap.clear();
        let [l1, l2] = self.meta_data.size;
        for i in 0..l1 {
            for j in 0..l2 {
                let site = [i, j];
                let nearby_block_ind_list = self.get_nearby_block_ind_list(&site);
                self.block_info
                    .site_to_nearby_block_index_hashmap
                    .insert(site, nearby_block_ind_list);
            }
        }
    }

    /// switch color only
    pub fn pass_move(&mut self) {
        println!("Move{} PASSED!!!\n", self.board_state.current_move_color);
        self.board_state.current_move_color = self.board_state.current_move_color.alternate();
    }

    /// check if capture occurs for the given move, *without* mutating current board
    fn _is_capture_move(&self, site: &[i32; 2]) -> bool {
        let stone_color_to_be_placed = self.board_state.current_move_color;
        match self.block_info.site_to_nearby_block_index_hashmap.get(site) {
            Some(nearby_block_ind_list) => {
                for &block_ind in nearby_block_ind_list.iter() {
                    let block_liberty = self.block_info.block_liberty_list[block_ind];
                    let block_color = self.block_info.block_list[block_ind].block_color;
                    // println!("{} liberty: {}", block_color, block_liberty);
                    if block_liberty == 1 && block_color != stone_color_to_be_placed {
                        // capture must occurs for the opponent color after current move
                        return true;
                    }
                }
                return false;
            }
            None => return false,
        }
    }

    /// check if suicide occurs for the given move, *without* mutating current board
    fn _is_suicide_move(&self, site: &[i32; 2]) -> bool {
        let nearby_site_list = self.get_nearby_site_list(site);
        for site in nearby_site_list.iter() {
            if !self
                .board_state
                .stone_pos_to_color_hashmap
                .contains_key(site)
            {
                // if the `nearby_site_list` contains some empty sites, it cannot be a suicide move
                return false;
            }
        }
        // now if all nearby sites are occupied
        let nearby_block_ind_list = self
            .block_info
            .site_to_nearby_block_index_hashmap
            .get(site)
            .unwrap();

        let mut nearby_block_counter_of_opponent_color = 0;
        let mut nearby_block_counter_of_current_move_color = 0;
        let mut nearby_block_counter_of_current_move_color_with_liberty_one = 0;
        for &block_ind in nearby_block_ind_list.iter() {
            if self.block_info.block_list[block_ind].block_color
                == self.board_state.current_move_color
            {
                nearby_block_counter_of_current_move_color += 1;
                if self.block_info.block_liberty_list[block_ind] == 1 {
                    nearby_block_counter_of_current_move_color_with_liberty_one += 1;
                }
            } else {
                nearby_block_counter_of_opponent_color += 1;
            }
        }
        if (nearby_block_counter_of_current_move_color
            == nearby_block_counter_of_current_move_color_with_liberty_one
            && nearby_block_counter_of_current_move_color > 0)
            || (nearby_block_counter_of_opponent_color > 0
                && nearby_block_counter_of_current_move_color == 0)
        {
            return true;
        } else {
            return false;
        }
    }

    pub fn update_all_board_data(&mut self, pos: &[i32; 2]) {
        let current_move = Stone {
            color: self.board_state.current_move_color,
            pos: *pos,
        };
        // the update order below is important: first, update the `block_list`, then update the `stone_pos_to_color_hashmap`. Next, using these two information to update all auxiliary info
        self.update_block_list(&current_move);
        self.update_stone_pos_to_color_hashmap();
        self.update_block_liberty_list_and_block_eye_list();
        self.update_site_to_nearby_block_index_hashmap();
        self.board_state.current_move_color = self.board_state.current_move_color.alternate();
        // self.show_board(pos);
    }

    /// ### Key method to determine if the given `pos` is a legal move
    ///
    /// For accurate treatment on the test move, we return `Option<(bool,bool)>` as `Option<(_is_capture, _is_suicide)>` for the given `pos`
    pub fn try_place_stone_at(&mut self, pos: &[i32; 2]) -> Option<(bool, bool)> {
        if self
            .board_state
            .stone_pos_to_color_hashmap
            .contains_key(pos)
        {
            // place at an occupied site, or out of board!
            return None;
        } else {
            let _is_capture = self._is_capture_move(pos);
            let _is_suicide = self._is_suicide_move(pos);
            // println!(
            //     "move{} {:?} `_is_capture`={:?}, `_is_suicide`={:?}",
            //     self.board_state.current_move_color, pos, _is_capture, _is_suicide
            // );
            match (_is_capture, _is_suicide) {
                (false, false) => {
                    // normal move
                    self.update_all_board_data(pos);
                    return Some((false, false));
                }
                (true, v) => {
                    // suicide with capture move
                    // we do not bother to place a virtual move to change the liberty condition
                    let mut block_ind_list_to_be_captured = Vec::<usize>::new();
                    for &block_ind in self
                        .block_info
                        .site_to_nearby_block_index_hashmap
                        .get(pos)
                        .unwrap()
                        .iter()
                    {
                        let block_liberty = self.block_info.block_liberty_list[block_ind];
                        let block_color = self.block_info.block_list[block_ind].block_color;
                        if block_liberty == 1 && block_color != self.board_state.current_move_color
                        {
                            // the next move must remove such stone-block
                            block_ind_list_to_be_captured.push(block_ind);
                        }
                    }
                    let new_block_list = self
                        .block_info
                        .block_list
                        .iter()
                        .cloned()
                        .enumerate()
                        .filter(|(block_ind, _)| !block_ind_list_to_be_captured.contains(block_ind))
                        .map(|(_, value)| value)
                        .collect::<Vec<StoneBlock>>();

                    self.block_info.block_list = new_block_list;
                    self.update_all_board_data(pos);

                    return Some((true, v));
                }
                (false, true) => {
                    // pure suicide: do nothing to the board
                    // println!("Check Input: pure suicide detected!!!");
                    // self.show_board_without_move();
                    return Some((false, true));
                }
            }
        }
    }

    pub fn show_board(&self, pos: &[i32; 2]) {
        println!(
            "gen move{} at: {:?}\nnext turn:{}",
            self.board_state.current_move_color.alternate(),
            pos,
            self.board_state.current_move_color
        );
        println!("{}", &self);
    }

    pub fn show_board_without_move(&self) {
        println!(
            "no legal gen move{} is generated!\nnext turn still:{}",
            self.board_state.current_move_color.alternate(),
            self.board_state.current_move_color
        );
        println!("{}", &self);
    }

    /// ignore the alternating-color rule and place stone with specific color on board
    pub fn try_place_stone_with_color_at(
        &mut self,
        pos: &[i32; 2],
        color: Color,
    ) -> Option<(bool, bool)> {
        self.board_state.current_move_color = color;
        return self.try_place_stone_at(pos);
    }

    /// Check if the pos is illegal for the given **test_board (as self)**
    /// Note: it does mutate the given board!
    fn _is_illegal_for_opponent(&mut self, pos: &[i32; 2]) -> bool {
        // temporarily change the color
        self.board_state.current_move_color = self.board_state.current_move_color.alternate();
        match self.try_place_stone_at(pos) {
            // Option<(_is_capture, _is_suicide)>
            Some((true, _)) | Some((false, false)) => {
                self.board_state.current_move_color =
                    self.board_state.current_move_color.alternate();
                return false;
            }
            None | Some((false, true)) => {
                // illegal move
                self.board_state.current_move_color =
                    self.board_state.current_move_color.alternate();
                return true;
            }
        }
    }

    pub fn update_allowed_searching_site_hashmap(
        &mut self,
        allowed_searching_site_hashmap: HashMap<[i32; 2], bool>,
    ) -> HashMap<[i32; 2], bool> {
        let mut new_allowed_searching_site_hashmap = allowed_searching_site_hashmap.clone();
        for site in allowed_searching_site_hashmap.keys() {
            let mut test_board = self.clone();
            match test_board.try_place_stone_at(site) {
                // Option<(_is_capture, _is_suicide)>
                None | Some((false, true)) => {
                    // if the site is already occupied, or the move is illegal, set the searching site to be false to exclude them
                    new_allowed_searching_site_hashmap.insert(*site, false);
                }
                Some((true, _)) => {
                    // if the test move does capture some stones, release more empty sites for search
                }
                Some((false, false)) => {
                    // is the test move is legal and normal for current player, chances may still such move to be placed at the key eye for the nearby block, which is a suicide behavior and we want to exclude that. This occurs when the test move is illegal for the opponent
                    let mut test_board = self.clone();
                    if test_board._is_illegal_for_opponent(site) {
                        // if is legal for current player, but illegal for the opponent to move, be cautious!
                        let nearby_block_ind_list = self
                            .block_info
                            .site_to_nearby_block_index_hashmap
                            .get(site)
                            .unwrap();

                        let nearby_block_eye_list = nearby_block_ind_list
                            .iter()
                            .map(|&block_ind| self.block_info.block_eye_list[block_ind])
                            .collect::<Vec<_>>();

                        let suicide_indicator_list = (1..nearby_block_ind_list.len())
                            .map(|i| nearby_block_eye_list[i] == 2)
                            .collect::<Vec<_>>();

                        if suicide_indicator_list.iter().any(|&x| x) {
                            // consider a virtual move on a virtual `another_test_board`
                            let mut another_test_board = self.clone();
                            another_test_board.try_place_stone_at(site);

                            let merged_block_ind_list = another_test_board
                                .block_info
                                .site_to_nearby_block_index_hashmap
                                .get(site)
                                .unwrap();
                            if merged_block_ind_list.len() > 0 {
                                let &merged_block_ind = merged_block_ind_list.first().unwrap();
                                let merged_block_liberty = another_test_board
                                    .block_info
                                    .block_liberty_list[merged_block_ind];
                                let merged_block_eye =
                                    another_test_board.block_info.block_eye_list[merged_block_ind];
                                if merged_block_eye < 2 && merged_block_liberty < 2 {
                                    println!("{} found site {:?} is suicide due to self-eye elimination so ignore the site! after move, libergy: {}, eye: {}", self.board_state.current_move_color, site, merged_block_liberty, merged_block_eye);

                                    new_allowed_searching_site_hashmap.insert(*site, false);
                                }
                            }
                        }
                    }
                }
            }
        }

        return new_allowed_searching_site_hashmap;
    }

    // pub fn update_ignored_searching_site_list(
    //     &mut self,
    //     ignored_searching_site_list: &mut Vec<[i32; 2]>,
    //     pos: &[i32; 2],
    // ) {
    //     if !ignored_searching_site_list.contains(pos) {
    //         let mut test_board = self.clone();
    //         if !test_board.try_place_stone_at(pos) {
    //             // if is illegal for current player, ignore such site for sure
    //             println!(
    //                 "{} found site {:?} is pure suicide so ignore it!",
    //                 self.board_state.current_move_color, pos
    //             );
    //             ignored_searching_site_list.push(*pos);
    //         } else {
    //             let mut test_board = self.clone();
    //             if test_board._is_illegal_for_opponent(pos) {
    //                 // if is legal for current player, but illegal for the opponent to move, be cautious!
    //                 let nearby_block_ind_list = self
    //                     .block_info
    //                     .site_to_nearby_block_index_hashmap
    //                     .get(pos)
    //                     .unwrap();

    //                 let nearby_block_eye_list = nearby_block_ind_list
    //                     .iter()
    //                     .map(|&block_ind| self.block_info.block_eye_list[block_ind])
    //                     .collect::<Vec<_>>();

    //                 let suicide_indicator_list = (1..nearby_block_ind_list.len())
    //                     .map(|i| nearby_block_eye_list[i] == 2)
    //                     .collect::<Vec<_>>();

    //                 if suicide_indicator_list.iter().any(|&x| x) {
    //                     // consider a virtual move on a virtual `another_test_board`
    //                     let mut another_test_board = self.clone();
    //                     another_test_board.try_place_stone_at(pos);

    //                     let merged_block_ind_list = another_test_board
    //                         .block_info
    //                         .site_to_nearby_block_index_hashmap
    //                         .get(pos)
    //                         .unwrap();
    //                     if merged_block_ind_list.len() > 0 {
    //                         let &merged_block_ind = merged_block_ind_list.first().unwrap();
    //                         let merged_block_liberty =
    //                             another_test_board.block_info.block_liberty_list[merged_block_ind];
    //                         let merged_block_eye =
    //                             another_test_board.block_info.block_eye_list[merged_block_ind];
    //                         if merged_block_eye < 2 && merged_block_liberty < 2 {
    //                             println!("{} found site {:?} is suicide due to self-eye elimination so ignore the site! after move, libergy: {}, eye: {}", self.board_state.current_move_color, pos, merged_block_liberty, merged_block_eye);

    //                             ignored_searching_site_list.push(*pos);
    //                         }
    //                     }
    //                 }
    //             }
    //         }
    //     }
    // }

    // pub fn generate_allowed_searching_site_list(
    //     &mut self,
    //     full_site_list: &Vec<[i32; 2]>,
    // ) -> Vec<[i32; 2]> {
    //     let allowed_searching_site_hashmap = HashMap::<[i32;2], bool>::new();

    //     let empty_site_list = full_site_list
    //         .iter()
    //         .cloned()
    //         .filter(|&x| !self.board_state.stone_pos_to_color_hashmap.contains_key(&x))
    //         .collect::<Vec<_>>();

    //     let mut allowed_searching_site_list = empty_site_list.clone();
    //     let mut ignored_searching_site_list = Vec::<[i32; 2]>::new();
    //     for &site in allowed_searching_site_list.iter() {
    //         self.update_ignored_searching_site_list(&mut ignored_searching_site_list, &site);
    //     }

    //     allowed_searching_site_list = allowed_searching_site_list
    //         .iter()
    //         .cloned()
    //         .filter(|&x| !ignored_searching_site_list.iter().any(|&y| y == x))
    //         .collect::<Vec<[i32; 2]>>();
    //     return allowed_searching_site_list;
    // }
}

pub fn distance(s1: &Stone, s2: &Stone) -> f32 {
    let delta_x = (s1.pos[0] - s2.pos[0]) as f32;
    let delta_y = (s1.pos[1] - s2.pos[1]) as f32;
    (delta_x * delta_x + delta_y * delta_y).sqrt()
}
