from setuptools import setup, find_packages

setup(
    name='django-redis-sessions',
    version='0.2.2',
    description="Redis Session Backend For Django",
    long_description="",
    keywords='django, sessions,',
    author='Martin Rusev',
    author_email='martinmcloud@gmail.com',
    url='http://github.com/martinrusev/django-redis-sessions',
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['setuptools','redis',],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
) 


