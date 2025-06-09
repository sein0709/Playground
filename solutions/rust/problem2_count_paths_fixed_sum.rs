use std::io::{self, Read};
use std::collections::HashMap;

fn dfs(v: usize, p: usize, g: &Vec<Vec<usize>>, w: &Vec<i64>, k: i64, ans: &mut i64) -> HashMap<i64,i64> {
    let mut m = HashMap::new();
    m.insert(w[v], 1);
    for &to in &g[v] {
        if to == p { continue; }
        let child = dfs(to, v, g, w, k, ans);
        let (mut big, mut small) = if m.len() >= child.len() { (m, child) } else { (child, m) };
        for (s2, c2) in &small {
            let need = k - *s2;
            if let Some(&cnt) = big.get(&(need + w[v])) { *ans += cnt * *c2; }
        }
        for (s2, c2) in small {
            *big.entry(s2 + w[v]).or_insert(0) += c2;
        }
        m = big;
    }
    m
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = match it.next() { Some(x) => x.parse().unwrap(), None => return };
    let k: i64 = it.next().unwrap().parse().unwrap();
    let mut w = vec![0i64; n+1];
    for i in 1..=n { w[i] = it.next().unwrap().parse().unwrap(); }
    let mut g = vec![Vec::new(); n+1];
    for _ in 0..n-1 { let u: usize = it.next().unwrap().parse().unwrap(); let v: usize = it.next().unwrap().parse().unwrap(); g[u].push(v); g[v].push(u); }
    let mut ans = 0i64;
    dfs(1, 0, &g, &w, k, &mut ans);
    println!("{}", ans);
}
