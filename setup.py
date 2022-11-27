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
                                    'read_pdfs', 'powo_searches',
                                    'unit_test_methods',
                                    'wcsp_distribution_search',
                                    'wikipedia_searches']),

    package_data={
        "clean_plant_occurrences": ["inputs/wgsrpd-master/level3/*.shp"],
        "metabolite_searches": ["inputs/*"]
    },
    install_requires=[
        "automatchnames == 1.0",
        "pandas==1.4.1",
        "numpy~=1.22.1",
        "typing~=3.7.4.3",
        "requests~=2.27.1",
        "Wikipedia-API~=0.5.4",
        "tqdm~=4.62.3",
        "pykew~=0.1.3",
        "beautifulsoup4~=4.10.0",
        "tika~=1.24",
        "html5lib~=1.1",
    ],
    # *strongly* suggested for sharing
    version='1.0',
    license='MIT',
    description='A set of python packages for mining plant trait data',
    long_description=open('README.md').read(),
)
