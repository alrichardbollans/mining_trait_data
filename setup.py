from setuptools import setup, find_packages

setup(
    name='miningtraitdata',
    url='https://github.com/alrichardbollans/mining_trait_data',
    author='Adam Richard-Bollans',
    author_email='adamrb@protonmail.com',
    # Needed to actually package something
    packages=find_packages(include=['wikipedia_searches', 'alkaloid_vars', 'common_name_vars',
                                    'knapsack_search', 'medicinal_usage_vars', 'morphological_vars',
                                    'name_matching_cleaning', 'poison_vars', 'powo_searches']),
    # Needed for dependencies
    install_requires=['requests', 'pandas', 'typing', 'Wikipedia-API'],
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='A set of python packages for mining plant trait data',
    long_description=open('README.md').read(),
)
