from setuptools import setup
import os
import sys


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

setup(name='notossh',
      version='1.0',
      description="NOTifications Over SSH",
      long_description=long_description,
      classifiers=["Environment :: Console",
                   "Topic :: Communications :: Chat :: Internet Relay Chat",
                   "Environment :: MacOS X",
                   "Environment :: X11 Applications",
                   "Topic :: Text Editors :: Emacs"],
      keywords='ssh irc notifications growl libnotify irssi erc daemon',
      author='Bernard `Guyzmo` Pratz',
      author_email='notossh@m0g.net',
      url='http://m0g.net/notossh/',
      license='WTFPL',
      packages=['notossh'],
      zip_safe=False,
      install_requires=[
          'argparse',
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      notossh = notossh.notossh:start
      """,
      )

if "install" in sys.argv:
    print """
Notossh is now installed!
You can configure how you want to connect to your IRC service:

cat >> ~/.ssh/config <EOF
    Host HOST
    PermitLocalCommand yes
    LocalCommand /path/to/bin/notossh
    RemoteForward PORT localhost:PORT
EOF

or simply notossh --help

"""
