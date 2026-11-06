"""Bounded cutting-stock search coupled to an exact small pickup tour."""
import math
SEARCH_LIMIT=30000

def num(x,label,lo,hi):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not lo<=x<=hi: raise ValueError(f"{label} must be finite and in [{lo}, {hi}]")
    return x

def tour(points,origin):
    # Held-Karp exact closed Euclidean tour. Coordinates are in kilometers.
    n=len(points)
    if not n: return 0,[]
    d=lambda a,b:math.hypot(a[0]-b[0],a[1]-b[1])
    dp={(1<<i,i):(d(origin,points[i]),[i]) for i in range(n)}
    for mask in range(1,1<<n):
        for i in range(n):
            if (mask,i) not in dp: continue
            cost,path=dp[mask,i]
            for j in range(n):
                if mask>>j&1: continue
                key=(mask|1<<j,j);value=cost+d(points[i],points[j])
                if key not in dp or value<dp[key][0]:dp[key]=(value,path+[j])
    return min((v[0]+d(points[i],origin),v[1]) for (mask,i),v in dp.items() if mask==(1<<n)-1)

def solve(s):
    stock=s.get("stock");demand=s.get("demand");suppliers=s.get("suppliers")
    if not isinstance(stock,list) or not 1<=len(stock)<=20: raise ValueError("Provide 1 to 20 individual stock pieces")
    if not isinstance(suppliers,list) or not 1<=len(suppliers)<=8: raise ValueError("Provide 1 to 8 suppliers")
    def xy(p):
        if not isinstance(p,list) or len(p)!=2: raise ValueError("Coordinates must be [x,y] in kilometers")
        return [num(x,"coordinate",-1000,1000) for x in p]
    if any(not isinstance(v,dict) for v in suppliers+stock): raise ValueError("Suppliers and stock entries must be objects")
    places={}
    for v in suppliers:
        if not isinstance(v.get('id'),str) or not v['id'] or v['id'] in places: raise ValueError("Supplier IDs must be unique nonempty strings")
        places[v['id']]=xy(v.get('position'))
    origin=xy(s.get('origin',[0,0]));kerf=num(s.get('kerf_mm',3),'kerf',0,20)
    waste_weight=num(s.get('waste_cost_per_meter',2),'waste cost',0,1000);trip_weight=num(s.get('travel_cost_per_km',1),'travel cost',0,1000)
    ids=set()
    for v in stock:
        if not isinstance(v.get('id'),str) or not v['id'] or v['id'] in ids:raise ValueError("Stock IDs must be unique")
        ids.add(v['id'])
        num(v.get('length_mm'),'stock length',1,20000);num(v.get('cost',0),'cost',0,10000)
        if v.get('supplier') not in places:raise ValueError("Unknown stock supplier")
        if not isinstance(v.get('material'),str) or not v['material']:raise ValueError("Stock needs a material key")
    if not isinstance(demand,list) or not demand:raise ValueError("Provide demand pieces")
    if any(not isinstance(v,dict) for v in demand): raise ValueError("Demand entries must be objects")
    pieces=[]
    for v in demand:
        num(v.get('length_mm'),'cut length',1,20000)
        if type(v.get('quantity')) is not int or not 1<=v['quantity']<=16:raise ValueError("Quantity must be an integer from 1 to 16")
        if not isinstance(v.get('material'),str):raise ValueError("Demand needs a material key")
        for k in range(v['quantity']):pieces.append({'label':str(v.get('label','Cut'))[:80]+f' #{k+1}','length_mm':v['length_mm'],'material':v['material']})
    if len(pieces)>16:raise ValueError("At most 16 requested cuts")
    ordered=sorted(pieces,key=lambda p:p['length_mm'],reverse=True)
    remaining=[v['length_mm'] for v in stock];patterns=[[] for _ in stock];cache={}
    def assess(pattern):
        used=[i for i,v in enumerate(pattern) if v];selected=sorted({stock[i]['supplier'] for i in used});key=tuple(selected)
        if key not in cache:cache[key]=tour([places[k] for k in selected],origin)
        distance,order=cache[key]
        length=sum(stock[i]['length_mm'] for i in used);cut=sum(p['length_mm'] for i in used for p in pattern[i]);loss=kerf*sum(len(pattern[i]) for i in used);leftover=length-cut-loss
        cost=sum(stock[i].get('cost',0) for i in used);score=cost+waste_weight*leftover/1000+trip_weight*distance
        return {'objective':round(score,6),'purchase_cost':cost,'pickup_km':round(distance,4),'individual_pickups_km':round(sum(2*math.dist(origin,places[k]) for k in selected),4),'route':[selected[i] for i in order],'stock_used':len(used),'cut_mm':cut,'stock_mm':length,'kerf_mm':loss,'leftover_mm':round(leftover,4),'utilization_percent':round(100*cut/length,2) if length else 0,'patterns':[{'stock_id':stock[i]['id'],'supplier':stock[i]['supplier'],'stock_length_mm':stock[i]['length_mm'],'cuts':list(pattern[i]),'remaining_mm':round(stock[i]['length_mm']-sum(p['length_mm']+kerf for p in pattern[i]),4)} for i in used]}
    # Baseline is explicitly input-order first fit, not a claim about human performance.
    base=[[] for _ in stock];space=[v['length_mm'] for v in stock];feasible=True
    for cut in pieces:
        for i,v in enumerate(stock):
            if v['material']==cut['material'] and space[i]>=cut['length_mm']+kerf:
                space[i]-=cut['length_mm']+kerf;base[i].append(cut);break
        else:feasible=False;break
    baseline=assess(base) if feasible else None
    best=baseline;nodes=0;capped=False
    def search(k,purchase):
        nonlocal best,nodes,capped
        nodes+=1
        if nodes>SEARCH_LIMIT:capped=True;return
        # Every other term in the objective is nonnegative, so purchase is a safe lower bound.
        if best and purchase>best['objective']+1e-7:return
        if k==len(ordered):
            candidate=assess(patterns)
            if best is None or candidate['objective']<best['objective']-1e-7:best=candidate
            return
        cut=ordered[k];need=cut['length_mm']+kerf
        candidates=[i for i,v in enumerate(stock) if v['material']==cut['material'] and remaining[i]+1e-9>=need]
        candidates.sort(key=lambda i:(not bool(patterns[i]),stock[i].get('cost',0),remaining[i]-need))
        seen=set()
        for i in candidates:
            v=stock[i];sig=(remaining[i],bool(patterns[i]),v['supplier'],v.get('cost',0),v['length_mm'])
            if sig in seen:continue
            seen.add(sig);unused=not patterns[i];remaining[i]-=need;patterns[i].append(cut)
            search(k+1,purchase+(v.get('cost',0) if unused else 0))
            patterns[i].pop();remaining[i]+=need
            if capped:return
    search(0,0)
    if best is None:raise ValueError("No feasible assignment found within the search budget; add matching stock, reduce demand, or simplify the case")
    return {'baseline':baseline,'optimized':best,'search_nodes':nodes,'search_complete':not capped,'model':'Exact pickup tour on straight-line coordinates; bounded cutting-stock search. Compatible material keys must encode grade and cross-section.'}
