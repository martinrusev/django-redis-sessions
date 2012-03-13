from setuptools import setup, find_packages
from redis_sessions import __version__

setup(
    name='django-redis-sessions',
    version=__version__,
    description="Redis Session Backend For Django",
    long_description="",
    keywords='django, sessions,',
    author='Martin Rusev',
    author_email='martinmcloud@gmail.com',
    url='http://github.com/martinrusev/django-redis-sessions',
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['redis>=2.4.10'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
)
