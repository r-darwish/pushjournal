from setuptools import setup, find_packages
import functools
import os

_in_same_dir = functools.partial(os.path.join, os.path.dirname(__file__))

try:
    from systemd import journal # pylint: disable=unused-import
except ImportError:
    raise Exception("Could not import systemd.journal. You should install python-systemd using your OS package manager")


with open(_in_same_dir("pushjournal", "__version__.py")) as version_file:
    exec(version_file.read())  # pylint: disable=W0122

install_requires = [
    "click",
    "logbook",
    "netifaces",
    "requests",
    "PyYAML"
]
setup(name="pushjournal",
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Intended Audience :: System Administrators",
          "Operating System :: POSIX :: Linux",
          "Topic :: System :: Monitoring",
      ],
      description="Get notified about important events via PushBullet",
      license="BSD",
      author="Roey Darwish Dror",
      author_email="roey.ghost@gmail.com",
      url="",
      version=__version__,  # pylint: disable=E0602
      packages=find_packages(exclude=["tests"]),
      install_requires=install_requires,
      entry_points=dict(
          console_scripts=[
              "pushjournal = pushjournal.main:main_entry_point",
          ]
      ),
)
