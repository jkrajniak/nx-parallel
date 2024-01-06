## nx-parallel

nx-parallel is a NetworkX backend that uses joblib for parallelization. This project aims to provide parallelized implementations of various NetworkX functions to improve performance.

## Features

nx-parallel provides parallelized implementations for the following NetworkX functions:

- [betweeness_centrality](https://github.com/networkx/nx-parallel/blob/main/nx_parallel/algorithms/centrality/betweenness.py#L17)
- [local_efficiency](https://github.com/networkx/nx-parallel/blob/main/nx_parallel/algorithms/efficiency_measures.py#L12)
- [number_of_isolates](https://github.com/networkx/nx-parallel/blob/main/nx_parallel/algorithms/isolate.py#L9)
- [all_pairs_bellman_ford_path](https://github.com/networkx/nx-parallel/blob/main/nx_parallel/algorithms/shortest_paths/weighted.py#L9)
- [is_reachable](https://github.com/networkx/nx-parallel/blob/main/nx_parallel/algorithms/tournament.py#L11)
- [tournament_is_strongly_connected](https://github.com/networkx/nx-parallel/blob/main/nx_parallel/algorithms/tournament.py#L103)
- [closeness_vitality](https://github.com/networkx/nx-parallel/blob/main/nx_parallel/algorithms/vitality.py#L9)

![alt text](timing/heatmap_all_functions.png)

See the `/timing` folder for more heatmaps and code for heatmap generation!


### Development install

To setup a local development:

- Fork this repository.
- Clone the forked repository locally.
```
git clone git@github.com:<your_username>/networkx.git
```
- Create a fresh conda/mamba virtualenv and install the dependencies
```
pip install -e ".[developer]"
```
- Install pre-commit actions that will run the linters before making a commit
```
pre-commit install
```


## Usage

Here's an example of how to use nx-parallel:

```python
In [1]: import networkx as nx; import nx_parallel

In [2]: G = nx.path_graph(4)

In [3]: H = nx_parallel.ParallelGraph(G)

In [4]: nx.betweenness_centrality(H)
Out[4]: {0: 0.0, 1: 0.6666666666666666, 2: 0.6666666666666666, 3: 0.0}
```

## Testing

To run tests for the project, use the following command:

```
PYTHONPATH=. \
NETWORKX_GRAPH_CONVERT=parallel \
NETWORKX_TEST_BACKEND=parallel \
NETWORKX_FALLBACK_TO_NX=True \
    pytest --pyargs networkx "$@"
```

## Contributing

We'd love to have you contribute to nx-parallel! Here are some guidelines on how to do that:

- **Issues:** Feel free to open issues for any problems you face, or for new features you'd like to see implemented.
- **Pull requests:** If you'd like to implement a feature or fix a bug yourself, we'd be happy to review a pull request. Please make sure to explain the changes you made in the pull request description.

## Additional Information

This project is part of the larger NetworkX project. If you're interested in contributing to NetworkX, you can find more information in the [NetworkX contributing guidelines](https://github.com/networkx/networkx/blob/main/CONTRIBUTING.rst).
