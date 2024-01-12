from joblib import Parallel, delayed
import nx_parallel as nxp

__all__ = [
    "is_reachable",
    "is_strongly_connected",
]


def is_reachable(G, s, t):
    """ 
    Parallel implementation of :func:`networkx.algorithms.tournament.is_reachable`

    Decides whether there is a path from `s` to `t` in the tournament `G`.

    Parallel Computation : The function parallelizes the calculation of two
    neighborhoods of vertices in `G` and checks closure conditions for each 
    neighborhood subset in parallel. 

    Parameters
    ----------
    G : NetworkX graph
        A directed graph representing a tournament.

    s : node
        A node in the graph.

    t : node
        A node in the graph.

    Returns
    -------
    bool
        Whether there is a path from `s` to `t` in `G`.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.DiGraph([(1, 0), (1, 3), (1, 2), (2, 3), (2, 0), (3, 0)])
    >>> nx.tournament.is_reachable(G, 1, 3, backend="parallel")
    True
    >>> import nx_parallel as nxp
    >>> nx.tournament.is_reachable(nxp.ParallelGraph(G), 3, 2)
    False
    >>> nx.tournament.is_reachable(G, 3, 2, backend="parallel")
    False
    """
    if hasattr(G, "graph_object"):
        G = G.graph_object

    G_adj = G._adj
    setG = set(G)

    cpu_count = nxp.cpu_count()

    def two_nbrhood_subset(G, chunk):
        result = []
        for v in chunk:
            v_nbrs = G_adj[v].keys()
            result.append(v_nbrs | {x for nbr in v_nbrs for x in G_adj[nbr]})
        return result

    def is_closed(G, nodes):
        return all(v in G_adj[u] for u in setG - nodes for v in nodes)

    def check_closure_subset(chunk):
        return all(not (s in S and t not in S and is_closed(G, S)) for S in chunk)

    # send chunk of vertices to each process (calculating neighborhoods)
    num_in_chunk = max(len(G) // cpu_count, 1)

    # neighborhoods = [two_neighborhood_subset(G, chunk) for chunk in node_chunks]
    neighborhoods = Parallel(n_jobs=cpu_count)(
        delayed(two_nbrhood_subset)(G, chunk) for chunk in nxp.chunks(G, num_in_chunk)
    )

    # send chunk of neighborhoods to each process (checking closure conditions)
    nbrhoods = (nhood for nh_chunk in neighborhoods for nhood in nh_chunk)
    results = Parallel(n_jobs=cpu_count)(
        delayed(check_closure_subset)(ch) for ch in nxp.chunks(nbrhoods, num_in_chunk)
    )
    return all(results)


def is_strongly_connected(G):
    """
    Paralell implementation of 
    :func:`networkx.algorithms.tournament.is_strongly_connected`

    Decides whether the given tournament is strongly connected.

    Parallel Computation : The parallel computation is implemented by dividing the
    nodes into chunks and then checking whether each node is reachable from each 
    other node in parallel.

    Parameters
    ----------
    G : NetworkX graph
        A directed graph representing a tournament.

    Returns
    -------
    bool
        Whether the tournament is strongly connected.

    Examples
    --------
    >>> import networkx as nx
    >>> import nx_parallel as nxp
    >>> G = nx.DiGraph([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    >>> nx.tournament.is_strongly_connected(nxp.ParallelGraph(G))
    False
    >>> nx.tournament.is_strongly_connected(G, backend="parallel")
    False
    >>> G.remove_edge(0, 3)
    >>> G.add_edge(3, 0)
    >>> nx.tournament.is_strongly_connected(G, backend="parallel")
    True
    """
    if hasattr(G, "graph_object"):
        G = G.graph_object

    # Subset version of is_reachable
    def is_reachable_subset(G, chunk):
        return all(is_reachable(G, u, v) for v in chunk for u in G)

    cpu_count = nxp.cpu_count()
    num_in_chunk = max(len(G) // cpu_count, 1)
    node_chunks = nxp.chunks(G, num_in_chunk)

    results = Parallel(n_jobs=cpu_count)(
        delayed(is_reachable_subset)(G, chunk) for chunk in node_chunks
    )
    return all(results)
