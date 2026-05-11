use anyhow::Result;
use plotters::prelude::*;

use crate::{model::Solution, parser::VrptwData};

const COLORS: &[RGBColor] = &[
    RGBColor(228, 26, 28),
    RGBColor(55, 126, 184),
    RGBColor(77, 175, 74),
    RGBColor(152, 78, 163),
    RGBColor(255, 127, 0),
    RGBColor(166, 86, 40),
    RGBColor(247, 129, 191),
    RGBColor(153, 153, 153),
];

pub fn visualize(instance: &VrptwData, solution: &Solution, path: &str) -> Result<()> {
    let root = BitMapBackend::new(path, (1024, 1024)).into_drawing_area();
    root.fill(&WHITE)?;

    // Compute bounding box with padding
    let all_x = instance
        .clients
        .iter()
        .map(|c| c.x)
        .chain([instance.depot.x]);
    let all_y = instance
        .clients
        .iter()
        .map(|c| c.y)
        .chain([instance.depot.y]);
    let (min_x, max_x) = all_x.fold((f64::MAX, f64::MIN), |(lo, hi), v| (lo.min(v), hi.max(v)));
    let (min_y, max_y) = all_y.fold((f64::MAX, f64::MIN), |(lo, hi), v| (lo.min(v), hi.max(v)));
    let pad_x = (max_x - min_x) * 0.05;
    let pad_y = (max_y - min_y) * 0.05;

    let mut chart = ChartBuilder::on(&root)
        .margin(20)
        .caption(
            format!(
                "{} — {} vehicles, dist {:.0}",
                instance.name,
                solution.nb_vehicles(),
                solution.total_distance(instance)
            ),
            ("sans-serif", 22),
        )
        .x_label_area_size(30)
        .y_label_area_size(40)
        .build_cartesian_2d(
            (min_x - pad_x)..(max_x + pad_x),
            (min_y - pad_y)..(max_y + pad_y),
        )?;

    chart.configure_mesh().draw()?;

    // Draw routes
    for (i, route) in solution.routes.iter().enumerate() {
        let color = COLORS[i % COLORS.len()];

        // Build node sequence: depot → clients → depot
        let nodes: Vec<(f64, f64)> = std::iter::once((instance.depot.x, instance.depot.y))
            .chain(route.clients.iter().map(|&k| {
                let c = &instance.clients[k];
                (c.x, c.y)
            }))
            .chain(std::iter::once((instance.depot.x, instance.depot.y)))
            .collect();

        chart.draw_series(LineSeries::new(nodes, color.stroke_width(2)))?;

        // Draw client dots
        chart.draw_series(route.clients.iter().map(|&k| {
            let c = &instance.clients[k];
            Circle::new((c.x, c.y), 4, color.filled())
        }))?;
    }

    // Draw depot
    chart.draw_series(std::iter::once(Circle::new(
        (instance.depot.x, instance.depot.y),
        8,
        BLACK.filled(),
    )))?;

    root.present()?;
    Ok(())
}
