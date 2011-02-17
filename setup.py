from setuptools import setup

setup(
    name='redis-import-tools',
    version='0.1',
    long_description=__doc__,
    packages=['redis_import_tools'],
    include_package_data=True,
    zip_safe=False,
    #install_requires=['redis==2.2.0'],
    scripts=['bin/redis-import-set']
)
