#![allow(unused)]

use anyhow::{Context, Result, bail};
use std::path::Path;

#[derive(Debug, Clone)]
pub struct VrptwData {
    pub name: String,
    pub comment: Option<String>,
    pub max_quantity: u32,
    pub depot: Depot,
    pub clients: Vec<Client>,
}

#[derive(Debug, Clone)]
pub struct Depot {
    pub id: String,
    pub x: f64,
    pub y: f64,
    pub ready_time: i64,
    pub due_time: i64,
}

#[derive(Debug, Clone)]
pub struct Client {
    pub id: String,
    pub x: f64,
    pub y: f64,
    pub ready_time: i64,
    pub due_time: i64,
    pub demand: u32,
    pub service_time: i64,
}

pub fn load(path: impl AsRef<Path>) -> Result<VrptwData> {
    let raw = std::fs::read_to_string(path.as_ref())
        .with_context(|| format!("failed to read `{}`", path.as_ref().display()))?;

    let mut lines = raw
        .lines()
        .enumerate()
        .map(|(i, l)| (i + 1, l.trim()))
        .filter(|(_, l)| !l.is_empty());

    macro_rules! header {
        ($key:literal) => {{
            let (no, line) = lines
                .next()
                .context(concat!("expected header `", $key, "`"))?;
            let value = line
                .strip_prefix(concat!($key, ":"))
                .with_context(|| format!("line {no}: expected `{}: ...`", $key))?;
            (no, value.trim())
        }};
    }

    let name = header!("NAME").1.to_string();
    let comment = header!("COMMENT").1;
    let comment = if comment.is_empty() {
        None
    } else {
        Some(comment.to_string())
    };
    header!("TYPE");
    header!("COORDINATES");
    header!("NB_DEPOTS");
    let nb_clients = header!("NB_CLIENTS")
        .1
        .parse::<usize>()
        .context("invalid NB_CLIENTS")?;
    let max_quantity = header!("MAX_QUANTITY")
        .1
        .parse::<u32>()
        .context("invalid MAX_QUANTITY")?;

    // skip DATA_DEPOTS header line
    lines.next().context("expected DATA_DEPOTS section")?;

    let (depot_no, depot_line) = lines.next().context("expected depot record")?;
    let depot = parse_depot(depot_no, depot_line)?;

    // skip DATA_CLIENTS header line
    lines.next().context("expected DATA_CLIENTS section")?;

    let mut clients = Vec::with_capacity(nb_clients);
    for (no, line) in lines {
        clients.push(parse_client(no, line)?);
    }

    if clients.len() != nb_clients {
        bail!(
            "client count mismatch: declared {nb_clients}, found {}",
            clients.len()
        );
    }

    Ok(VrptwData {
        name,
        comment,
        max_quantity,
        depot,
        clients,
    })
}

fn parse_depot(line_no: usize, line: &str) -> Result<Depot> {
    let t: Vec<&str> = line.split_whitespace().collect();
    if t.len() != 5 {
        bail!("line {line_no}: depot expects 5 fields, got {}", t.len());
    }
    Ok(Depot {
        id: t[0].to_string(),
        x: t[1]
            .parse()
            .with_context(|| format!("line {line_no}: invalid depot.x"))?,
        y: t[2]
            .parse()
            .with_context(|| format!("line {line_no}: invalid depot.y"))?,
        ready_time: t[3]
            .parse()
            .with_context(|| format!("line {line_no}: invalid depot.ready_time"))?,
        due_time: t[4]
            .parse()
            .with_context(|| format!("line {line_no}: invalid depot.due_time"))?,
    })
}

fn parse_client(line_no: usize, line: &str) -> Result<Client> {
    let t: Vec<&str> = line.split_whitespace().collect();
    if t.len() != 7 {
        bail!("line {line_no}: client expects 7 fields, got {}", t.len());
    }
    Ok(Client {
        id: t[0].to_string(),
        x: t[1]
            .parse()
            .with_context(|| format!("line {line_no}: invalid client.x"))?,
        y: t[2]
            .parse()
            .with_context(|| format!("line {line_no}: invalid client.y"))?,
        ready_time: t[3]
            .parse()
            .with_context(|| format!("line {line_no}: invalid client.ready_time"))?,
        due_time: t[4]
            .parse()
            .with_context(|| format!("line {line_no}: invalid client.due_time"))?,
        demand: t[5]
            .parse()
            .with_context(|| format!("line {line_no}: invalid client.demand"))?,
        service_time: t[6]
            .parse()
            .with_context(|| format!("line {line_no}: invalid client.service_time"))?,
    })
}

impl VrptwData {
    pub fn without_time_windows(&self) -> Self {
        Self {
            depot: Depot {
                ready_time: 0,
                due_time: i64::MAX,
                ..self.depot.clone()
            },
            clients: self
                .clients
                .iter()
                .map(|c| Client {
                    ready_time: 0,
                    due_time: i64::MAX,
                    ..c.clone()
                })
                .collect(),
            ..self.clone()
        }
    }
}
