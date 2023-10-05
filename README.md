# Python packages for gathering trait data

## Disclaimer

WARNING: The information contained herein is provided as a public service with the understanding that authors make no
warranties, either expressed or implied, concerning the accuracy, completeness, reliability, or suitability of the
information.

In particular, concerning lists of poisonous/toxic plants --- just because a plant is not on the list *DOES NOT* mean
that it is not dangerous/poisonous/toxic. Similarly, concerning lists of non_poisonous plants --- just because a plant
is on the list *DOES NOT* mean that it is not dangerous/poisonous/toxic.

## Installation

Run:
`pip install git+https://github.com/alrichardbollans/mining_trait_data.git@XX`

### Requirements

Given in requirements.txt

## Notes on Data in Repository

Data archived here is collected for the purposes of a particular study and as a result some variables are specific to
particular ranks and families. However, the methods can be used for various ranks and taxa (with the exception of
methods that rely on a downloaded copy of a specific dataset which is restricted by taxa and rank).

## Sources

See `cite.txt` file in each package for lists of sources.

## Naming

Names from different datasets are matched using the automatchnames
package (https://github.com/alrichardbollans/automatchnames)