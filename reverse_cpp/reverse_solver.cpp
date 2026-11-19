// Zgjidhja e kundert per Programmable Cubes (ESA SpOC 3).
// Kompilim: g++ -O2 -o reverse_solver reverse_solver.cpp
// Perdoret nga run_cpp.py per JWST dhe Enterprise.
#include <bits/stdc++.h>
// generated
static const int SURR0[24][3]={{-2,2,0},{-1,2,0},{0,2,0},{1,2,0},{2,2,0},{-2,1,0},{-1,1,0},{0,1,0},{1,1,0},{2,1,0},{-2,0,0},{-1,0,0},{1,0,0},{2,0,0},{-2,-1,0},{-1,-1,0},{0,-1,0},{1,-1,0},{2,-1,0},{-2,-2,0},{-1,-2,0},{0,-2,0},{1,-2,0},{2,-2,0}};
static const int SURR1[24][3]={{0,-2,2},{0,-1,2},{0,0,2},{0,1,2},{0,2,2},{0,-2,1},{0,-1,1},{0,0,1},{0,1,1},{0,2,1},{0,-2,0},{0,-1,0},{0,1,0},{0,2,0},{0,-2,-1},{0,-1,-1},{0,0,-1},{0,1,-1},{0,2,-1},{0,-2,-2},{0,-1,-2},{0,0,-2},{0,1,-2},{0,2,-2}};
static const int SURR2[24][3]={{-2,0,2},{-1,0,2},{0,0,2},{1,0,2},{2,0,2},{-2,0,1},{-1,0,1},{0,0,1},{1,0,1},{2,0,1},{-2,0,0},{-1,0,0},{1,0,0},{2,0,0},{-2,0,-1},{-1,0,-1},{0,0,-1},{1,0,-1},{2,0,-1},{-2,0,-2},{-1,0,-2},{0,0,-2},{1,0,-2},{2,0,-2}};
static const int NPAT=16;
static const int PATOCC[16][6]={{7,8,-1,-1,-1,-1},{6,11,-1,-1,-1,-1},{15,16,-1,-1,-1,-1},{12,17,-1,-1,-1,-1},{6,7,-1,-1,-1,-1},{11,15,-1,-1,-1,-1},{16,17,-1,-1,-1,-1},{8,12,-1,-1,-1,-1},{16,-1,-1,-1,-1,-1},{7,-1,-1,-1,-1,-1},{11,-1,-1,-1,-1,-1},{12,-1,-1,-1,-1,-1},{12,-1,-1,-1,-1,-1},{11,-1,-1,-1,-1,-1},{16,-1,-1,-1,-1,-1},{7,-1,-1,-1,-1,-1}};
static const int PATEMP[16][6]={{12,16,17,-1,-1,-1},{7,8,12,-1,-1,-1},{6,7,11,-1,-1,-1},{11,15,16,-1,-1,-1},{11,15,16,-1,-1,-1},{12,16,17,-1,-1,-1},{7,8,12,-1,-1,-1},{6,7,11,-1,-1,-1},{14,15,10,11,6,7},{8,9,12,13,16,17},{12,6,7,8,1,2},{11,15,16,17,21,22},{11,6,7,8,2,3},{12,15,16,17,20,21},{17,18,12,13,7,8},{5,6,10,11,15,16}};
static const int PATDIR[2][8]={{0,1,2,3,8,9,10,11},{4,5,6,7,12,13,14,15}};
static const int DISP[48][3]={{1,0,0},{0,1,0},{-1,0,0},{0,-1,0},{-1,0,0},{0,-1,0},{1,0,0},{0,1,0},{-1,-1,0},{1,1,0},{-1,1,0},{1,-1,0},{1,1,0},{-1,-1,0},{1,-1,0},{-1,1,0},{0,1,0},{0,0,1},{0,-1,0},{0,0,-1},{0,-1,0},{0,0,-1},{0,1,0},{0,0,1},{0,-1,-1},{0,1,1},{0,-1,1},{0,1,-1},{0,1,1},{0,-1,-1},{0,1,-1},{0,-1,1},{1,0,0},{0,0,1},{-1,0,0},{0,0,-1},{-1,0,0},{0,0,-1},{1,0,0},{0,0,1},{-1,0,-1},{1,0,1},{-1,0,1},{1,0,-1},{1,0,1},{-1,0,-1},{1,0,-1},{-1,0,1}};



using namespace std;
typedef array<int,3> P3;
static const int D6[6][3]={{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};

struct Problem{
  int N,T,maxc; double F0;
  vector<P3> init,target; vector<int> itype,ttype;
  void load(const string&fn){
    ifstream f(fn); f>>N>>T>>maxc>>F0; init.resize(N);target.resize(N);itype.resize(N);ttype.resize(N);
    for(int i=0;i<N;i++) f>>init[i][0]>>init[i][1]>>init[i][2]>>itype[i];
    for(int i=0;i<N;i++) f>>target[i][0]>>target[i][1]>>target[i][2]>>ttype[i];
  }
};

struct Sim{
  int N; vector<P3> pos; 
  int lo[3],hi[3],dim[3]; vector<int16_t> g; vector<int> stamp; int cur=0;
  vector<int> stk;
  void init(const Problem&pb,int margin=14){
    N=pb.N; pos=pb.init;
    for(int a=0;a<3;a++){lo[a]=1e9;hi[a]=-1e9;}
    for(auto&v:pb.init)for(int a=0;a<3;a++){lo[a]=min(lo[a],v[a]);hi[a]=max(hi[a],v[a]);}
    for(auto&v:pb.target)for(int a=0;a<3;a++){lo[a]=min(lo[a],v[a]);hi[a]=max(hi[a],v[a]);}
    for(int a=0;a<3;a++){lo[a]-=margin;hi[a]+=margin;dim[a]=hi[a]-lo[a]+1;}
    g.assign((size_t)dim[0]*dim[1]*dim[2],-1); stamp.assign(g.size(),0);
    for(int i=0;i<N;i++) g[idx(pos[i])]=i;
  }
  inline bool inb(int x,int y,int z)const{return x>=lo[0]&&x<=hi[0]&&y>=lo[1]&&y<=hi[1]&&z>=lo[2]&&z<=hi[2];}
  inline size_t idx(const P3&p)const{return ((size_t)(p[0]-lo[0])*dim[1]+(p[1]-lo[1]))*dim[2]+(p[2]-lo[2]);}
  inline int at(int x,int y,int z)const{ if(!inb(x,y,z))return -1; return g[((size_t)(x-lo[0])*dim[1]+(y-lo[1]))*dim[2]+(z-lo[2])];}
  inline bool occ(int x,int y,int z)const{return at(x,y,z)>=0;}
  // does removing cube c keep ensemble connected
  bool connected_without(int c){
    const P3&p=pos[c]; int nb[6][3]; int nn=0;
    for(int d=0;d<6;d++){int x=p[0]+D6[d][0],y=p[1]+D6[d][1],z=p[2]+D6[d][2]; if(occ(x,y,z)){nb[nn][0]=x;nb[nn][1]=y;nb[nn][2]=z;nn++;}}
    if(nn<=1) return true;
    ++cur; stk.clear();
    size_t ci=idx(p); stamp[ci]=cur;
    // mark targets
    // BFS from nb[0]
    auto push=[&](int x,int y,int z){ if(!inb(x,y,z))return; size_t i=((size_t)(x-lo[0])*dim[1]+(y-lo[1]))*dim[2]+(z-lo[2]); if(g[i]<0||stamp[i]==cur)return; stamp[i]=cur; stk.push_back(x);stk.push_back(y);stk.push_back(z);};
    // need to count found neighbours: neighbour cells set
    int found=0;
    // mark neighbour cells with special flag via separate small check
    auto isnb=[&](int x,int y,int z){return abs(x-p[0])+abs(y-p[1])+abs(z-p[2])==1;};
    push(nb[0][0],nb[0][1],nb[0][2]); found=1;
    while(!stk.empty()){
      int z=stk.back();stk.pop_back();int y=stk.back();stk.pop_back();int x=stk.back();stk.pop_back();
      for(int d=0;d<6;d++){
        int a=x+D6[d][0],b=y+D6[d][1],cc=z+D6[d][2];
        if(!inb(a,b,cc))continue;
        size_t i=((size_t)(a-lo[0])*dim[1]+(b-lo[1]))*dim[2]+(cc-lo[2]);
        if(g[i]<0||stamp[i]==cur)continue;
        stamp[i]=cur; stk.push_back(a);stk.push_back(b);stk.push_back(cc);
        if(isnb(a,b,cc)){ if(++found==nn) return true; }
      }
    }
    return false;
  }
  // returns pattern index or -1, no apply
  int find_pattern(int c,int m)const{
    int ax=m>>1,dir=m&1; const P3&p=pos[c];
    const int (*S)[3]= ax==0?SURR0:(ax==1?SURR1:SURR2);
    for(int t=0;t<8;t++){
      int pi=PATDIR[dir][t]; bool ok=true;
      for(int k=0;k<6&&ok;k++){int s=PATOCC[pi][k]; if(s<0)break; if(!occ(p[0]+S[s][0],p[1]+S[s][1],p[2]+S[s][2]))ok=false;}
      if(!ok)continue;
      for(int k=0;k<6&&ok;k++){int s=PATEMP[pi][k]; if(s<0)break; if(occ(p[0]+S[s][0],p[1]+S[s][1],p[2]+S[s][2]))ok=false;}
      if(ok) return pi;
    }
    return -1;
  }
  bool move(int c,int m){
    if(!connected_without(c))return false;
    int pi=find_pattern(c,m); if(pi<0)return false;
    const int*d=DISP[(m>>1)*16+pi]; P3 q={pos[c][0]+d[0],pos[c][1]+d[1],pos[c][2]+d[2]};
    if(!inb(q[0],q[1],q[2]))return false;
    g[idx(pos[c])]=-1; pos[c]=q; g[idx(q)]=c; return true;
  }
  // legal without applying (for mobility)
  bool legal(int c,int m){
    if(find_pattern(c,m)<0)return false;
    return connected_without(c);
  }
};

Problem pb; Sim S;
vector<pair<int,int>> cmds; vector<char> correct; vector<set<P3>> freeT; map<P3,int> tt_at;
int N;
int l1(const P3&a,const P3&b){return abs(a[0]-b[0])+abs(a[1]-b[1])+abs(a[2]-b[2]);}
double score(int C,int L){double F=0.9*C/pb.N+0.1*(1-(double)L/pb.maxc);return -(F-pb.F0)/(1-pb.F0);}
void setpos(int c,const P3&p){S.g[S.idx(S.pos[c])]=-1;S.pos[c]=p;S.g[S.idx(p)]=c;}
vector<int> par_mv; vector<int> vis; int vcur=0; vector<size_t> par_cell;
// BFS single cube to nearest free target; returns path or empty (found flag)
set<P3> allowedS; bool useAllowed=false;
bool bfs_path(int c,int maxd,int maxstates,vector<int>&path,P3&goal){
  ++vcur; P3 st=S.pos[c]; int t=pb.itype[c];
  if(par_mv.size()!=S.g.size()){par_mv.assign(S.g.size(),0);vis.assign(S.g.size(),0);par_cell.assign(S.g.size(),0);}
  deque<pair<size_t,int>> dq; size_t si=S.idx(st); vis[si]=vcur; dq.push_back({si,0}); par_mv[si]=-1;
  int cnt=0; vector<P3> cellpos; 
  // need to recover P3 from cell index
  auto unidx=[&](size_t i){P3 p;p[2]=i%S.dim[2]+S.lo[2];i/=S.dim[2];p[1]=i%S.dim[1]+S.lo[1];i/=S.dim[1];p[0]=i+S.lo[0];return p;};
  bool found=false; size_t gi=0;
  while(!dq.empty()){
    auto [ci,d]=dq.front();dq.pop_front(); P3 p=unidx(ci);
    if(ci!=si && freeT[t].count(p) && (!useAllowed||allowedS.count(p))){found=true;gi=ci;break;}
    if(d>=maxd||++cnt>maxstates)continue;
    setpos(c,p);
    for(int m=0;m<6;m++){
      if(!S.move(c,m))continue; P3 q=S.pos[c]; setpos(c,p); // restore
      size_t qi=S.idx(q); if(vis[qi]==vcur)continue; vis[qi]=vcur; par_mv[qi]=m; par_cell[qi]=ci; dq.push_back({qi,d+1});
    }
  }
  setpos(c,st);
  if(!found)return false;
  path.clear(); size_t cur=gi; goal=unidx(gi);
  while(cur!=si){path.push_back(par_mv[cur]);cur=par_cell[cur];}
  reverse(path.begin(),path.end()); return true;
}
int ncorrect(){int k=0;for(char x:correct)k+=x;return k;}

// apply path for cube c (moves), record commands; returns nothing
void applyPath(int c,const vector<int>&path){ for(int m:path){ if(!S.move(c,m)){fprintf(stderr,"applyPath fail\n");exit(1);} cmds.push_back({c,m}); } }
void undoPath(int c,const vector<int>&path){ for(int i=(int)path.size()-1;i>=0;i--){ if(!S.move(c,path[i]^1)){fprintf(stderr,"undoPath fail\n");exit(1);} cmds.pop_back(); } }
bool unstick_round(int maxd,int maxst,vector<pair<int,int>>&hist,int radius){
  bool improved=false;
  for(int w=0;w<N;w++){
    if(correct[w]||freeT[pb.itype[w]].empty())continue;
    vector<int> pw;P3 gw;
    useAllowed=false;
    if(bfs_path(w,maxd,maxst,pw,gw)){ applyPath(w,pw); freeT[pb.itype[w]].erase(S.pos[w]);correct[w]=1;hist.push_back({(int)cmds.size(),ncorrect()});improved=true;continue; }
    P3 pp=S.pos[w];
    vector<int> cand; for(int n=0;n<N;n++){ if(n==w)continue; auto&q=S.pos[n]; if(abs(q[0]-pp[0])<=radius&&abs(q[1]-pp[1])<=radius&&abs(q[2]-pp[2])<=radius&&correct[n])cand.push_back(n);} 
    for(int n:cand){
      vector<int> pn;P3 gn; P3 old=S.pos[n]; int tn=pb.itype[n];
      if(!bfs_path(n,maxd,maxst,pn,gn))continue;
      applyPath(n,pn);
      vector<int> pw2;P3 gw2;
      // old cell of n becomes free target (n will be placed at gn)
      freeT[tn].insert(old); freeT[tn].erase(gn);
      bool ok=bfs_path(w,maxd,maxst,pw2,gw2);
      if(ok){ applyPath(w,pw2); freeT[pb.itype[w]].erase(S.pos[w]); correct[w]=1; hist.push_back({(int)cmds.size(),ncorrect()}); improved=true; break; }
      freeT[tn].erase(old); freeT[tn].insert(gn);
      undoPath(n,pn);
    }
  }
  return improved;
}

map<P3,double> connRank(double noise,mt19937&rng,map<P3,int>&tcount_unused){
  // components of correct cubes
  map<P3,int> comp; int nc=0;
  vector<P3> cp; for(int c=0;c<N;c++) if(correct[c]) cp.push_back(S.pos[c]);
  set<P3> cs(cp.begin(),cp.end());
  for(auto&p:cp){ if(comp.count(p))continue; deque<P3> dq; dq.push_back(p); comp[p]=nc; while(!dq.empty()){P3 a=dq.front();dq.pop_front(); for(int d=0;d<6;d++){P3 b={a[0]+D6[d][0],a[1]+D6[d][1],a[2]+D6[d][2]}; if(cs.count(b)&&!comp.count(b)){comp[b]=nc;dq.push_back(b);}}} nc++; }
  map<P3,double> key; uniform_real_distribution<double> U(0,1);
  for(int t=0;t<pb.T;t++)for(auto&q:freeT[t]){ set<int> cc; int nbc=0; for(int d=0;d<6;d++){P3 b={q[0]+D6[d][0],q[1]+D6[d][1],q[2]+D6[d][2]}; auto it=comp.find(b); if(it!=comp.end()){cc.insert(it->second);nbc++;}}
    key[q]=-(double)cc.size()*10-nbc*0.5+noise*U(rng); }
  return key;
}
set<int> evictedS; set<int> prioS;

template<class OCC>
bool reach_occ(int w,const P3&start,OCC occ,int maxst){
  int t=pb.itype[w]; vector<P3> q; set<P3> seen; q.push_back(start); seen.insert(start); size_t h=0;
  while(h<q.size()&&(int)h<maxst){ P3 p=q[h++]; if(p!=start&&freeT[t].count(p))return true;
    for(int m=0;m<6;m++){ int ax=m>>1,dir=m&1; const int (*SS)[3]=ax==0?SURR0:(ax==1?SURR1:SURR2); int pi=-1;
      for(int tt=0;tt<8&&pi<0;tt++){int pj=PATDIR[dir][tt]; bool ok=true;
        for(int k=0;k<6&&ok;k++){int sx=PATOCC[pj][k]; if(sx<0)break; if(!occ(p[0]+SS[sx][0],p[1]+SS[sx][1],p[2]+SS[sx][2]))ok=false;}
        for(int k=0;k<6&&ok;k++){int sx=PATEMP[pj][k]; if(sx<0)break; if(occ(p[0]+SS[sx][0],p[1]+SS[sx][1],p[2]+SS[sx][2]))ok=false;}
        if(ok)pi=pj;}
      if(pi<0)continue; const int*d=DISP[ax*16+pi]; P3 r={p[0]+d[0],p[1]+d[1],p[2]+d[2]}; if(!S.inb(r[0],r[1],r[2]))continue; if(seen.insert(r).second)q.push_back(r);} }
  return false;
}
// BFS: cube c to first reachable cell with L1 distance >= minDist from ref
bool bfs_park(int c,const P3&ref,int minDist,int maxd,int maxst,vector<int>&path){
  ++vcur; P3 st=S.pos[c];
  if(par_mv.size()!=S.g.size()){par_mv.assign(S.g.size(),0);vis.assign(S.g.size(),0);par_cell.assign(S.g.size(),0);}
  deque<pair<size_t,int>> dq; size_t si=S.idx(st); vis[si]=vcur; dq.push_back({si,0}); par_mv[si]=-1; int cnt=0;
  auto unidx=[&](size_t i){P3 p;p[2]=i%S.dim[2]+S.lo[2];i/=S.dim[2];p[1]=i%S.dim[1]+S.lo[1];i/=S.dim[1];p[0]=i+S.lo[0];return p;};
  bool found=false; size_t gi=0;
  while(!dq.empty()){ auto [ci,d]=dq.front();dq.pop_front(); P3 p=unidx(ci);
    if(ci!=si&&l1(p,ref)>=minDist){found=true;gi=ci;break;}
    if(d>=maxd||++cnt>maxst)continue; setpos(c,p);
    for(int m=0;m<6;m++){ if(!S.move(c,m))continue; P3 q=S.pos[c]; setpos(c,p); size_t qi=S.idx(q); if(vis[qi]==vcur)continue; vis[qi]=vcur; par_mv[qi]=m; par_cell[qi]=ci; dq.push_back({qi,d+1}); } }
  setpos(c,st); if(!found)return false;
  path.clear(); size_t cur=gi; while(cur!=si){path.push_back(par_mv[cur]);cur=par_cell[cur];} reverse(path.begin(),path.end()); return true;
}
struct Applied{int c; vector<int> path;};
bool dig(int w,int maxSub,int rad,int parkDist,int maxd,int maxst,vector<pair<int,int>>&hist){
  P3 pw0=S.pos[w]; int tw=pb.itype[w];
  auto tryRem=[&](const set<int>&rem)->bool{
        // execute
        vector<char> corr0=correct; vector<set<P3>> free0=freeT; size_t cmd0=cmds.size(); vector<Applied> applied; map<int,P3> oldpos;
        auto rollback=[&](){ for(int i=(int)applied.size()-1;i>=0;i--){ for(int j=(int)applied[i].path.size()-1;j>=0;j--){ if(!S.move(applied[i].c,applied[i].path[j]^1)){fprintf(stderr,"rollback fail\n");exit(1);} cmds.pop_back(); } } correct=corr0; freeT=free0; };
        vector<int> remaining(rem.begin(),rem.end()); bool moved=true;
        for(int r:remaining) oldpos[r]=S.pos[r];
        while(!remaining.empty()&&moved){ moved=false;
          for(size_t i=0;i<remaining.size();i++){ int r=remaining[i]; vector<int> pp; if(bfs_park(r,pw0,parkDist,maxd,maxst,pp)){ for(int m:pp){S.move(r,m);cmds.push_back({r,m});} applied.push_back({r,pp}); remaining.erase(remaining.begin()+i); moved=true; break; } } }
        if(!remaining.empty()){ rollback(); return false; }
        // cubes that were correct: their old cell becomes free target
        for(int r:rem) if(correct[r]){ correct[r]=0; freeT[pb.itype[r]].insert(oldpos[r]); }
        vector<int> pth;P3 gg; useAllowed=false;
        if(!bfs_path(w,maxd,maxst,pth,gg)){ rollback(); return false; }
        for(int m:pth){S.move(w,m);cmds.push_back({w,m});} applied.push_back({w,pth}); freeT[tw].erase(S.pos[w]); correct[w]=1;
        // return parked cubes
        for(int r:rem){ if(correct[r])continue; vector<int> pr;P3 g2; useAllowed=false; if(!bfs_path(r,maxd,maxst,pr,g2)){ rollback(); return false; }
          for(int m:pr){S.move(r,m);cmds.push_back({r,m});} applied.push_back({r,pr}); freeT[pb.itype[r]].erase(S.pos[r]); correct[r]=1; }
        hist.push_back({(int)cmds.size(),ncorrect()});
        return true;
  };
  if(getenv("DIGBIG")){ int RB=atoi(getenv("DIGBIG")); int RB2=getenv("DIGBIG2")?atoi(getenv("DIGBIG2")):RB; vector<int> cb;
    for(int n=0;n<N;n++){ if(n==w)continue; int dd=l1(S.pos[n],pw0); bool in=dd<=RB; for(auto&f:freeT[tw]) if(l1(S.pos[n],f)<=RB2) in=true; if(in)cb.push_back(n);} 
    set<int> rem(cb.begin(),cb.end());
    auto reachWith=[&](const set<int>&r){ auto occ=[&](int x,int y,int z){int a=S.at(x,y,z);return a>=0&&a!=w&&!r.count(a);}; return reach_occ(w,pw0,occ,100000); };
    fprintf(stderr,"big w=%d ball=%zu reach=%d\n",w,rem.size(),(int)reachWith(rem));
    if(reachWith(rem)){
      sort(cb.begin(),cb.end(),[&](int a,int b){return l1(S.pos[a],pw0)>l1(S.pos[b],pw0);});
      for(int n:cb){ set<int> r2=rem; r2.erase(n); if(reachWith(r2)) rem=r2; }
      fprintf(stderr,"  min rem=%zu\n",rem.size());
      if((int)rem.size()<=atoi(getenv("DIGBIGMAX")?getenv("DIGBIGMAX"):"12") && tryRem(rem)) return true;
    }
  }
  vector<int> cand; int rad2=getenv("DIGRAD2")?atoi(getenv("DIGRAD2")):2;
  auto dist=[&](int n){ int d=l1(S.pos[n],pw0); if(d>rad) d=1000; for(auto&f:freeT[tw]){ int e=l1(S.pos[n],f); if(e<=rad2) d=min(d,e);} return d; };
  for(int n=0;n<N;n++){ if(n==w)continue; if(dist(n)<1000)cand.push_back(n);} 
  sort(cand.begin(),cand.end(),[&](int a,int b){return dist(a)<dist(b);});
  if((int)cand.size()>(getenv("DIGM")?atoi(getenv("DIGM")):40))cand.resize(getenv("DIGM")?atoi(getenv("DIGM")):40);
  int M=cand.size();
  for(int sz=1;sz<=maxSub;sz++){
    vector<int> idx(sz); function<bool(int,int)> rec=[&](int start,int depth)->bool{
      if(depth==sz){
        set<int> rem; for(int i:idx)rem.insert(cand[i]);
        auto occ=[&](int x,int y,int z){int a=S.at(x,y,z);return a>=0&&a!=w&&!rem.count(a);};
        if(!reach_occ(w,pw0,occ,getenv("REACHMS")?atoi(getenv("REACHMS")):100000))return false;
        return tryRem(rem);
      }
      for(int i=start;i<M;i++){ idx[depth]=i; if(rec(i+1,depth+1))return true; }
      return false; };
    if(rec(0,0))return true;
  }
  return false;
}
bool relay(int w,int maxd,int maxst,vector<pair<int,int>>&hist){
  int t=pb.itype[w]; int RM=getenv("RELM")?atoi(getenv("RELM")):40; int RQ=getenv("RELQ")?atoi(getenv("RELQ")):6;
  vector<P3> qs(freeT[t].begin(),freeT[t].end()); sort(qs.begin(),qs.end(),[&](const P3&a,const P3&b){return l1(a,S.pos[w])<l1(b,S.pos[w]);}); if((int)qs.size()>RQ)qs.resize(RQ);
  for(auto q:qs){
    vector<int> xs; for(int x=0;x<N;x++) if(x!=w&&correct[x]&&pb.itype[x]==t) xs.push_back(x);
    sort(xs.begin(),xs.end(),[&](int a,int b){return l1(S.pos[a],q)<l1(S.pos[b],q);}); if((int)xs.size()>RM)xs.resize(RM);
    for(int x:xs){
      set<P3> sv=freeT[t]; freeT[t]={q}; bool ua=useAllowed; useAllowed=false; vector<int> px; P3 g; bool ok=bfs_path(x,maxd,maxst,px,g); freeT[t]=sv; if(!ok){useAllowed=ua;continue;}
      P3 xo=S.pos[x]; size_t c0=cmds.size(); for(int m:px){S.move(x,m);cmds.push_back({x,m});}
      freeT[t].erase(q); freeT[t].insert(xo);
      vector<int> pw; P3 g2; if(bfs_path(w,maxd,maxst,pw,g2)){ for(int m:pw){S.move(w,m);cmds.push_back({w,m});} freeT[t].erase(S.pos[w]); correct[w]=1; useAllowed=ua; hist.push_back({(int)cmds.size(),ncorrect()}); fprintf(stderr,"relay %d via %d -> correct %d\n",w,x,ncorrect()); return true; }
      for(int j=(int)px.size()-1;j>=0;j--){ if(!S.move(x,px[j]^1)){fprintf(stderr,"relay rollback fail\n");exit(1);} cmds.pop_back(); }
      freeT[t].erase(xo); freeT[t].insert(q); useAllowed=ua; (void)c0;
    }
  }
  return false;
}
bool relay_round(int maxd,int maxst,vector<pair<int,int>>&hist){ bool imp=false; for(int w=0;w<N;w++){ if(correct[w]||freeT[pb.itype[w]].empty())continue; if(relay(w,maxd,maxst,hist)){imp=true; string cn=string(getenv("CKPT")?getenv("CKPT"):"ck.ckpt"); FILE*fc=fopen(cn.c_str(),"w"); for(auto&c:cmds)fprintf(fc,"%d %d\n",c.first,c.second); fclose(fc);} } return imp; }
bool dig_round(int maxSub,int rad,int parkDist,int maxd,int maxst,vector<pair<int,int>>&hist){
  bool imp=false;
  for(int w=0;w<N;w++){ if(correct[w]||freeT[pb.itype[w]].empty())continue; if(dig(w,maxSub,rad,parkDist,maxd,maxst,hist)){imp=true; fprintf(stderr,"dug %d -> correct %d\n",w,ncorrect()); if(getenv("STOPAT")&&ncorrect()>=atoi(getenv("STOPAT"))){ FILE*fo=fopen(getenv("STOPOUT"),"w"); for(auto&c:cmds)fprintf(fo,"%d %d\n",c.first,c.second); fclose(fo); fprintf(stderr,"STOPAT reached\n"); exit(0);}  {string cn=string(getenv("CKPT")?getenv("CKPT"):"ck.ckpt"); FILE*fc=fopen(cn.c_str(),"w"); for(auto&c:cmds)fprintf(fc,"%d %d\n",c.first,c.second); fclose(fc);}} }
  return imp;
}
bool moveTo(int s,const P3&c,int maxd,int maxst,vector<int>&path){ int t=pb.itype[s]; set<P3> sv=freeT[t]; freeT[t]={c}; bool ua=useAllowed; useAllowed=false; P3 g; bool ok=bfs_path(s,maxd,maxst,path,g); freeT[t]=sv; useAllowed=ua; return ok; }
int gBefore=0; P3 gWo;
int compsOf(int w,map<P3,int>&comp,vector<int>&csz){ comp.clear(); csz.clear(); int nc=0;
  for(int d=0;d<6;d++){ P3 b={S.pos[w][0]+D6[d][0],S.pos[w][1]+D6[d][1],S.pos[w][2]+D6[d][2]}; if(S.at(b[0],b[1],b[2])<0||comp.count(b))continue; int sz=0; deque<P3> dq; dq.push_back(b); comp[b]=nc;
    while(!dq.empty()){P3 a=dq.front();dq.pop_front();sz++; for(int e=0;e<6;e++){P3 x={a[0]+D6[e][0],a[1]+D6[e][1],a[2]+D6[e][2]}; if(x==S.pos[w]||comp.count(x)||S.at(x[0],x[1],x[2])<0)continue; comp[x]=nc; dq.push_back(x);} }
    csz.push_back(sz); nc++; }
  return nc; }
bool bridgeRec(int w,int depth,vector<int>&sup,int maxd,int maxst){
  map<P3,int> comp; vector<int> csz; int nc=compsOf(w,comp,csz);
  if(nc<2){ if(depth==0) return false;
    vector<int> pw; P3 g; bool wok=false; int BMS=getenv("BRMAXST")?atoi(getenv("BRMAXST")):200000;
    if(bfs_path(w,200,BMS,pw,g)){ for(int m:pw){S.move(w,m);cmds.push_back({w,m});} freeT[pb.itype[w]].erase(S.pos[w]); correct[w]=1; wok=true; }
    else { int lm=0; for(int m=0;m<6;m++){ if(S.move(w,m)){lm++;S.move(w,m^1);} } if(lm>0 && getenv("BRDIG")){ vector<pair<int,int>> h2; if(dig(w,atoi(getenv("BRDIG")),3,5,40,20000,h2)) wok=true; } }
    if(!wok) return false;
    { auto itw=tt_at.find(gWo); if(itw!=tt_at.end() && S.at(gWo[0],gWo[1],gWo[2])<0){ int tw2=itw->second; vector<int> xs; for(int x=0;x<N;x++) if(!correct[x]&&x!=w&&pb.itype[x]==tw2&&find(sup.begin(),sup.end(),x)==sup.end()) xs.push_back(x);
        sort(xs.begin(),xs.end(),[&](int a,int b){return l1(S.pos[a],gWo)<l1(S.pos[b],gWo);});
        for(int x:xs){ vector<int> px; if(moveTo(x,gWo,200,400000,px)){ for(int m:px){S.move(x,m);cmds.push_back({x,m});} freeT[tw2].erase(gWo); correct[x]=1; if(getenv("BRDBG"))fprintf(stderr,"  filled old cell with %d\n",x); break; } } } }
    for(int k=(int)sup.size()-1;k>=0;k--){ int s=sup[k]; if(correct[s])continue; if(freeT[pb.itype[s]].count(S.pos[s])){ freeT[pb.itype[s]].erase(S.pos[s]); correct[s]=1; continue; } vector<int> pr; P3 g2; if(!bfs_path(s,maxd,maxst,pr,g2)) continue; for(int m:pr){S.move(s,m);cmds.push_back({s,m});} freeT[pb.itype[s]].erase(S.pos[s]); correct[s]=1; }
    int drop=getenv("BRDROP")?atoi(getenv("BRDROP")):0; return ncorrect()>=gBefore+1-drop; }
  int MAXB=getenv("BRMAX")?atoi(getenv("BRMAX")):3; if(depth>=MAXB) return false;
  int big=max_element(csz.begin(),csz.end())-csz.begin(); int sm=-1; for(int k=0;k<nc;k++) if(k!=big&&(sm<0||csz[k]<csz[sm]))sm=k;
  vector<P3> cells; set<P3> seenc;
  for(auto&kv:comp){ if(kv.second!=sm)continue; for(int e=0;e<6;e++){ P3 c={kv.first[0]+D6[e][0],kv.first[1]+D6[e][1],kv.first[2]+D6[e][2]}; if(S.at(c[0],c[1],c[2])>=0||c==S.pos[w]||seenc.count(c))continue; seenc.insert(c);
      bool tb=false; for(int f=0;f<6;f++){P3 y={c[0]+D6[f][0],c[1]+D6[f][1],c[2]+D6[f][2]}; auto it=comp.find(y); if(it!=comp.end()&&it->second!=sm)tb=true;} if(tb)cells.push_back(c);} }
  int BS=getenv("BRS")?atoi(getenv("BRS")):30; int K=getenv("BRK")?atoi(getenv("BRK")):3; int succ=0;
  for(auto&c:cells){
    vector<int> ss; for(int s=0;s<N;s++){ if(s==w)continue; if(find(sup.begin(),sup.end(),s)!=sup.end())continue; auto it=comp.find(S.pos[s]); if(it!=comp.end()&&it->second!=big)continue; ss.push_back(s);} 
    bool ctg=false; {auto it2=tt_at.find(c); ctg=(it2!=tt_at.end());} sort(ss.begin(),ss.end(),[&](int a,int b){ auto it2=tt_at.find(c); int ma=(it2!=tt_at.end()&&it2->second==pb.itype[a])?-1000:0; int mb=(it2!=tt_at.end()&&it2->second==pb.itype[b])?-1000:0; int ka=ma+l1(S.pos[a],c)+(correct[a]?0:-1); int kb=mb+l1(S.pos[b],c)+(correct[b]?0:-1); return ka<kb;}); (void)ctg; if((int)ss.size()>BS)ss.resize(BS);
    for(int s:ss){
      vector<char> corr0=correct; vector<set<P3>> free0=freeT; size_t c0=cmds.size();
      P3 so=S.pos[s]; vector<int> ps; if(!moveTo(s,c,getenv("BRMD")?atoi(getenv("BRMD")):maxd,getenv("BRMS")?atoi(getenv("BRMS")):maxst,ps))continue;
      for(int m:ps){S.move(s,m);cmds.push_back({s,m});}
      if(correct[s]){ correct[s]=0; freeT[pb.itype[s]].insert(so); }
      sup.push_back(s);
      if(bridgeRec(w,depth+1,sup,maxd,maxst)) return true;
      sup.pop_back();
      while(cmds.size()>c0){ auto pr=cmds.back(); if(!S.move(pr.first,pr.second^1)){fprintf(stderr,"bridge rollback fail\n");exit(1);} cmds.pop_back(); } correct=corr0; freeT=free0;
      if(++succ>=K) return false;
    }
  }
  return false;
}
bool bridge(int w,int maxd,int maxst,vector<pair<int,int>>&hist){
  vector<int> sup; gBefore=ncorrect(); gWo=S.pos[w]; bool ua=useAllowed; useAllowed=false; bool ok=bridgeRec(w,0,sup,maxd,maxst); useAllowed=ua;
  if(ok){ hist.push_back({(int)cmds.size(),ncorrect()}); fprintf(stderr,"bridged %d with %zu supporters -> correct %d\n",w,sup.size(),ncorrect()); }
  return ok; }
bool bridge_round(int maxd,int maxst,vector<pair<int,int>>&hist){ bool imp=false; for(int w=0;w<N;w++){ if(correct[w]||freeT[pb.itype[w]].empty())continue; if(bridge(w,maxd,maxst,hist)){imp=true; string cn=string(getenv("CKPT")?getenv("CKPT"):"ck.ckpt"); FILE*fc=fopen(cn.c_str(),"w"); for(auto&c:cmds)fprintf(fc,"%d %d\n",c.first,c.second); fclose(fc);} } return imp; }
bool bridgeL(int w,int maxd,int maxst,vector<pair<int,int>>&hist){
  // components without w
  map<P3,int> comp; int nc=0; vector<int> csz;
  for(int d=0;d<6;d++){ P3 b={S.pos[w][0]+D6[d][0],S.pos[w][1]+D6[d][1],S.pos[w][2]+D6[d][2]}; if(S.at(b[0],b[1],b[2])<0||comp.count(b))continue; int sz=0; deque<P3> dq; dq.push_back(b); comp[b]=nc;
    while(!dq.empty()){P3 a=dq.front();dq.pop_front();sz++; for(int e=0;e<6;e++){P3 x={a[0]+D6[e][0],a[1]+D6[e][1],a[2]+D6[e][2]}; if(x==S.pos[w]||comp.count(x)||S.at(x[0],x[1],x[2])<0)continue; comp[x]=nc; dq.push_back(x);} }
    csz.push_back(sz); nc++; }
  if(nc<2) return false;
  int big=max_element(csz.begin(),csz.end())-csz.begin();
  // candidate cells: empty, adjacent to a small-comp cube and to a big-comp cube
  vector<P3> cells; set<P3> seenc;
  for(auto&kv:comp){ if(kv.second==big)continue; for(int e=0;e<6;e++){ P3 c={kv.first[0]+D6[e][0],kv.first[1]+D6[e][1],kv.first[2]+D6[e][2]}; if(S.at(c[0],c[1],c[2])>=0||c==S.pos[w]||seenc.count(c))continue; seenc.insert(c);
      bool tb=false; for(int f=0;f<6;f++){P3 y={c[0]+D6[f][0],c[1]+D6[f][1],c[2]+D6[f][2]}; auto it=comp.find(y); if(it!=comp.end()&&it->second==big)tb=true;} if(tb)cells.push_back(c);} }
  int BS=getenv("BRS")?atoi(getenv("BRS")):30;
  fprintf(stderr,"bridge w=%d comps=%d cells=%zu\n",w,nc,cells.size());
  for(auto&c:cells){
    vector<int> ss; for(int s=0;s<N;s++){ if(s==w)continue; auto it=comp.find(S.pos[s]); if(it!=comp.end()&&it->second!=big)continue; ss.push_back(s);} 
    sort(ss.begin(),ss.end(),[&](int a,int b){ int ka=l1(S.pos[a],c)+(correct[a]?0:-1); int kb=l1(S.pos[b],c)+(correct[b]?0:-1); return ka<kb;}); if((int)ss.size()>BS)ss.resize(BS);
    for(int s:ss){
      vector<char> corr0=correct; vector<set<P3>> free0=freeT; size_t c0=cmds.size();
      vector<pair<int,int>> done;
      auto rollback=[&](){ while(cmds.size()>c0){ auto pr=cmds.back(); if(!S.move(pr.first,pr.second^1)){fprintf(stderr,"bridge rollback fail\n");exit(1);} cmds.pop_back(); } correct=corr0; freeT=free0; };
      P3 so=S.pos[s]; vector<int> ps; if(!moveTo(s,c,maxd,maxst,ps))continue;
      for(int m:ps){S.move(s,m);cmds.push_back({s,m});}
      if(correct[s]){ correct[s]=0; freeT[pb.itype[s]].insert(so); }
      vector<int> pw; P3 g; bool ua=useAllowed; useAllowed=false;
      bool wok=false; int BMS=getenv("BRMAXST")?atoi(getenv("BRMAXST")):200000;
      if(bfs_path(w,200,BMS,pw,g)){ for(int m:pw){S.move(w,m);cmds.push_back({w,m});} freeT[pb.itype[w]].erase(S.pos[w]); correct[w]=1; wok=true; }
      else { int lm=0; for(int m=0;m<6;m++){ if(S.move(w,m)){lm++;S.move(w,m^1);} } if(lm>0 && getenv("BRDIG")){ vector<pair<int,int>> h2; if(dig(w,atoi(getenv("BRDIG")),3,5,40,20000,h2)) wok=true; } }
      if(!wok){ useAllowed=ua; rollback(); continue; }
      if(!correct[s]){ vector<int> pr; P3 g2; if(!bfs_path(s,maxd,maxst,pr,g2)){ useAllowed=ua; rollback(); continue; } for(int m:pr){S.move(s,m);cmds.push_back({s,m});} freeT[pb.itype[s]].erase(S.pos[s]); correct[s]=1; }
      useAllowed=ua; hist.push_back({(int)cmds.size(),ncorrect()}); fprintf(stderr,"bridged %d via %d -> correct %d\n",w,s,ncorrect()); return true;
    }
  }
  return false;
}
bool bridgeL_round(int maxd,int maxst,vector<pair<int,int>>&hist){ bool imp=false; for(int w=0;w<N;w++){ if(correct[w]||freeT[pb.itype[w]].empty())continue; if(bridgeL(w,maxd,maxst,hist)){imp=true; string cn=string(getenv("CKPT")?getenv("CKPT"):"ck.ckpt"); FILE*fc=fopen(cn.c_str(),"w"); for(auto&c:cmds)fprintf(fc,"%d %d\n",c.first,c.second); fclose(fc);} } return imp; }

int main(int argc,char**argv){
  pb.load(argv[1]); N=pb.N; int maxd=argc>2?atoi(argv[2]):60; int maxst=argc>3?atoi(argv[3]):20000;
  string mode=argc>5?argv[5]:"near"; double win=argc>6?atof(argv[6]):0.2; int seed=argc>7?atoi(argv[7]):0; double noise=argc>8?atof(argv[8]):0; mt19937 rng(seed); uniform_real_distribution<double> U(0,1); S.init(pb);
  map<P3,double> rk; 
  if(mode!="near"){ set<P3> TT; for(auto&q:pb.target)TT.insert(q); vector<pair<double,P3>> v;
    map<P3,int> dep; if(mode=="depth"||mode=="depthA"){ // depth from exterior of I (6-conn flood outside)
      P3 lo={1000,1000,1000},hi={-1000,-1000,-1000}; for(auto&q:pb.target)for(int a=0;a<3;a++){lo[a]=min(lo[a],q[a]-1);hi[a]=max(hi[a],q[a]+1);}
      set<P3> ext; deque<P3> dq; ext.insert(lo); dq.push_back(lo);
      while(!dq.empty()){P3 p=dq.front();dq.pop_front();for(int d=0;d<6;d++){P3 r={p[0]+D6[d][0],p[1]+D6[d][1],p[2]+D6[d][2]};bool in=true;for(int a=0;a<3;a++)if(r[a]<lo[a]||r[a]>hi[a])in=false;if(!in||TT.count(r)||ext.count(r))continue;ext.insert(r);dq.push_back(r);}}
      for(auto&q:pb.target){for(int d=0;d<6;d++){P3 r={q[0]+D6[d][0],q[1]+D6[d][1],q[2]+D6[d][2]};if(ext.count(r)){dep[q]=1;dq.push_back(q);break;}}}
      while(!dq.empty()){P3 p=dq.front();dq.pop_front();for(int d=0;d<6;d++){P3 r={p[0]+D6[d][0],p[1]+D6[d][1],p[2]+D6[d][2]};if(TT.count(r)&&!dep.count(r)){dep[r]=dep[p]+1;dq.push_back(r);}}}
    }
    for(auto&q:pb.target){int nb=0;for(int d=0;d<6;d++){P3 r={q[0]+D6[d][0],q[1]+D6[d][1],q[2]+D6[d][2]};nb+=TT.count(r);}
      double key;
      if(mode=="enc")key=-nb; else if(mode=="enca")key=nb; else if(mode=="depth")key=-dep[q]; else if(mode=="depthA")key=dep[q]; else key=0;
      v.push_back({key+noise*U(rng),q});}
    sort(v.begin(),v.end()); for(size_t i=0;i<v.size();i++)rk[v[i].second]=i; }
  freeT.assign(pb.T,{}); for(int i=0;i<N;i++){freeT[pb.ttype[i]].insert(pb.target[i]);tt_at[pb.target[i]]=pb.ttype[i];}
  correct.assign(N,0);
  for(int c=0;c<N;c++){auto it=tt_at.find(S.pos[c]);if(it!=tt_at.end()&&it->second==pb.itype[c]){correct[c]=1;freeT[pb.itype[c]].erase(S.pos[c]);}}
  if(getenv("RESUME")){ ifstream rf(getenv("RESUME")); int cc,mm; while(rf>>cc>>mm){ if(!S.move(cc,mm)){fprintf(stderr,"resume move fail\n");exit(1);} cmds.push_back({cc,mm}); }
    freeT.assign(pb.T,{}); for(int i=0;i<N;i++)freeT[pb.ttype[i]].insert(pb.target[i]); correct.assign(N,0);
    for(int c=0;c<N;c++){auto it=tt_at.find(S.pos[c]);if(it!=tt_at.end()&&it->second==pb.itype[c]){correct[c]=1;freeT[pb.itype[c]].erase(S.pos[c]);}}
    fprintf(stderr,"resumed %zu cmds correct %d\n",cmds.size(),ncorrect()); }
  if(getenv("PRIO")){ ifstream pf(getenv("PRIO")); int o; while(pf>>o) prioS.insert(o); fprintf(stderr,"prio %zu\n",prioS.size()); }
  if(getenv("PSEUDO")){ int w,R; sscanf(getenv("PSEUDO"),"%d %d",&w,&R); int t=pb.itype[w]; vector<P3> ps; P3 p0=S.pos[w];
    for(int dx=-R;dx<=R;dx++)for(int dy=-R;dy<=R;dy++)for(int dz=-R;dz<=R;dz++){ if(abs(dx)+abs(dy)+abs(dz)>R||abs(dx)+abs(dy)+abs(dz)<2)continue; P3 q={p0[0]+dx,p0[1]+dy,p0[2]+dz}; if(S.at(q[0],q[1],q[2])>=0||tt_at.count(q))continue; bool adj=false; for(int d=0;d<6;d++) if(S.at(q[0]+D6[d][0],q[1]+D6[d][1],q[2]+D6[d][2])>=0) adj=true; if(adj) ps.push_back(q);} 
    fprintf(stderr,"pseudo cells %zu\n",ps.size());
    set<P3> sv=freeT[t]; for(auto&q:ps) freeT[t].insert(q); for(auto&q:sv) if(!ps.empty()) {} 
    // keep only pseudo targets so w goes there
    freeT[t].clear(); for(auto&q:ps) freeT[t].insert(q);
    vector<pair<int,int>> h2; useAllowed=false; int D=getenv("DIG")?atoi(getenv("DIG")):3;
    bool ok=false; vector<int> pth; P3 gg; if(bfs_path(w,100,1000000,pth,gg)){ for(int m:pth){S.move(w,m);cmds.push_back({w,m});} ok=true; }
    if(!ok) ok=dig(w,D,getenv("DIGRAD")?atoi(getenv("DIGRAD")):3,getenv("PARK")?atoi(getenv("PARK")):5,100,200000,h2);
    fprintf(stderr,"pseudo move ok=%d pos %d %d %d\n",(int)ok,S.pos[w][0],S.pos[w][1],S.pos[w][2]);
    FILE*f=fopen(argv[4],"w"); for(auto&c:cmds)fprintf(f,"%d %d\n",c.first,c.second); fclose(f); {string en=string(argv[4])+".end"; FILE*fe=fopen(en.c_str(),"w"); for(int c=0;c<N;c++)fprintf(fe,"%d %d %d\n",S.pos[c][0],S.pos[c][1],S.pos[c][2]); fclose(fe);} exit(0); }
  if(getenv("DIAG")){ for(int w=0;w<N;w++){ if(correct[w])continue; int lm=0; for(int m=0;m<6;m++){ if(S.move(w,m)){lm++; S.move(w,m^1);} } int nb=0; for(int d=0;d<6;d++) if(S.at(S.pos[w][0]+D6[d][0],S.pos[w][1]+D6[d][1],S.pos[w][2]+D6[d][2])>=0)nb++; auto occ=[&](int x,int y,int z){int a2=S.at(x,y,z);return a2>=0&&a2!=w&&false;}; fprintf(stderr,"w=%d type %d pos %d %d %d legal=%d nb=%d reachEmpty=%d cut=%d\n",w,pb.itype[w],S.pos[w][0],S.pos[w][1],S.pos[w][2],lm,nb,(int)reach_occ(w,S.pos[w],occ,100000),0); } exit(0); }
  if(getenv("EVICTF")){ int R=atoi(getenv("EVICTF")); vector<P3> fr; for(int t=0;t<pb.T;t++)for(auto&q:freeT[t])fr.push_back(q); int ne=0; for(int o=0;o<N;o++){ if(!correct[o])continue; bool near=false; for(auto&q:fr) if(l1(S.pos[o],q)<=R){near=true;break;} if(near){correct[o]=0;freeT[pb.itype[o]].insert(S.pos[o]);evictedS.insert(o);ne++;} } fprintf(stderr,"evictF %d\n",ne); }
  if(getenv("EVICTC")){ int SL=atoi(getenv("EVICTC")); int ne=0; vector<int> st; for(int c=0;c<N;c++)if(!correct[c])st.push_back(c);
    for(int w:st){ int tw=pb.itype[w]; if(freeT[tw].empty())continue; P3 bf; int bd=1e9; for(auto&f:freeT[tw]){int d=l1(S.pos[w],f); if(d<bd){bd=d;bf=f;}}
      for(int o=0;o<N;o++){ if(!correct[o]||pb.itype[o]!=tw)continue; if(l1(S.pos[o],S.pos[w])+l1(S.pos[o],bf)<=bd+2*SL){correct[o]=0;freeT[tw].insert(S.pos[o]);evictedS.insert(o);ne++;} } }
    fprintf(stderr,"evictC %d\n",ne); }
  if(getenv("EVICTR")){ int R=atoi(getenv("EVICTR")); vector<int> st; for(int c=0;c<N;c++)if(!correct[c])st.push_back(c); int ne=0; for(int o=0;o<N;o++){ if(!correct[o])continue; bool near=false; for(int c:st) if(l1(S.pos[o],S.pos[c])<=R){near=true;break;} if(near){correct[o]=0;freeT[pb.itype[o]].insert(S.pos[o]);evictedS.insert(o);ne++;} } fprintf(stderr,"evictR %d\n",ne); }
  if(argc>12){ ifstream ef(argv[12]); int o; int ne=0; while(ef>>o){ if(o>=0&&o<N&&correct[o]){correct[o]=0;freeT[pb.itype[o]].insert(S.pos[o]);evictedS.insert(o);ne++;} } fprintf(stderr,"evicted %d\n",ne); }
  vector<pair<int,int>> hist{{0,ncorrect()}};
  bool progress=true; int DIG=getenv("DIG")?atoi(getenv("DIG")):0; int UR=argc>9?atoi(argv[9]):2;
  while(progress&&(int)cmds.size()<pb.maxc){
    progress=false;
    if(mode=="conn"){ map<P3,int> dummy; rk=connRank(noise,rng,dummy); }
    if(mode!="near"){ vector<pair<double,P3>> fr; for(int t=0;t<pb.T;t++)for(auto&q:freeT[t])fr.push_back({rk[q],q}); sort(fr.begin(),fr.end()); size_t k=max<size_t>(1,(size_t)(fr.size()*win)); allowedS.clear(); for(size_t i=0;i<k&&i<fr.size();i++)allowedS.insert(fr[i].second); useAllowed=true; }
    vector<pair<int,int>> keys;
    for(int c=0;c<N;c++){ if(correct[c]||freeT[pb.itype[c]].empty())continue; int best=1e9;for(auto&q:freeT[pb.itype[c]])best=min(best,l1(S.pos[c],q)); keys.push_back({(prioS.count(c)?-1000000:0)+(tt_at.count(S.pos[c])?0:100000)+best+(int)(noise*3*U(rng)),c});}
    sort(keys.begin(),keys.end());
    for(auto&kc:keys){int c=kc.second; if(correct[c])continue; vector<int> path;P3 goal;
      bool ua=useAllowed; if(prioS.count(c)) useAllowed=false; bool okp=bfs_path(c,maxd,maxst,path,goal); useAllowed=ua; if(!okp)continue;
      for(int m:path){S.move(c,m);cmds.push_back({c,m});}
      freeT[pb.itype[c]].erase(S.pos[c]);correct[c]=1;progress=true;hist.push_back({(int)cmds.size(),ncorrect()});
    }
    if(!progress&&mode!="near"&&win<1.0){win=min(1.0,win*2);progress=true;}
    if(!progress&&!evictedS.empty()){ for(int o:evictedS){ if(!correct[o]){ auto it=tt_at.find(S.pos[o]); if(it!=tt_at.end()&&it->second==pb.itype[o]&&freeT[pb.itype[o]].count(S.pos[o])){correct[o]=1;freeT[pb.itype[o]].erase(S.pos[o]);hist.push_back({(int)cmds.size(),ncorrect()});} } } evictedS.clear(); progress=true; }
    if(!progress&&getenv("BRLEG")){ useAllowed=false; if(bridgeL_round(maxd,maxst,hist))progress=true; }
    if(!progress&&getenv("BRIDGE")){ useAllowed=false; if(bridge_round(maxd,maxst,hist))progress=true; }
    if(!progress&&getenv("RELAY")){ useAllowed=false; if(relay_round(maxd,maxst,hist))progress=true; }
    if(!progress&&DIG>0){ useAllowed=false; if(dig_round(DIG,getenv("DIGRAD")?atoi(getenv("DIGRAD")):3,getenv("PARK")?atoi(getenv("PARK")):5,getenv("DIGMD")?atoi(getenv("DIGMD")):40,getenv("DIGMS")?atoi(getenv("DIGMS")):20000,hist)){progress=true;} }
    if(!progress){ useAllowed=false; if(unstick_round(maxd,maxst,hist,UR)){progress=true;} }
    fprintf(stderr,"pass: correct %d cmds %zu\n",ncorrect(),cmds.size());{string cn=string(argc>4?argv[4]:"ck")+".ckpt"; FILE*fc=fopen(cn.c_str(),"w"); for(auto&c:cmds)fprintf(fc,"%d %d\n",c.first,c.second); fclose(fc);}
  }
  {string en=string(argc>4?argv[4]:"/dev/null")+".stuck"; FILE*fs=fopen(en.c_str(),"w"); for(int c=0;c<N;c++) if(!correct[c]) fprintf(fs,"%d %d %d %d %d\n",c,pb.itype[c],S.pos[c][0],S.pos[c][1],S.pos[c][2]); fclose(fs);}
  int bl=0;double bs=-1e9;for(auto&h:hist){double s=0.9*h.second/N-0.1*(double)h.first/pb.maxc;if(s>bs){bs=s;bl=h.first;}}
  Sim s2; s2.init(pb); for(int i=0;i<bl;i++)s2.move(cmds[i].first,cmds[i].second);
  int C=0;for(int c=0;c<N;c++){auto it=tt_at.find(s2.pos[c]);if(it!=tt_at.end()&&it->second==pb.itype[c])C++;}
  printf("RESULT correct %d cmds %d fitness %.4f\n",C,bl,score(C,bl));
  {string en=string(argc>4?argv[4]:"/dev/null")+".end"; FILE*fe=fopen(en.c_str(),"w"); for(int c=0;c<N;c++)fprintf(fe,"%d %d %d\n",s2.pos[c][0],s2.pos[c][1],s2.pos[c][2]); fclose(fe);}
  FILE*f=fopen(argc>4?argv[4]:"/dev/null","w");for(int i=0;i<bl;i++)fprintf(f,"%d %d\n",cmds[i].first,cmds[i].second);fclose(f);
}
