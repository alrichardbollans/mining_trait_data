from setuptools import setup, find_packages

setup(
    name='miningtraitdata',
    url='https://github.com/alrichardbollans/mining_trait_data',
    author='Adam Richard-Bollans',
    author_email='38588335+alrichardbollans@users.noreply.github.com',
    # Needed to actually package something
    packages=find_packages(include=['clean_plant_occurrences', 'data_compilation_methods',
                                    'knapsack_searches', 'metabolite_properties',
                                    'powo_searches',
                                    'wikipedia_searches'], exclude=['unit_test_methods']),

    package_data={
        "clean_plant_occurrences": ["inputs/wgsrpd-master/level3/*.shp"],
        "metabolite_properties": ["inputs/*"],
        "knapsack_searches": ["inputs/*"]
    },
    install_requires=[
        "automatchnames == 1.2.1",
        'openpyxl'
    ],
    extras_require={
        'powo': ["pykew"],
        'wiki': ["Wikipedia-API"],
        'knapsack': ["html5lib"]
    },
    # *strongly* suggested for sharing
    version='1.0',
    description='A set of python packages for mining plant trait data',
    long_description=open('README.md').read(),
)
