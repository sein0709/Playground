use std::io::{self, Read};

fn dfs(v: usize, p: usize, g: &Vec<Vec<usize>>, c: &Vec<i64>, dp: &mut Vec<[i64;2]>) {
    dp[v][1] = c[v];
    dp[v][0] = 0;
    for &to in &g[v] {
        if to == p { continue; }
        dfs(to, v, g, c, dp);
        dp[v][1] += dp[to][0].min(dp[to][1]);
        dp[v][0] += dp[to][1];
    }
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = match it.next() { Some(x) => x.parse().unwrap(), None => return };
    let mut c = vec![0i64; n+1];
    for i in 1..=n { c[i] = it.next().unwrap().parse().unwrap(); }
    let mut g = vec![Vec::new(); n+1];
    for _ in 0..n-1 { let u: usize = it.next().unwrap().parse().unwrap(); let v: usize = it.next().unwrap().parse().unwrap(); g[u].push(v); g[v].push(u); }
    let mut dp = vec![[0i64;2]; n+1];
    dfs(1, 0, &g, &c, &mut dp);
    println!("{}", dp[1][0].min(dp[1][1]));
}
