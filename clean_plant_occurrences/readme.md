The methods in `clean_by_tdwg_region.py` will remove gbif occurrence records based on WCSP distribution data.

To do this, you will need to use the `automatchnames` package (https://github.com/alrichardbollans/automatchnames) to
match names from gbif to the WCVP backbone.

You will also need to get distribution data using the `wscp_distribution_search` package in this library.

Example for Apocynaceae, Rubiaceae records:
```python
import pandas as pd
import clean_plant_occurrences as cpo
# Names of families in your occurrence records
families_in_occurrences =['Apocynaceae', 'Rubiaceae']

distributions_csv = 'path_to_distribution_data.csv'

gbif_records = pd.read_csv('your_gbif_records.csv')
occurrences_with_accepted_information = cpo.read_occurences_and_output_acc_names(gbif_records, 'output_file_for_accepted_info.csv',
                                         families_in_occurrences=families_in_occurrences)
# To clean with both native and introduced regions
both = cpo.clean_occurrences_by_tdwg_regions(occurrences_with_accepted_information, distributions_csv, priority='both',
                                         output_csv=final_occurrence_output_csv)

# To clean with just native regions
native = cpo.clean_occurrences_by_tdwg_regions(occurrences_with_accepted_information, distributions_csv, priority='native',
                                           output_csv=final_native_occurrence_output_csv)
```
