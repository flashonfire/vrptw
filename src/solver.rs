use rand::prelude::*;
use std::collections::VecDeque;

use crate::generator::random_solution;
use crate::model::{Route, Solution};
use crate::parser::VrptwData;

// ---------------------------------------------------------------------------
// Trait
// ---------------------------------------------------------------------------

pub trait Solver {
    fn name(&self) -> &str;
    fn neighborhoods(&self) -> &[Neighborhood] {
        &DEFAULT_NEIGHBORHOODS
    }
    fn parameters(&self) -> String {
        "-".to_string()
    }
    fn solve(&self, instance: &VrptwData) -> SolveResult;
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum Neighborhood {
    Relocate,
    Swap,
    TwoOpt,
}

static DEFAULT_NEIGHBORHOODS: [Neighborhood; 1] = [Neighborhood::Relocate];

pub fn neighborhoods_label(neighborhoods: &[Neighborhood]) -> String {
    let neighborhoods = if neighborhoods.is_empty() {
        &DEFAULT_NEIGHBORHOODS
    } else {
        neighborhoods
    };

    neighborhoods
        .iter()
        .map(|n| match n {
            Neighborhood::Relocate => "relocate",
            Neighborhood::Swap => "swap",
            Neighborhood::TwoOpt => "2opt",
        })
        .collect::<Vec<_>>()
        .join("+")
}

#[derive(Default, Clone)]
pub struct SolverStats {
    pub solutions_generated: usize,
    pub neighbors_attempted: usize,
    pub neighbors_accepted: usize,
}

pub struct SolveResult {
    pub solution: Solution,
    pub stats: SolverStats,
}

pub struct MoveCandidate {
    pub solution: Solution,
    pub moved_clients: Vec<usize>,
}

// ---------------------------------------------------------------------------
// Neighborhood: relocate one client to another position
// ---------------------------------------------------------------------------

fn relocate(
    solution: &Solution,
    from_route: usize,
    from_pos: usize,
    to_route: usize,
    to_pos: usize,
) -> Solution {
    let mut routes: Vec<Vec<usize>> = solution.routes.iter().map(|r| r.clients.clone()).collect();

    let client = routes[from_route].remove(from_pos);

    // to_pos was computed before the removal — adjust if same route and index shifted
    let mut to_pos = to_pos;
    if from_route == to_route && from_pos < to_pos {
        to_pos = to_pos.saturating_sub(1);
    }
    let to_pos = to_pos.min(routes[to_route].len());

    routes[to_route].insert(to_pos, client);

    Solution {
        routes: routes
            .into_iter()
            .filter(|r| !r.is_empty())
            .map(|clients| Route { clients })
            .collect(),
    }
}

fn swap_clients(
    solution: &Solution,
    route_a: usize,
    pos_a: usize,
    route_b: usize,
    pos_b: usize,
) -> Solution {
    let mut routes: Vec<Vec<usize>> = solution.routes.iter().map(|r| r.clients.clone()).collect();
    let tmp = routes[route_a][pos_a];
    routes[route_a][pos_a] = routes[route_b][pos_b];
    routes[route_b][pos_b] = tmp;

    Solution {
        routes: routes.into_iter().map(|clients| Route { clients }).collect(),
    }
}

fn two_opt(solution: &Solution, route_idx: usize, start: usize, end: usize) -> Solution {
    let mut routes: Vec<Vec<usize>> = solution.routes.iter().map(|r| r.clients.clone()).collect();
    if let Some(route) = routes.get_mut(route_idx) {
        route[start..=end].reverse();
    }
    Solution {
        routes: routes.into_iter().map(|clients| Route { clients }).collect(),
    }
}

fn random_relocate(solution: &Solution, rng: &mut impl Rng) -> Option<MoveCandidate> {
    let non_empty: Vec<usize> = solution
        .routes
        .iter()
        .enumerate()
        .filter(|(_, r)| !r.clients.is_empty())
        .map(|(i, _)| i)
        .collect();

    if non_empty.is_empty() {
        return None;
    }

    let from_route = non_empty[rng.random_range(0..non_empty.len())];
    let from_pos = rng.random_range(0..solution.routes[from_route].clients.len());
    let moved_client = solution.routes[from_route].clients[from_pos];
    let to_route = rng.random_range(0..solution.routes.len());
    let to_len = solution.routes[to_route].clients.len();
    let to_pos = if to_len == 0 {
        0
    } else {
        rng.random_range(0..=to_len)
    };

    Some(MoveCandidate {
        solution: relocate(solution, from_route, from_pos, to_route, to_pos),
        moved_clients: vec![moved_client],
    })
}

fn random_swap(solution: &Solution, rng: &mut impl Rng) -> Option<MoveCandidate> {
    let non_empty: Vec<usize> = solution
        .routes
        .iter()
        .enumerate()
        .filter(|(_, r)| !r.clients.is_empty())
        .map(|(i, _)| i)
        .collect();

    if non_empty.is_empty() {
        return None;
    }

    let route_a = non_empty[rng.random_range(0..non_empty.len())];
    let pos_a = rng.random_range(0..solution.routes[route_a].clients.len());
    let route_b = non_empty[rng.random_range(0..non_empty.len())];
    let pos_b = rng.random_range(0..solution.routes[route_b].clients.len());
    let moved_a = solution.routes[route_a].clients[pos_a];
    let moved_b = solution.routes[route_b].clients[pos_b];

    if route_a == route_b && pos_a == pos_b {
        return None;
    }

    Some(MoveCandidate {
        solution: swap_clients(solution, route_a, pos_a, route_b, pos_b),
        moved_clients: vec![moved_a, moved_b],
    })
}

fn random_two_opt(solution: &Solution, rng: &mut impl Rng) -> Option<MoveCandidate> {
    let candidates: Vec<usize> = solution
        .routes
        .iter()
        .enumerate()
        .filter(|(_, r)| r.clients.len() >= 3)
        .map(|(i, _)| i)
        .collect();

    if candidates.is_empty() {
        return None;
    }

    let route_idx = candidates[rng.random_range(0..candidates.len())];
    let len = solution.routes[route_idx].clients.len();
    let i = rng.random_range(0..len - 1);
    let k = rng.random_range(i + 1..len);

    Some(MoveCandidate {
        solution: two_opt(solution, route_idx, i, k),
        moved_clients: Vec::new(),
    })
}

fn random_neighbor(
    solution: &Solution,
    instance: &VrptwData,
    neighborhoods: &[Neighborhood],
    rng: &mut impl Rng,
) -> Option<MoveCandidate> {
    let neighborhoods = if neighborhoods.is_empty() {
        &DEFAULT_NEIGHBORHOODS
    } else {
        neighborhoods
    };

    let mut attempts = 0;
    while attempts < 3 {
        attempts += 1;
        let pick = neighborhoods[rng.random_range(0..neighborhoods.len())];

        let candidate = match pick {
            Neighborhood::Relocate => random_relocate(solution, rng),
            Neighborhood::Swap => random_swap(solution, rng),
            Neighborhood::TwoOpt => random_two_opt(solution, rng),
        };

        if let Some(candidate) = candidate {
            if candidate.solution.is_feasible(instance) {
                return Some(candidate);
            }
        }
    }

    None
}

// ---------------------------------------------------------------------------
// Random Walk
// ---------------------------------------------------------------------------

pub struct RandomWalk {
    pub iterations: usize,
    pub neighborhoods: Vec<Neighborhood>,
}

impl Solver for RandomWalk {
    fn name(&self) -> &str {
        "Random Walk"
    }
    fn neighborhoods(&self) -> &[Neighborhood] {
        if self.neighborhoods.is_empty() {
            &DEFAULT_NEIGHBORHOODS
        } else {
            &self.neighborhoods
        }
    }
    fn parameters(&self) -> String {
        format!("iterations={}", self.iterations)
    }
    fn solve(&self, instance: &VrptwData) -> SolveResult {
        let mut current = random_solution(instance);
        let mut rng = rand::rng();
        let mut stats = SolverStats {
            solutions_generated: 1,
            ..SolverStats::default()
        };
        for _ in 0..self.iterations {
            stats.neighbors_attempted += 1;
            if let Some(candidate) = random_neighbor(&current, instance, self.neighborhoods(), &mut rng) {
                stats.solutions_generated += 1;
                stats.neighbors_accepted += 1;
                current = candidate.solution;
            }
        }
        SolveResult {
            solution: current,
            stats,
        }
    }
}

// ---------------------------------------------------------------------------
// Descent
// ---------------------------------------------------------------------------

pub struct Descent {
    pub iterations: usize,
    pub neighborhoods: Vec<Neighborhood>,
}

impl Solver for Descent {
    fn name(&self) -> &str {
        "Descent"
    }
    fn neighborhoods(&self) -> &[Neighborhood] {
        if self.neighborhoods.is_empty() {
            &DEFAULT_NEIGHBORHOODS
        } else {
            &self.neighborhoods
        }
    }
    fn parameters(&self) -> String {
        format!("iterations={}", self.iterations)
    }
    fn solve(&self, instance: &VrptwData) -> SolveResult {
        let mut best = random_solution(instance);
        let mut rng = rand::rng();
        let mut stats = SolverStats {
            solutions_generated: 1,
            ..SolverStats::default()
        };
        for _ in 0..self.iterations {
            stats.neighbors_attempted += 1;
            let Some(candidate) = random_neighbor(&best, instance, self.neighborhoods(), &mut rng) else {
                continue;
            };
            stats.solutions_generated += 1;
            if candidate.solution.total_distance(instance) < best.total_distance(instance) {
                best = candidate.solution;
                stats.neighbors_accepted += 1;
            }
        }
        SolveResult {
            solution: best,
            stats,
        }
    }
}

// ---------------------------------------------------------------------------
// Tabu Search
// ---------------------------------------------------------------------------

pub struct TabuSearch {
    pub iterations: usize,
    pub tabu_tenure: usize,
    pub attempts_per_iter: usize,
    pub neighborhoods: Vec<Neighborhood>,
}

impl Solver for TabuSearch {
    fn name(&self) -> &str {
        "Tabu Search"
    }
    fn neighborhoods(&self) -> &[Neighborhood] {
        if self.neighborhoods.is_empty() {
            &DEFAULT_NEIGHBORHOODS
        } else {
            &self.neighborhoods
        }
    }
    fn parameters(&self) -> String {
        format!(
            "iterations={};tabu_tenure={};attempts_per_iter={}",
            self.iterations, self.tabu_tenure, self.attempts_per_iter
        )
    }
    fn solve(&self, instance: &VrptwData) -> SolveResult {
        let mut rng = rand::rng();
        let mut current = random_solution(instance);
        let mut best = current.clone();
        let mut tabu: VecDeque<usize> = VecDeque::new();
        let mut stats = SolverStats {
            solutions_generated: 1,
            ..SolverStats::default()
        };

        for _ in 0..self.iterations {
            let mut best_move: Option<(Solution, Vec<usize>)> = None;

            for _ in 0..self.attempts_per_iter {
                stats.neighbors_attempted += 1;
                let Some(candidate) =
                    random_neighbor(&current, instance, self.neighborhoods(), &mut rng)
                else {
                    continue;
                };

                if !candidate.moved_clients.is_empty()
                    && candidate
                        .moved_clients
                        .iter()
                        .any(|c| tabu.contains(c))
                {
                    continue;
                }

                stats.solutions_generated += 1;

                let is_better = best_move.as_ref().is_none_or(|(bn, _)| {
                    candidate.solution.total_distance(instance) < bn.total_distance(instance)
                });

                if is_better {
                    let tabu_clients = if candidate.moved_clients.is_empty() {
                        Vec::new()
                    } else {
                        candidate.moved_clients.clone()
                    };
                    best_move = Some((candidate.solution, tabu_clients));
                }
            }

            if let Some((neighbor, moved_clients)) = best_move {
                if neighbor.total_distance(instance) < best.total_distance(instance) {
                    best = neighbor.clone();
                }
                current = neighbor;
                stats.neighbors_accepted += 1;
                for moved_client in moved_clients {
                    tabu.push_back(moved_client);
                    if tabu.len() > self.tabu_tenure {
                        tabu.pop_front();
                    }
                }
            }
        }

        SolveResult {
            solution: best,
            stats,
        }
    }
}

// ---------------------------------------------------------------------------
// Simulated Annealing
// ---------------------------------------------------------------------------

pub struct SimulatedAnnealing {
    pub initial_temp: f64,
    pub cooling_rate: f64,
    pub iterations: usize,
    pub neighborhoods: Vec<Neighborhood>,
}

impl Solver for SimulatedAnnealing {
    fn name(&self) -> &str {
        "Simulated Annealing"
    }
    fn neighborhoods(&self) -> &[Neighborhood] {
        if self.neighborhoods.is_empty() {
            &DEFAULT_NEIGHBORHOODS
        } else {
            &self.neighborhoods
        }
    }
    fn parameters(&self) -> String {
        format!(
            "iterations={};initial_temp={:.2};cooling_rate={:.4}",
            self.iterations, self.initial_temp, self.cooling_rate
        )
    }
    fn solve(&self, instance: &VrptwData) -> SolveResult {
        let mut current = random_solution(instance);
        let mut rng = rand::rng();
        let mut best = current.clone();
        let mut temp = self.initial_temp;
        let mut stats = SolverStats {
            solutions_generated: 1,
            ..SolverStats::default()
        };

        for _ in 0..self.iterations {
            stats.neighbors_attempted += 1;
            if let Some(candidate) = random_neighbor(&current, instance, self.neighborhoods(), &mut rng) {
                stats.solutions_generated += 1;
                let delta = candidate.solution.total_distance(instance) - current.total_distance(instance);
                if delta < 0.0 || rng.random::<f64>() < (-delta / temp).exp() {
                    current = candidate.solution;
                    if current.total_distance(instance) < best.total_distance(instance) {
                        best = current.clone();
                    }
                    stats.neighbors_accepted += 1;
                }
            }
            temp *= self.cooling_rate;
        }

        SolveResult {
            solution: best,
            stats,
        }
    }
}
