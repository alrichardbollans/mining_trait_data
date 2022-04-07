# Python packages for gathering trait data

Still under construction. Some datasets are not yet included until publishing rights have been clarified.

In general, useful methods which are frequently used have been split into separate packages (e.g. `powo_searches`) and
found variables are stored in packages with the `_var` suffix. Currently the data is generally focussed on species in
Apocynaceae and Rubiaceae though I plan to make the methods more general if it becomes useful for anyone.

## Disclaimer

WARNING: The information contained herein is provided as a public service with the understanding that authors make no
warranties, either expressed or implied, concerning the accuracy, completeness, reliability, or suitability of the
information.

In particular, concerning lists of poisonous/toxic plants --- just because a plant is not on the list *DOES NOT* mean
that it is not dangerous/poisonous/toxic. Similarly, concerning lists of non_poisonous plants --- just because a plant
is on the list *DOES NOT* mean that it is not dangerous/poisonous/toxic.

## Installation

Run:
`pip install git+https://github.com/alrichardbollans/mining_trait_data.git#egg=mining_trait_data`

### Requirements

Given in requirements.txt

## Notes on Data in Repository

Data archived here is collected for the purposes of a particular study and as a result some variables are specific to
particular ranks and families. However, the methods can be used for various ranks and taxa (with the exception of
methods that rely on a downloaded copy of a specific dataset which is restricted by taxa and rank).

## Sources

See `cite.txt` file in each package for lists of sources.