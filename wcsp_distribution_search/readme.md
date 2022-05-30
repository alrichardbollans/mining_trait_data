The methods in `get_wcsp_dist_from_powo.py` will get distribution information for given taxa IDs.

This is quite a long process and it is hoped that in future this data will be made public through direct downloads.

Example for Apocynaceae, Rubiaceae records using the `automatchnames` package:

```python
import automatchnames
import wcsp_distribution_search as wds

distributions_csv = 'output.csv'
acc_taxa = automatchnames.get_all_taxa(families_of_interest=['Apocynaceae', 'Rubiaceae'], accepted=True,
                                       ranks=['Species', 'Subspecies', 'Variety'])
id_list = acc_taxa['kew_id'].to_list()
wds.search_powo_for_tdwg3_distributions(id_list, 'distributions_pkl.pkl')
wds.convert_pkl_to_df('distributions_pkl.pkl', distributions_csv)
```
