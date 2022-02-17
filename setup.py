from setuptools import setup, find_packages

# To install run pip install -e PATH_TO_PACKAGE

setup(
    name='miningtraitdata',
    url='https://github.com/alrichardbollans/mining_trait_data',
    author='Adam Richard-Bollans',
    author_email='adamrb@protonmail.com',
    # Needed to actually package something
    packages=find_packages(include=['alkaloid_vars', 'common_name_vars',
                                    'medicinal_usage_vars', 'morphological_vars',
                                    'cleaning', 'poison_vars', 'powo_searches''wikipedia_searches',
                                    'wikipedia_vars']),
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='A set of python packages for mining plant trait data',
    long_description=open('README.md').read(),
)
