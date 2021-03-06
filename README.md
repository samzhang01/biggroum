# BigGroum

BigGroum is a programming pattern-mining tool for finding patterns conserved across corpora consisting of hundreds or even thousands of projects.

Frameworks like Android expose rich functionality through a complex, object-oriented application-programming interface (API). How to properly use API methods is rarely fully documented and so app developers may guess incorrectly. BigGroum reifies in a mining tool the intuitive approach of looking for examples of how others use the API. The underlying assumption is that a “popular” way of using the API probably works, and code that is slightly off from a popular pattern is suspicious. To accurately capture API usage patterns, BigGroum mines graph-based object usage models (groums) that simultaneously describe control flow and data dependencies between methods of
multiple interacting object types.

This repository contains code for extracting groums from Android apps and then performs the mining task.

## Subprojects

The extraction of the Groums and the implementation of the mining
algorithm is implemented in the FixrGraphExtractor and FixrGraphIso
submodules.

`git submodule update --init --recursive --remote`


## Installation and dependencies

1. Follow the README files in the `FixrGraphExtractor` and `FixrGraphIso` to check the required dependencies of both tools.


To build the `FixrGraphExtractor`:
```
$> cd FixrGraphExtractor
$> sbt oneJar
```

To build `FixrGraphIso`:
```
$> cd FixrGraphIso
$> mkdir build
$> cd build
$> cmake ../ -DFIXR_GRAPH_EXTRACTOR_DIRECTORY=../../FixrGraphExtractor
$> make
```


2. Install the following dependencies to use the automated scripts to run the graph extraction and graph mining computation:
- python 2.7
- enum34 python package (`pip install enum34`)
- protobuf (`pip install protobuf`)
- sql_alchemy for python


- android SDK
Remember to set the android SDK home

3. Generate the protobuffer bindings for python

```
protoc -I=./FixrGraphExtractor/src/main/protobuf --python_out=./python/fixrgraph/annotator/protobuf ./FixrGraphExtractor/src/main/protobuf/proto_acdfg.proto 
protoc -I=./FixrGraphExtractor/src/main/protobuf --python_out=./python/fixrgraph/annotator/protobuf ./FixrGraphExtractor/src/main/protobuf/proto_iso.proto
protoc -I=./FixrGraphIso/src/fixrgraphiso/protobuf:./FixrGraphExtractor/src/main/protobuf --python_out=./python/fixrgraph/annotator/protobuf ./FixrGraphIso/src/fixrgraphiso/protobuf/proto_acdfg_bin.proto ./FixrGraphIso/src/fixrgraphiso/protobuf/proto_unweighted_iso.proto ./FixrGraphIso/src/fixrgraphiso/protobuf/proto_search.proto
```

4. Set the `PYTHONPATH` variable to include the package

```
export PYTHONPATH=`pwd`""/python:$PYTHONPATH
```

4. To test if your environment is set-up correctly, you can run the tests.
```
$> cd python/fixrgraph/test
$> nosetests
```

You need to have `nose` installed on your system to run the tests automatically. It can be installed using `pip` via `pip install nose`




## Run the Groum extraction and mining process

You need to include the python package in your `PYTHON_PATH`.
You can execute the following command from the repository path:
```
repo_path=`pwd`
export PYTHONPATH="${repo_path}/python":${PYTHONPATH}
```



### Set-up the extraction step:

The file `scripts/sample_setup/config.txt` shows an example of parameters that can be used to setup the extraction and mining process.

Note that the file paths in the configiration file must be absolute or relative to the path where the script is executed.

#### Setting for the extraction `[extraction]` section in the configuration file

- repo_list:
Path to a json file containing the name of the github repository that must be processed (see the file `scripts/sample_setup/repo_list.json`)

- buildable_list:
Path to a json file describing where the github repositories have been already built.

See the file `buildable_small.json` file to see the information that must be provided.

- build_data:
Path to the directory that contains the built repositories.

Each repository must be built in a folder called `<github-username>/<github-repo-name>/<github-commit-hash>`.

- out_path:
Output directory for all the produced data (you have to create the folder `out` under `scripts/sample_setup` it to run the tool on the example setup).


#### Setting for the itemset computation `[itemset]` section in the configuration file

- frequency_cutoff:
The minimum frequency of an itemset (i.e., number of groums that support that itemset) that will be considered by the itemset computation.

- min_methods_in_itemset
The minimum number of methods that an itemset must have


#### Setting for the pattern `[pattern]` section in the configuration file

- timeout
The timeout (in seconds) for the computation of the patterns of a single cluster

- frequency_cutoff
The minimum frequency (number of groums) that a pattern must have to be considered frequent.


### Run the whole process
```
$> cd scripts/sample_setup
$> python run_mining.py -c config.txt
```


## Inspect the patterns generated by BigGroum
BigGroum generates an html representation of the mined pattern in `scripts/sample_setup/out/clusters/html_files/index.html`.
The page contains a list of clusters (itemsets of Groums generated by the tool), reporting for each of them the set of method names included in the itemset computation and a link to a page summarizing the results (i.e., the patterns) computed for each cluster.
The list is ordered by "Cluster ID", so the first element is the cluster with ID 1, ...

A cluster page (e.g., `scripts/sample_setup/out/clusters/html_files/cluster_2.html`) first reports the id of the cluster (e.g., `Cluster 2`) and the list of methods contained in the frequent itemset corresponding to the cluster.
Then, the cluster page reports in order the list of popular patterns, the list of anomalous patterns, and the list of isolated patterns (i.e., the page reports a list of patterns ordered first by pattern category and then by pattern ID).

For each single pattern the page shows:
- A label containing: the clategory of the pattern (popular, anomalous, isolated), the id of the pattern and its frequency
- An image of the pattern:
the image shows the groum representation of the pattern where each square, gray node is a method node, each rounded, red circled node is a data node, each black edge is a control node, each blue edge is a def node, and each green edge is a use edge.
- A list of groums (i.e., app specific methods) that contains the pattern. Each element in the list report the full name of the class containing the method, and the method name. Furthermore, each element in the list contains a link to the provenance page describing the groum.



## References and experiments

The techniques implemented by the tool are described in the paper:
```
Mining Framework Usage Graphs from App Corpora,
Sergio Mover, Sriram Sankaranarayanan, Rhys Braginton Pettee Olsen, Bor-Yuh Evan Chang,
IEEE International Conference on Software Analysis, Evolution and Reengineering, 2018
```

A copy of a pre-print of the paper is available in the doc folder.

In the paper we used the `BigGroum` tool to extract and mine patterns from 500 Android applications. The results are available here: https://goo.gl/r1VAgc


