from setuptools import setup  # , find_packages
import os


def read(*names):
    values = dict()
    for name in names:
        if os.path.isfile(name):
            value = open(name).read()
        else:
            value = ''
        values[name] = value
    return values

long_description = """

%(README)s

""" % read('README')

setup(name='tunneled_notify_service',
      version='1.0',
      description="Tunneled notification service",
      long_description=long_description,
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Bernard `Guyzmo` Pratz',
      author_email='guyzmo@m0g.net',
      url='http://i.got.nothing.to/blog',
      license='WTFPL',
      #packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=[
          'argparse',
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      notify_service_listener = tunneled_notify_service:start
      """,
      )
