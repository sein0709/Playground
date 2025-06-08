#include <bits/stdc++.h>
using namespace std;

// Count paths with sum exactly K in a tree

int n; long long K;
vector<long long> w;
vector<vector<int>> g;
long long answer = 0;

unordered_map<long long,long long> dfs(int v, int p){
    unordered_map<long long,long long> m;
    m[w[v]] = 1; // path consisting only of v
    for(int to: g[v]) if(to!=p){
        auto child = dfs(to, v);
        // ensure merging smaller into larger
        if(child.size() > m.size()) swap(child, m);
        // count cross paths using sums from child and m
        for(auto [s2,c2]: child){
            long long need = K - s2;
            auto it = m.find(need + w[v]);
            if(it != m.end()) answer += it->second * c2;
        }
        // merge child into m
        for(auto [s2,c2]: child){
            m[s2 + w[v]] += c2;
        }
    }
    return m;
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    if(!(cin >> n >> K)) return 0;
    w.assign(n+1,0);
    for(int i=1;i<=n;i++) cin >> w[i];
    g.assign(n+1,{});
    for(int i=0;i<n-1;i++){int u,v;cin>>u>>v;g[u].push_back(v);g[v].push_back(u);}    

    dfs(1,0);
    cout << answer << "\n";
    return 0;
}

