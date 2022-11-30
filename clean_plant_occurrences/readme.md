The methods in `clean_by_tdwg_region.py` will remove gbif occurrence records based on WCVP distribution data.

To do this, you will need to use the `automatchnames`
library v1.0 (https://github.com/alrichardbollans/automatchnames) to
match names from gbif to the WCVP backbone.

Example for Apocynaceae, Rubiaceae records:

```python
import pandas as pd
import clean_plant_occurrences as cpo

# Names of families in your occurrence records
families_in_occurrences = ['Apocynaceae', 'Rubiaceae']

gbif_records = pd.read_csv('your_gbif_records.csv')
occurrences_with_accepted_information = cpo.read_occurences_and_output_acc_names(gbif_records,
                                                                                 'output_file_for_accepted_info.csv',
                                                                                 families_in_occurrences=families_in_occurrences)
# To clean with both native and introduced regions
both = cpo.clean_occurrences_by_tdwg_regions(occurrences_with_accepted_information,
                                             clean_by='both',
                                             output_csv='final_occurrence_output.csv')

# To clean with just native regions
native = cpo.clean_occurrences_by_tdwg_regions(occurrences_with_accepted_information,
                                               clean_by='native',
                                               output_csv='final_native_occurrence_output.csv')
```
