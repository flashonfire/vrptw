use rand::seq::SliceRandom;

use crate::model::{Route, Solution};
use crate::parser::VrptwData;

/// Builds a random feasible solution using a greedy random insertion.
///
/// Clients are shuffled, then each client is appended to the current route if
/// feasible, or pushed to a new route otherwise.
pub fn random_solution(instance: &VrptwData) -> Solution {
    let mut order: Vec<usize> = (0..instance.clients.len()).collect();
    let mut rng = rand::rng();
    order.shuffle(&mut rng);

    let mut routes: Vec<Route> = vec![Route { clients: vec![] }];

    for client in order {
        let current = routes.last_mut().unwrap();
        current.clients.push(client);

        if !current.is_feasible(instance) {
            current.clients.pop();
            routes.push(Route {
                clients: vec![client],
            });
        }
    }

    let solution = Solution { routes };
    assert!(
        solution.is_feasible(instance),
        "random_solution produced an infeasible solution"
    );
    solution
}
