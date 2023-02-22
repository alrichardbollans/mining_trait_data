The methods in `clean_by_tdwg_region.py` will remove gbif occurrence records based on WCVP distribution data.

To do this, you will need to use the `automatchnames`
library v1.0 (https://github.com/alrichardbollans/automatchnames) to
match names from gbif to the WCVP backbone.

Example:

```python
import pandas as pd
import clean_plant_occurrences as cpo

gbif_records = pd.read_csv('your_gbif_records.csv')
# kwargs to pass to `get_accepted_info_from_names_in_column`
name_matching_kwargs = {'family_column': 'Family'}
# To clean with both native and introduced regions
both = cpo.clean_occurrences_by_tdwg_regions(gbif_records,name_column = 'scientificName',
                                             clean_by='both',
                                             output_csv='final_occurrence_output.csv', **name_matching_kwargs)

# To clean with just native regions
native = cpo.clean_occurrences_by_tdwg_regions(gbif_records,name_column = 'scientificName',
                                               clean_by='native',
                                               output_csv='final_native_occurrence_output.csv',**name_matching_kwargs)
```
