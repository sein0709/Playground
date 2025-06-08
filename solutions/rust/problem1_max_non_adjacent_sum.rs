use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = match it.next() { Some(x) => x.parse().unwrap(), None => return };
    let mut w = vec![0i64; n+1];
    for i in 1..=n { w[i] = it.next().unwrap().parse().unwrap(); }
    let mut g = vec![Vec::new(); n+1];
    for _ in 0..n-1 {
        let u: usize = it.next().unwrap().parse().unwrap();
        let v: usize = it.next().unwrap().parse().unwrap();
        g[u].push(v); g[v].push(u);
    }

    let mut parent = vec![0usize; n+1];
    let mut order = vec![1usize];
    for i in 0..order.len() {
        let v = order[i];
        for &to in &g[v] { if to != parent[v] { parent[to] = v; order.push(to); } }
    }

    let mut dp0 = vec![0i64; n+1];
    let mut dp1 = vec![0i64; n+1];

    for &v in order.iter().rev() {
        let mut select = w[v];
        let mut notsel = 0i64;
        for &to in &g[v] { if to != parent[v] { select += dp0[to]; notsel += dp0[to].max(dp1[to]); } }
        dp0[v] = notsel; dp1[v] = select;
    }

    println!("{}", dp0[1].max(dp1[1]));
}
