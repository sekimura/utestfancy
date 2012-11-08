try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="utestfancy",
    version="0.0.1",
    author="Masayoshi Sekimura",
    author_email="sekimura@gmail.com",
    url="http://github.com/sekimura/utestfancy",
    description="Fancy unitetest suite runner",
    packages=['utestfancy'],
)
