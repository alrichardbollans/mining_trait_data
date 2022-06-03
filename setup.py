from setuptools import setup, find_packages

# To install run pip install PATH_TO_PACKAGE

setup(
    name='miningtraitdata',
    url='https://github.com/alrichardbollans/mining_trait_data',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(include=['clean_plant_occurrences', 'cleaning',
                                    'conservation_priorities', 'metabolite_searches',
                                    'read_pdfs', 'powo_searches', 'soilgrid_searches',
                                    'unit_test_methods',
                                    'wcsp_distribution_search',
                                    'wikipedia_searches']),

    package_data={
        "clean_plant_occurrences": ["inputs/wgsrpd-master/level3/*.shp"],
        "metabolite_searches": ["inputs/*"]
    },
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='A set of python packages for mining plant trait data',
    long_description=open('README.md').read(),
)
