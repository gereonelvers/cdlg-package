from setuptools import setup

setup(
    name='concept-drift-generation',
    version='0.0.2',
    packages=['conceptdrift', 'conceptdrift.drifts', 'conceptdrift.source'],
    install_requires=[
        'pm4py==2.2.13.1'
        'graphviz==0.17'
    ],
    url='',
    license='MIT',
    author='Justus Grimm',
    author_email='jgrimm98@gmx.de',
    description='Module for creating drifts in logs and randomly evolving a process tree to a new version.'
)
