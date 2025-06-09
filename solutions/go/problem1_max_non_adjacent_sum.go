package main

import (
    "bufio"
    "fmt"
    "os"
)

func main() {
    in := bufio.NewReader(os.Stdin)
    var n int
    if _, err := fmt.Fscan(in, &n); err != nil {
        return
    }
    w := make([]int64, n+1)
    for i := 1; i <= n; i++ {
        fmt.Fscan(in, &w[i])
    }
    g := make([][]int, n+1)
    for i := 0; i < n-1; i++ {
        var u, v int
        fmt.Fscan(in, &u, &v)
        g[u] = append(g[u], v)
        g[v] = append(g[v], u)
    }

    dp0 := make([]int64, n+1)
    dp1 := make([]int64, n+1)

    parent := make([]int, n+1)
    order := []int{1}
    for i := 0; i < len(order); i++ {
        v := order[i]
        for _, to := range g[v] {
            if to != parent[v] {
                parent[to] = v
                order = append(order, to)
            }
        }
    }

    for i := n - 1; i >= 0; i-- {
        v := order[i]
        selectSum := w[v]
        notSel := int64(0)
        for _, to := range g[v] {
            if to != parent[v] {
                selectSum += dp0[to]
                if dp0[to] > dp1[to] {
                    notSel += dp0[to]
                } else {
                    notSel += dp1[to]
                }
            }
        }
        dp0[v] = notSel
        dp1[v] = selectSum
    }

    if dp0[1] > dp1[1] {
        fmt.Println(dp0[1])
    } else {
        fmt.Println(dp1[1])
    }
}

