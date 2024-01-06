from joblib import Parallel, delayed
from networkx.algorithms.centrality.betweenness import (
    _accumulate_basic,
    _accumulate_endpoints,
    _rescale,
    _single_source_dijkstra_path_basic,
    _single_source_shortest_path_basic,
)
from networkx.utils import py_random_state
import nx_parallel as nxp

__all__ = ["betweenness_centrality"]


@py_random_state(5)
def betweenness_centrality(
    G, k=None, normalized=True, weight=None, endpoints=False, seed=None, n_jobs=-1
):
    """Parallel implementation of :func:`networkx.betweenness_centrality`.

    Returns the shortest-path betweenness centrality for all the nodes.
    Betweenness centrality of a node $v$ is the sum of the fraction of all-pairs 
    shortest paths that pass through $v$.

    Refer to the :func:`networkx.betweenness_centrality` documentation for more 
    details on how the betweenness centrality is defined and computed.

    Parameters
    ----------
    G : graph
      A NetworkX graph.

    k : int, optional (default=None)
        If k is not None, use k node samples to estimate betweenness.

    normalized : bool, optional
        If True the betweenness values are normalized

    weight : None or string, optional (default=None)
        If None, all edge weights are considered equal.
        Otherwise, holds the name of the edge attribute used as weight.

    endpoints : bool, optional
        If True include the endpoints in the shortest path counts.

    seed : integer, random_state, or None (default)
        Indicator of random number generation state. Only used if `k` is not None.

    n_jobs : int, optional (default=-1)
        Number of parallel jobs. If -1, uses all available CPUs.
        For `n_jobs` < 0, (`n_cpus` + 1 + `n_jobs`) CPUs are used.
        Here, `n_cpus` are computed by `os.cpu_count()`.
        If an invalid value is given, then `n_jobs` is set to default.

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with betweenness centrality as the value.

    Notes
    -------
    The parallel computation is implemented by dividing the nodes into chunks and
    computing betweenness centrality for each chunk concurrently.

    Examples
    --------
    >>> import networkx as nx
    >>> import nx_parallel as nxp
    >>> G = nx.Graph()
    >>> G.add_weighted_edges_from([(1, 0, 1), (1, 2, 1), (2, 0, 3)])
    >>> centrality = nxp.betweenness_centrality(G, n_jobs=3)
    >>> centrality_ = nx.betweenness_centrality(G, backend="parallel", n_jobs=3)

    See Also
    --------
    :func:`networkx.betweenness_centrality`
    """
    if hasattr(G, "graph_object"):
        G = G.graph_object

    if k is None:
        nodes = G.nodes
    else:
        nodes = seed.sample(list(G.nodes), k)

    cpu_count = nxp.cpu_count(n_jobs)

    num_in_chunk = max(len(nodes) // cpu_count, 1)
    node_chunks = nxp.chunks(nodes, num_in_chunk)

    bt_cs = Parallel(n_jobs=cpu_count)(
        delayed(_betweenness_centrality_node_subset)(G, chunk, weight, endpoints,)
        for chunk in node_chunks
    )

    # Reducing partial solution
    bt_c = bt_cs[0]
    for bt in bt_cs[1:]:
        for n in bt:
            bt_c[n] += bt[n]

    betweenness = _rescale(
        bt_c,
        len(G),
        normalized=normalized,
        directed=G.is_directed(),
        k=k,
        endpoints=endpoints,
    )
    return betweenness


def _betweenness_centrality_node_subset(G, nodes, weight=None, endpoints=False):
    betweenness = dict.fromkeys(G, 0.0)
    for s in nodes:
        # single source shortest paths
        if weight is None:  # use BFS
            S, P, sigma, _ = _single_source_shortest_path_basic(G, s)
        else:  # use Dijkstra's algorithm
            S, P, sigma, _ = _single_source_dijkstra_path_basic(G, s, weight)
        # accumulation
        if endpoints:
            betweenness, delta = _accumulate_endpoints(betweenness, S, P, sigma, s)
        else:
            betweenness, delta = _accumulate_basic(betweenness, S, P, sigma, s)
    return betweenness
