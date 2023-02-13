from setuptools import setup, find_packages

# To install run pip install PATH_TO_PACKAGE

setup(
    name='miningtraitdata',
    url='https://github.com/alrichardbollans/mining_trait_data',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(include=['clean_plant_occurrences', 'data_compilation_methods',
                                    'conservation_priorities', 'knapsack_searches',
                                    'powo_searches',
                                    'wikipedia_searches'], exclude=['unit_test_methods']),

    package_data={
        "clean_plant_occurrences": ["inputs/wgsrpd-master/level3/*.shp"],
        "knapsack_metabolite_properties": ["inputs/*"]
    },
    install_requires=[
        "automatchnames == 1.0",
        "pandas==1.5.3",
        "numpy~=1.22.1",
        "typing~=3.7.4.3",
        "requests~=2.27.1",
        "Wikipedia-API==0.5.8",
        "tqdm~=4.62.3",
        "pykew==0.1.3",
        "beautifulsoup4~=4.10.0",
        "tika~=2.6.0",
        "html5lib~=1.1",
        "lxml",
        "sre_yield",
        "html5lib",
        'openpyxl'
    ],
    # *strongly* suggested for sharing
    version='1.0',
    license='MIT',
    description='A set of python packages for mining plant trait data',
    long_description=open('README.md').read(),
)
