use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Color {
    White,
    Black,
}
impl Color {
    pub fn alternate(&self) -> Self {
        use Color::*;
        match self {
            White => Black,
            Black => White,
        }
    }
}
impl fmt::Display for Color {
    fn fmt(&self, io: &mut fmt::Formatter) -> fmt::Result {
        use colored::Colorize;
        use Color::*;

        match self {
            Black => write!(io, "{}", " ⬤".red().bold()),
            White => write!(io, "{}", " ⬤".blue().bold()),
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Stone {
    pub color: Color,
    pub pos: [i32; 2],
}
impl Stone {
    pub fn new(color: Color, pos: [i32; 2]) -> Self {
        Stone {
            color: color,
            pos: pos,
        }
    }
}
impl fmt::Display for Stone {
    fn fmt(&self, io: &mut fmt::Formatter) -> fmt::Result {
        write!(io, "{}", self.color)
    }
}
