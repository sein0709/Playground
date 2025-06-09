package main

import (
    "bufio"
    "fmt"
    "os"
)

var (
    n int
    K int64
    w []int64
    g [][]int
    answer int64
)

func dfs(v, p int) map[int64]int64 {
    m := map[int64]int64{w[v]: 1}
    for _, to := range g[v] {
        if to == p {
            continue
        }
        child := dfs(to, v)
        if len(child) > len(m) {
            child, m = m, child
        }
        for s2, c2 := range child {
            need := K - s2
            if cnt, ok := m[need+w[v]]; ok {
                answer += cnt * c2
            }
        }
        for s2, c2 := range child {
            m[s2+w[v]] += c2
        }
    }
    return m
}

func main() {
    in := bufio.NewReader(os.Stdin)
    if _, err := fmt.Fscan(in, &n, &K); err != nil {
        return
    }
    w = make([]int64, n+1)
    for i := 1; i <= n; i++ {
        fmt.Fscan(in, &w[i])
    }
    g = make([][]int, n+1)
    for i := 0; i < n-1; i++ {
        var u, v int
        fmt.Fscan(in, &u, &v)
        g[u] = append(g[u], v)
        g[v] = append(g[v], u)
    }
    dfs(1, 0)
    fmt.Println(answer)
}

