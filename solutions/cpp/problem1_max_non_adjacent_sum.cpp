#include <bits/stdc++.h>
using namespace std;

// Maximum Non-Adjacent Node Sum in a Tree

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n; if(!(cin >> n)) return 0;
    vector<long long> w(n+1);
    for (int i=1;i<=n;i++) cin >> w[i];
    vector<vector<int>> g(n+1);
    for(int i=0;i<n-1;i++){
        int u,v; cin>>u>>v; g[u].push_back(v); g[v].push_back(u);
    }
    vector<array<long long,2>> dp(n+1, {0,0});
    vector<int> parent(n+1,0);
    vector<int> order; order.reserve(n);
    order.push_back(1); parent[1]=0;
    for(size_t i=0;i<order.size();++i){
        int v=order[i];
        for(int to:g[v]) if(to!=parent[v]){
            parent[to]=v; order.push_back(to);
        }
    }
    for(int i=n-1;i>=0;--i){
        int v=order[i];
        long long select = w[v];
        long long notsel = 0;
        for(int to:g[v]) if(to!=parent[v]){
            select += dp[to][0];
            notsel += max(dp[to][0], dp[to][1]);
        }
        dp[v][0]=notsel; dp[v][1]=select;
    }
    cout << max(dp[1][0], dp[1][1]) << "\n";
    return 0;
}

