#include <bits/stdc++.h>
using namespace std;

// Minimum Guard Placement on a tree with costs

int n;
vector<long long> c;
vector<vector<int>> g;
vector<array<long long,2>> dp;

void dfs(int v, int p){
    dp[v][1] = c[v];
    dp[v][0] = 0;
    for(int to:g[v]) if(to!=p){
        dfs(to,v);
        dp[v][1] += min(dp[to][0], dp[to][1]);
        dp[v][0] += dp[to][1];
    }
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    if(!(cin>>n)) return 0;
    c.assign(n+1,0);
    for(int i=1;i<=n;i++) cin>>c[i];
    g.assign(n+1,{});
    for(int i=0;i<n-1;i++){int u,v;cin>>u>>v;g[u].push_back(v);g[v].push_back(u);}
    dp.assign(n+1,{0,0});
    dfs(1,0);
    cout << min(dp[1][0], dp[1][1]) << "\n";
    return 0;
}

