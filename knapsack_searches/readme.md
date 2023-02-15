The methods in `knapsack_search.py` allow for finding phytochemmical information from KNApSAcK.

Example to get data for a given taxon:

```python
from knapsack_searches import get_metabolites_for_taxon

# To get the metabolite data for a specific taxon
# Note that this is greedy as name matches in Knapsack search include partial e.g. Cissus matches Narcissus
data_table = get_metabolites_for_taxon('Cinchona officianalis')
```

Example for all data in given families in Apocynaceae, Rubiaceae:

```python
from knapsack_searches import get_metabolites_in_family

# Temp output is optional and provides the downloaded data prior to name matching and cleaning
get_metabolites_in_family('Apocynaceae',
                          'temp_output.csv',
                          'final_output.csv')

```
