package main

import (
    "bufio"
    "fmt"
    "os"
)

var (
    n int
    c []int64
    g [][]int
    dp0 []int64
    dp1 []int64
)

func dfs(v, p int) {
    dp1[v] = c[v]
    for _, to := range g[v] {
        if to == p {
            continue
        }
        dfs(to, v)
        dp1[v] += min(dp0[to], dp1[to])
        dp0[v] += dp1[to]
    }
}

func min(a, b int64) int64 {
    if a < b {
        return a
    }
    return b
}

func main() {
    in := bufio.NewReader(os.Stdin)
    if _, err := fmt.Fscan(in, &n); err != nil {
        return
    }
    c = make([]int64, n+1)
    for i := 1; i <= n; i++ {
        fmt.Fscan(in, &c[i])
    }
    g = make([][]int, n+1)
    for i := 0; i < n-1; i++ {
        var u, v int
        fmt.Fscan(in, &u, &v)
        g[u] = append(g[u], v)
        g[v] = append(g[v], u)
    }
    dp0 = make([]int64, n+1)
    dp1 = make([]int64, n+1)
    dfs(1, 0)
    fmt.Println(min(dp0[1], dp1[1]))
}

