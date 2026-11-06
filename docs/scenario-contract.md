# Scenario contract

- `origin`: workshop `[x,y]` in local Cartesian kilometers.
- `suppliers`: unique ID, optional name, and position in the same coordinate system.
- `stock`: individual piece IDs with supplier, material key, length in mm, and cost.
- `demand`: label, compatible material key, cut length in mm, and integer quantity.
- `kerf_mm`: conservative material loss per requested cut.
- `waste_cost_per_meter`: penalty for unused length in selected stock.
- `travel_cost_per_km`: cost weight of the closed pickup tour.

Unused stock is not charged or counted as consumed. Remaining offcuts may be reusable; the objective’s leftover penalty is a user preference, not a physical waste or carbon claim.

Demand is expanded into individual cuts, sorted longest-first, and assigned to compatible individual stock pieces. The search considers purchase cost, conservative per-cut kerf, leftover length, and the closed pickup tour of the required suppliers.

`objective = purchase_cost + waste_cost_per_meter × leftover_mm / 1000 + travel_cost_per_km × pickup_km`

Assignments are explored with branch-and-bound. Purchase cost is a safe lower bound because the other terms are nonnegative. Equivalent stock candidates are deduplicated only when supplier, cost, stock length, remaining capacity, and used-state agree. Each supplier set has its own exact Held–Karp closed Euclidean tour, cached during the search.

The cutting search stops at 30,000 visited nodes. `search_complete` distinguishes a completed search from a best-so-far plan. The initial incumbent is input-order first fit when feasible. This is an explicit algorithmic baseline, not a claim about normal workshop performance. Exact stock-assignment optimality is only claimed when the search completes (subject to floating-point arithmetic).

Limits: 16 cuts, 20 individual stock pieces, 8 suppliers. All costs use one arbitrary currency unit. Each requested piece consumes one kerf, including the last cut on a stock piece; this is deliberately conservative.
