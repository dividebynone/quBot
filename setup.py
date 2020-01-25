from setuptools import setup
from main import version

requirements = []
with open('requirements.txt') as reqs_file:
    requirements = reqs_file.read().splitlines()

readme = ''
with open('README.md') as readme_file:
    readme = readme_file.read()

setup(name='quBot',
      author='martin-r-georgiev',
      url='https://github.com/martin-r-georgiev/quBot',
      description='General-purpose Discord bot written in Python',
      long_description=readme,
      long_description_content_type="text/markdown",
      version=version,
      license='MIT',
      include_package_data=True,
      install_requires=requirements,
      python_requires='>=3.7.6',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
      ]
)