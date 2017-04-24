import os

from setuptools import setup
from setuptools import find_packages

import dumbc


# Read long description of the package from README.md
dirname = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(dirname, 'README.md'), 'r') as f:
    long_description = f.read()

setup(name='dumbc',
      version=dumbc.VERSION,
      description='Simple static programming language',
      long_description=long_description,
      author='Vlad Zagorodniy',
      author_email='vladzzag@gmail.com',
      license='BSD',
      classifiers=[
          'Development Status :: 7 - Inactive',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Software Development :: Compilers',
          'Programming Language :: Python :: 3'
      ],
      packages=find_packages(dirname),
      keywords='compiler',
      install_requires=[],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      entry_points={
          'console_scripts': [
              'dumbc = dumbc.compiler:main'
          ]
      })
