from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='Climind',
    url='https://github.com/jjk-code-otter/climate-indicator-manager',
    author='John Kennedy',
    author_email='jjk.code.otter@gmail.com',
    # Needed to actually package something
    packages=['climind'],
    # Needed for dependencies
    install_requires=['pytest', 'numpy', 'requests', 'beautifulsoup4',
                      'pandas', 'jsonschema', 'matplotlib', 'seaborn', 'xarray'],
    # version number
    version='0.1',
    # The license can be anything you like
    license='GNU General Public License v3.0',
    description='A python package for managing climate indicator information',
    # We will also need a readme eventually (there will be a warning)
    long_description=open('README.md').read(),
)