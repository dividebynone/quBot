from setuptools import setup
import json

requirements = []
with open('requirements.txt') as reqs_file:
    requirements = reqs_file.read().splitlines()

readme = ''
with open('README.md') as readme_file:
    readme = readme_file.read()

required_extras = {
    'docs': [
        'alabaster==0.7.12',
        'sphinx==2.3.1',
    ]
}

with open('./data/data.json', 'r') as json_file:
    json_data = json.load(json_file)
json_file.close()

version = json_data["appVersion"]

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
      extras_require=required_extras,
      python_requires='>=3.7.3',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
      ]
)