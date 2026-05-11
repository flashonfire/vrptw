mod generator;
mod model;
mod parser;
mod solver;
mod visualize;

use anyhow::Result;

use solver::*;
use std::collections::HashMap;
use std::fs;
use std::io::Write;
use std::path::Path;
use std::time::Instant;

fn main() -> Result<()> {
    let datasets = [
        "data/data101.vrp",
        "data/data102.vrp",
        "data/data1101.vrp",
        "data/data1102.vrp",
        "data/data111.vrp",
        "data/data112.vrp",
        "data/data1201.vrp",
        "data/data1202.vrp",
        "data/data201.vrp",
        "data/data202.vrp",
    ];

    let solvers: Vec<Box<dyn Solver>> = vec![
        Box::new(RandomWalk {
            iterations: 5_000,
            neighborhoods: vec![Neighborhood::Relocate],
        }),
        Box::new(RandomWalk {
            iterations: 5_000,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap],
        }),
        Box::new(RandomWalk {
            iterations: 5_000,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap, Neighborhood::TwoOpt],
        }),
        Box::new(Descent {
            iterations: 5_000,
            neighborhoods: vec![Neighborhood::Relocate],
        }),
        Box::new(Descent {
            iterations: 5_000,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap],
        }),
        Box::new(Descent {
            iterations: 5_000,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap, Neighborhood::TwoOpt],
        }),
        Box::new(TabuSearch {
            iterations: 500,
            tabu_tenure: 20,
            attempts_per_iter: 50,
            neighborhoods: vec![Neighborhood::Relocate],
        }),
        Box::new(TabuSearch {
            iterations: 500,
            tabu_tenure: 20,
            attempts_per_iter: 50,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap],
        }),
        Box::new(TabuSearch {
            iterations: 500,
            tabu_tenure: 20,
            attempts_per_iter: 50,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap, Neighborhood::TwoOpt],
        }),
        Box::new(SimulatedAnnealing {
            initial_temp: 500.0,
            cooling_rate: 0.995,
            iterations: 10_000,
            neighborhoods: vec![Neighborhood::Relocate],
        }),
        Box::new(SimulatedAnnealing {
            initial_temp: 500.0,
            cooling_rate: 0.995,
            iterations: 10_000,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap],
        }),
        Box::new(SimulatedAnnealing {
            initial_temp: 500.0,
            cooling_rate: 0.995,
            iterations: 10_000,
            neighborhoods: vec![Neighborhood::Relocate, Neighborhood::Swap, Neighborhood::TwoOpt],
        }),
    ];

    let output_root = "outputs";
    fs::create_dir_all(output_root)?;

    let mut rows: Vec<TableRow> = Vec::new();
    let mut stats_off: HashMap<(String, String, String, String), ConfigStats> = HashMap::new();
    let mut stats_on: HashMap<(String, String, String, String), ConfigStats> = HashMap::new();

    for path in datasets {
        let file_stem = Path::new(path)
            .file_stem()
            .and_then(|s| s.to_str())
            .unwrap_or(path);
        let dataset_dir = format!("{}/{}", output_root, file_stem);
        fs::create_dir_all(&dataset_dir)?;
        let mut csv = std::fs::File::create(format!("{}/results.csv", dataset_dir))?;
        writeln!(
            csv,
            "dataset,tw,solver,neighborhood,params,vehicles,distance,ms,solutions_generated,neighbors_attempted,neighbors_accepted"
        )?;

        let base = parser::load(path)?;
        for (tw_label, instance) in [
            ("off", base.without_time_windows()),
            ("on", base.clone()),
        ] {
            for solver in &solvers {
                let start = Instant::now();
                let result = solver.solve(&instance);
                let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;

                let solution = result.solution;
                let distance = solution.total_distance(&instance);

                let solver_name = solver.name().to_lowercase().replace(' ', "_");
                let params = solver.parameters();
                let neighbor = neighborhoods_label(solver.neighborhoods());
                let solver_label = solver.name().to_string();

                rows.push(TableRow {
                    dataset: file_stem.to_string(),
                    tw: tw_label.to_string(),
                    solver: solver_label,
                    neighbor: neighbor.clone(),
                    params: params.clone(),
                    vehicles: solution.nb_vehicles().to_string(),
                    distance: format!("{:.2}", distance),
                    time_ms: format!("{:.2}", elapsed_ms),
                    solutions: result.stats.solutions_generated.to_string(),
                    neighbors_attempted: result.stats.neighbors_attempted.to_string(),
                    neighbors_accepted: result.stats.neighbors_accepted.to_string(),
                });

                let key = (
                    file_stem.to_string(),
                    solver.name().to_string(),
                    neighbor.clone(),
                    params.clone(),
                );
                let target = if tw_label == "on" {
                    &mut stats_on
                } else {
                    &mut stats_off
                };
                target
                    .entry(key)
                    .or_insert_with(ConfigStats::default)
                    .update(
                        distance,
                        elapsed_ms,
                        result.stats.solutions_generated,
                        result.stats.neighbors_attempted,
                        result.stats.neighbors_accepted,
                    );

                writeln!(
                    csv,
                    "{},{},{},{},{},{},{:.2},{:.2},{},{},{}",
                    file_stem,
                    tw_label,
                    solver.name(),
                    neighborhoods_label(solver.neighborhoods()),
                    solver.parameters(),
                    solution.nb_vehicles(),
                    distance,
                    elapsed_ms,
                    result.stats.solutions_generated,
                    result.stats.neighbors_attempted,
                    result.stats.neighbors_accepted
                )?;

                let out_path = format!(
                    "{}/{}_{}.png",
                    dataset_dir, tw_label, solver_name
                );
                visualize::visualize(&instance, &solution, &out_path)?;
            }
        }
    }

    print_table(&rows);
    print_config_tables_by_dataset("TW off", &stats_off);
    print_config_tables_by_dataset("TW on", &stats_on);

    Ok(())
}

struct TableRow {
    dataset: String,
    tw: String,
    solver: String,
    neighbor: String,
    params: String,
    vehicles: String,
    distance: String,
    time_ms: String,
    solutions: String,
    neighbors_attempted: String,
    neighbors_accepted: String,
}


fn print_table(rows: &[TableRow]) {
    let headers = [
        "Dataset",
        "TW",
        "Solver",
        "Neighbor",
        "Params",
        "Veh",
        "Distance",
        "Time(ms)",
        "Solutions",
        "NeighborsAttempted",
        "NeighborsAccepted",
    ];

    let mut widths = headers.iter().map(|h| h.len()).collect::<Vec<usize>>();
    for row in rows {
        let values = [
            row.dataset.as_str(),
            row.tw.as_str(),
            row.solver.as_str(),
            row.neighbor.as_str(),
            row.params.as_str(),
            row.vehicles.as_str(),
            row.distance.as_str(),
            row.time_ms.as_str(),
            row.solutions.as_str(),
            row.neighbors_attempted.as_str(),
            row.neighbors_accepted.as_str(),
        ];
        for (i, value) in values.iter().enumerate() {
            widths[i] = widths[i].max(value.len());
        }
    }

    let header_line = format!(
        "{:<w0$} | {:<w1$} | {:<w2$} | {:<w3$} | {:<w4$} | {:>w5$} | {:>w6$} | {:>w7$} | {:>w8$} | {:>w9$} | {:>w10$}",
        headers[0],
        headers[1],
        headers[2],
        headers[3],
        headers[4],
        headers[5],
        headers[6],
        headers[7],
        headers[8],
        headers[9],
        headers[10],
        w0 = widths[0],
        w1 = widths[1],
        w2 = widths[2],
        w3 = widths[3],
        w4 = widths[4],
        w5 = widths[5],
        w6 = widths[6],
        w7 = widths[7],
        w8 = widths[8],
        w9 = widths[9],
        w10 = widths[10],
    );
    println!("{}", header_line);
    println!("{}", "-".repeat(header_line.len()));

    for row in rows {
        println!(
            "{:<w0$} | {:<w1$} | {:<w2$} | {:<w3$} | {:<w4$} | {:>w5$} | {:>w6$} | {:>w7$} | {:>w8$} | {:>w9$} | {:>w10$}",
            row.dataset,
            row.tw,
            row.solver,
            row.neighbor,
            row.params,
            row.vehicles,
            row.distance,
            row.time_ms,
            row.solutions,
            row.neighbors_attempted,
            row.neighbors_accepted,
            w0 = widths[0],
            w1 = widths[1],
            w2 = widths[2],
            w3 = widths[3],
            w4 = widths[4],
            w5 = widths[5],
            w6 = widths[6],
            w7 = widths[7],
            w8 = widths[8],
            w9 = widths[9],
            w10 = widths[10],
        );
    }
}

#[derive(Default, Clone)]
struct ConfigStats {
    runs: usize,
    distance_sum: f64,
    time_sum: f64,
    solutions_sum: usize,
    neighbors_attempted_sum: usize,
    neighbors_accepted_sum: usize,
}

impl ConfigStats {
    fn update(
        &mut self,
        distance: f64,
        time_ms: f64,
        solutions_generated: usize,
        neighbors_attempted: usize,
        neighbors_accepted: usize,
    ) {
        self.runs += 1;
        self.distance_sum += distance;
        self.time_sum += time_ms;
        self.solutions_sum += solutions_generated;
        self.neighbors_attempted_sum += neighbors_attempted;
        self.neighbors_accepted_sum += neighbors_accepted;
    }

    fn avg_distance(&self) -> f64 {
        if self.runs == 0 {
            0.0
        } else {
            self.distance_sum / self.runs as f64
        }
    }

    fn avg_time(&self) -> f64 {
        if self.runs == 0 {
            0.0
        } else {
            self.time_sum / self.runs as f64
        }
    }

}

fn print_config_tables_by_dataset(
    label: &str,
    stats: &HashMap<(String, String, String, String), ConfigStats>,
) {
    let mut datasets: Vec<String> = stats
        .keys()
        .map(|(dataset, _, _, _)| dataset.clone())
        .collect();
    datasets.sort();
    datasets.dedup();

    println!("\n{}", label);
    println!("{}", "-".repeat(label.len()));

    for dataset in datasets {
        let mut entries: Vec<(String, String, String, ConfigStats)> = stats
            .iter()
            .filter(|((d, _, _, _), _)| d == &dataset)
            .map(|((_, solver, neighbor, params), v)| {
                (solver.clone(), neighbor.clone(), params.clone(), v.clone())
            })
            .collect();

        entries.sort_by(|a, b| a.0.cmp(&b.0).then(a.1.cmp(&b.1)).then(a.2.cmp(&b.2)));

        println!("\nDataset: {}", dataset);
        print_compact_table(
            "Qualite (distance moyenne)",
            "AvgDistance",
            "DeltaBest",
            &entries,
            |e| e.3.avg_distance(),
            true,
        );
        print_compact_table(
            "Rapidite (temps moyen ms)",
            "AvgTimeMs",
            "DeltaBest",
            &entries,
            |e| e.3.avg_time(),
            true,
        );
    }
}

fn print_compact_table(
    title: &str,
    metric_label: &str,
    delta_label: &str,
    entries: &[(String, String, String, ConfigStats)],
    metric: impl Fn(&(String, String, String, ConfigStats)) -> f64,
    best_is_min: bool,
) {
    println!("\n{}", title);
    println!("{}", "-".repeat(title.len()));
    let mut rows: Vec<(String, String, String, f64, f64)> = entries
        .iter()
        .map(|e| (e.0.clone(), e.1.clone(), e.2.clone(), metric(e), 0.0))
        .collect();
    let best = if best_is_min {
        rows.iter().map(|r| r.3).fold(f64::INFINITY, |a, b| a.min(b))
    } else {
        rows.iter().map(|r| r.3).fold(f64::NEG_INFINITY, |a, b| a.max(b))
    };
    for row in &mut rows {
        row.4 = if best_is_min { row.3 - best } else { best - row.3 };
    }

    if best_is_min {
        rows.sort_by(|a, b| a.3.total_cmp(&b.3).then(a.0.cmp(&b.0)).then(a.1.cmp(&b.1)).then(a.2.cmp(&b.2)));
    } else {
        rows.sort_by(|a, b| b.3.total_cmp(&a.3).then(a.0.cmp(&b.0)).then(a.1.cmp(&b.1)).then(a.2.cmp(&b.2)));
    }

    let headers = ["Solver", "Neighbor", "Params", metric_label, delta_label];
    let mut widths = headers.iter().map(|h| h.len()).collect::<Vec<usize>>();
    for row in &rows {
        let values = [
            row.0.as_str(),
            row.1.as_str(),
            row.2.as_str(),
            &format!("{:.2}", row.3),
            &format!("{:.2}", row.4),
        ];
        for (i, value) in values.iter().enumerate() {
            widths[i] = widths[i].max(value.len());
        }
    }

    let header_line = format!(
        "{:<w0$} | {:<w1$} | {:<w2$} | {:>w3$} | {:>w4$}",
        headers[0],
        headers[1],
        headers[2],
        headers[3],
        headers[4],
        w0 = widths[0],
        w1 = widths[1],
        w2 = widths[2],
        w3 = widths[3],
        w4 = widths[4],
    );
    println!("{}", header_line);
    println!("{}", "-".repeat(header_line.len()));
    for row in rows {
        println!(
            "{:<w0$} | {:<w1$} | {:<w2$} | {:>w3$} | {:>w4$}",
            row.0,
            row.1,
            row.2,
            format!("{:.2}", row.3),
            format!("{:.2}", row.4),
            w0 = widths[0],
            w1 = widths[1],
            w2 = widths[2],
            w3 = widths[3],
            w4 = widths[4],
        );
    }
}
