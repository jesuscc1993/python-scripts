from setuptools import setup, find_packages

setup(
  name='mtsound',
  version='1.0.0',
  packages=find_packages(),
  description='A minimal sound package',
  author='jesuscc1993',
  install_requires=[
    'scipy',
    'simpleaudio',
  ],
)
