"""Logistics network maximum flow analysis using the Edmonds-Karp algorithm."""

from collections import deque


def bfs(capacity, flow, source, sink, parent):
    """Find an augmenting path from source to sink using BFS."""
    visited = {source}
    queue = deque([source])

    while queue:
        node = queue.popleft()
        for neighbor in range(len(capacity)):
            residual = capacity[node][neighbor] - flow[node][neighbor]
            if neighbor not in visited and residual > 0:
                visited.add(neighbor)
                parent[neighbor] = node
                if neighbor == sink:
                    return True
                queue.append(neighbor)

    return False


def edmonds_karp(capacity, source, sink):
    """
    Compute maximum flow using Edmonds-Karp.
    Returns tuple(max_flow, flow_matrix).
    """
    n = len(capacity)
    flow = [[0] * n for _ in range(n)]
    max_flow = 0

    while True:
        parent = [-1] * n
        if not bfs(capacity, flow, source, sink, parent):
            break

        # Find the bottleneck capacity along the augmenting path
        path_flow = float("inf")
        node = sink
        while node != source:
            prev = parent[node]
            path_flow = min(path_flow, capacity[prev][node] - flow[prev][node])
            node = prev

        # Update flow along the path (including reverse edges)
        node = sink
        while node != source:
            prev = parent[node]
            flow[prev][node] += path_flow
            flow[node][prev] -= path_flow
            node = prev

        max_flow += path_flow

    return max_flow, flow


def build_network():
    """
    Build the logistics network graph.

    Network layout:
      super_source -> T1, T2 (infinite capacity)
      T1, T2 -> warehouses W1-W4
      W1-W4 -> stores S1-S14
      S1-S14 -> super_sink (infinite capacity)
    """
    nodes = {
        "T1": 0, "T2": 1,
        "W1": 2, "W2": 3, "W3": 4, "W4": 5,
        "S1": 6,  "S2": 7,  "S3": 8,
        "S4": 9,  "S5": 10, "S6": 11,
        "S7": 12, "S8": 13, "S9": 14,
        "S10": 15, "S11": 16, "S12": 17, "S13": 18, "S14": 19,
        "source": 20,
        "sink": 21,
    }

    n = len(nodes)
    capacity = [[0] * n for _ in range(n)]
    INF = 10 ** 9

    def add_edge(u, v, cap):
        capacity[nodes[u]][nodes[v]] = cap

    # Virtual super source connects to both terminals
    add_edge("source", "T1", INF)
    add_edge("source", "T2", INF)

    # Terminals -> Warehouses
    add_edge("T1", "W1", 25)
    add_edge("T1", "W2", 20)
    add_edge("T1", "W3", 15)
    add_edge("T2", "W3", 15)
    add_edge("T2", "W4", 30)
    add_edge("T2", "W2", 10)

    # Warehouses -> Stores
    add_edge("W1", "S1",  15)
    add_edge("W1", "S2",  10)
    add_edge("W1", "S3",  20)
    add_edge("W2", "S4",  15)
    add_edge("W2", "S5",  10)
    add_edge("W2", "S6",  25)
    add_edge("W3", "S7",  20)
    add_edge("W3", "S8",  15)
    add_edge("W3", "S9",  10)
    add_edge("W4", "S10", 20)
    add_edge("W4", "S11", 10)
    add_edge("W4", "S12", 15)
    add_edge("W4", "S13",  5)
    add_edge("W4", "S14", 10)

    # All stores connect to virtual super sink
    for store in [f"S{i}" for i in range(1, 15)]:
        add_edge(store, "sink", INF)

    return capacity, nodes


# Warehouse -> stores mapping
WAREHOUSE_STORES = {
    "W1": ["S1", "S2", "S3"],
    "W2": ["S4", "S5", "S6"],
    "W3": ["S7", "S8", "S9"],
    "W4": ["S10", "S11", "S12", "S13", "S14"],
}

TERMINALS = ["T1", "T2"]
STORES = [f"S{i}" for i in range(1, 15)]

TERMINAL_LABELS = {"T1": "Terminal 1", "T2": "Terminal 2"}
STORE_LABELS = {f"S{i}": f"Store {i}" for i in range(1, 15)}


def calculate_terminal_to_store_flows(flow, nodes):
    """
    Attribute store flows back to originating terminals.

    For warehouses fed by a single terminal the attribution is 100%.
    For warehouses fed by both terminals the attribution is proportional
    to each terminal's share of the total inbound flow to that warehouse.
    """
    result = {t: {s: 0.0 for s in STORES} for t in TERMINALS}

    for warehouse, stores in WAREHOUSE_STORES.items():
        w = nodes[warehouse]

        terminal_inflows = {
            t: max(flow[nodes[t]][w], 0) for t in TERMINALS
        }
        total_in = sum(terminal_inflows.values())

        for store in stores:
            s = nodes[store]
            store_flow = flow[w][s]
            if store_flow <= 0:
                continue

            for terminal in TERMINALS:
                share = terminal_inflows[terminal] / total_in if total_in > 0 else 0
                result[terminal][store] += share * store_flow

    return result


def print_flow_table(terminal_flows):
    """Print the Terminal -> Store flow distribution table."""
    print(f"{'Terminal':<14} {'Store':<10} {'Actual Flow (units)'}")
    print("-" * 42)
    for terminal in TERMINALS:
        for store in STORES:
            val = terminal_flows[terminal][store]
            display = int(val) if val == int(val) else round(val, 2)
            t_label = TERMINAL_LABELS[terminal]
            s_label = STORE_LABELS[store]
            print(f"{t_label:<14} {s_label:<10} {display}")
        print()


def print_analysis(max_flow, flow, nodes, terminal_flows):
    """Print answers to the four analysis questions."""
    # Q1: Which terminal provides the most flow?
    t1_out = sum(max(flow[nodes["T1"]][nodes[w]], 0) for w in WAREHOUSE_STORES)
    t2_out = sum(max(flow[nodes["T2"]][nodes[w]], 0) for w in WAREHOUSE_STORES)
    print("1. Terminal throughput:")
    print(f"   Terminal 1: {t1_out} units")
    print(f"   Terminal 2: {t2_out} units")
    leader = "Terminal 1" if t1_out >= t2_out else "Terminal 2"
    print(f"   -> {leader} provides the highest flow.\n")

    # Q2: Which routes have the lowest capacity?
    print("2. Routes with lowest capacity (potential bottlenecks):")
    edges = [
        ("T1", "W1", 25), ("T1", "W2", 20), ("T1", "W3", 15),
        ("T2", "W3", 15), ("T2", "W4", 30), ("T2", "W2", 10),
        ("W1", "S1", 15), ("W1", "S2", 10), ("W1", "S3", 20),
        ("W2", "S4", 15), ("W2", "S5", 10), ("W2", "S6", 25),
        ("W3", "S7", 20), ("W3", "S8", 15), ("W3", "S9", 10),
        ("W4", "S10", 20), ("W4", "S11", 10), ("W4", "S12", 15),
        ("W4", "S13", 5), ("W4", "S14", 10),
    ]
    min_cap = min(cap for _, _, cap in edges)
    low_cap = [(u, v, cap) for u, v, cap in edges if cap <= min_cap + 5]
    for u, v, cap in low_cap:
        print(f"   {u} -> {v}: {cap} units")
    print()

    # Q3: Which stores received the least goods?
    print("3. Stores with zero or minimal supply:")
    totals = {s: sum(terminal_flows[t][s] for t in TERMINALS) for s in STORES}
    zero_stores = [s for s, v in totals.items() if v == 0]
    low_stores = sorted(totals.items(), key=lambda x: x[1])[:5]
    if zero_stores:
        print(f"   Stores with 0 units: {', '.join(zero_stores)}")
    print(f"   Five lowest: {', '.join(f'{s}={int(v)}' for s, v in low_stores)}")
    print("   Supply to these stores could be increased by expanding")
    print("   warehouse output capacity on the relevant routes.\n")

    # Q4: Bottlenecks
    print("4. System bottlenecks:")
    total_terminal_capacity = 60 + 55
    total_store_capacity = sum(cap for _, v, cap in edges if v.startswith("S"))
    print(f"   Total terminal output capacity: {total_terminal_capacity} units")
    print(f"   Total store input capacity:     {total_store_capacity} units")
    print(f"   Achieved maximum flow:          {max_flow} units")
    print("   -> The bottleneck is at the terminal output level.")
    print("      Increasing warehouse-to-store capacity would not improve")
    print("      overall throughput without first expanding terminal output.")


if __name__ == "__main__":
    capacity, nodes = build_network()
    max_flow, flow = edmonds_karp(capacity, nodes["source"], nodes["sink"])

    print(f"Maximum flow in the logistics network: {max_flow} units\n")
    print("=" * 38)

    terminal_flows = calculate_terminal_to_store_flows(flow, nodes)

    print_flow_table(terminal_flows)
    print("=" * 38)
    print()
    print_analysis(max_flow, flow, nodes, terminal_flows)
