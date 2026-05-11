use crate::parser::VrptwData;

// ---------------------------------------------------------------------------
// Core types
// ---------------------------------------------------------------------------

/// An ordered sequence of client indices (into `VrptwData::clients`).
/// Implicitly starts and ends at the depot.
#[derive(Clone)]
pub struct Route {
    pub clients: Vec<usize>,
}

/// A complete solution: a set of routes covering all clients.
#[derive(Clone)]
pub struct Solution {
    pub routes: Vec<Route>,
}

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------

fn euclidean(ax: f64, ay: f64, bx: f64, by: f64) -> f64 {
    ((ax - bx).powi(2) + (ay - by).powi(2)).sqrt()
}

/// Distance between two nodes, where node 0 is the depot and node i+1 is client i.
fn node_distance(instance: &VrptwData, a: usize, b: usize) -> f64 {
    let (ax, ay) = node_coords(instance, a);
    let (bx, by) = node_coords(instance, b);
    euclidean(ax, ay, bx, by)
}

fn node_coords(instance: &VrptwData, node: usize) -> (f64, f64) {
    if node == 0 {
        (instance.depot.x, instance.depot.y)
    } else {
        let c = &instance.clients[node - 1];
        (c.x, c.y)
    }
}

// ---------------------------------------------------------------------------
// Route evaluation
// ---------------------------------------------------------------------------

impl Route {
    /// Total travel distance of this route (depot → clients → depot).
    pub fn distance(&self, instance: &VrptwData) -> f64 {
        if self.clients.is_empty() {
            return 0.0;
        }

        // node indices: 0 = depot, client i → node i+1
        let nodes: Vec<usize> = std::iter::once(0)
            .chain(self.clients.iter().map(|&c| c + 1))
            .chain(std::iter::once(0))
            .collect();

        nodes
            .windows(2)
            .map(|w| node_distance(instance, w[0], w[1]))
            .sum()
    }

    /// Total demand carried on this route.
    pub fn load(&self, instance: &VrptwData) -> u32 {
        self.clients
            .iter()
            .map(|&c| instance.clients[c].demand)
            .sum()
    }

    /// Simulates the route and returns the arrival time at each client stop (after waiting
    /// if early). Returns `None` if any time window is violated.
    ///
    /// Time starts at 0 (depot departure). Travel time equals Euclidean distance.
    pub fn arrival_times(&self, instance: &VrptwData) -> Option<Vec<f64>> {
        let mut times = Vec::with_capacity(self.clients.len());
        let mut current_time = instance.depot.ready_time as f64;
        let mut current_node = 0usize;

        for &ci in &self.clients {
            let client = &instance.clients[ci];
            let travel = node_distance(instance, current_node, ci + 1);
            let arrival = current_time + travel;

            if arrival > client.due_time as f64 {
                return None; // too late
            }

            let start_service = arrival.max(client.ready_time as f64);
            times.push(start_service);

            current_time = start_service + client.service_time as f64;
            current_node = ci + 1;
        }

        // Check return to depot within its time window
        let return_travel = node_distance(instance, current_node, 0);
        let return_time = current_time + return_travel;
        if return_time > instance.depot.due_time as f64 {
            return None;
        }

        Some(times)
    }

    pub fn is_feasible(&self, instance: &VrptwData) -> bool {
        self.load(instance) <= instance.max_quantity && self.arrival_times(instance).is_some()
    }
}

// ---------------------------------------------------------------------------
// Solution evaluation
// ---------------------------------------------------------------------------

impl Solution {
    pub fn total_distance(&self, instance: &VrptwData) -> f64 {
        self.routes.iter().map(|r| r.distance(instance)).sum()
    }

    pub fn nb_vehicles(&self) -> usize {
        self.routes.len()
    }

    /// Checks capacity and time windows on every route, and that every client
    /// is visited exactly once.
    pub fn is_feasible(&self, instance: &VrptwData) -> bool {
        if !self.routes.iter().all(|r| r.is_feasible(instance)) {
            return false;
        }

        let mut visited = vec![false; instance.clients.len()];
        for route in &self.routes {
            for &ci in &route.clients {
                if visited[ci] {
                    return false; // visited twice
                }
                visited[ci] = true;
            }
        }

        visited.iter().all(|&v| v) // every client visited
    }
}
