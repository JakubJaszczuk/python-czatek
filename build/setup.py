from distutils.core import setup
from mypyc.build import mypycify

setup(name='mypyc_output',
      ext_modules=mypycify(['src/client.py'], opt_level="3"),
)
