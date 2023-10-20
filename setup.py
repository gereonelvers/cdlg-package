from setuptools import setup

setup(
    name='cdlg-package',
    version='0.0.2',
    packages=['conceptdrift', 'conceptdrift.drifts', 'conceptdrift.source'],
    install_requires=[
        'pm4py>=2.2.13.1',
        'graphviz>=0.17'
    ],
    url='',
    license='GPL 3.0',
    author='Justus Grimm',
    author_email='jugrimm@mail.uni-mannheim.de',
    description='Module for creating drifts in logs and randomly evolving a process tree to a new version.'
)
