from setuptools import setup, find_packages

setup(
    name='django_redis_sessions',
    version='0.2.0',
    description="Redis Session Backend For Django",
    long_description="",
    keywords='django, sessions,',
    author='Chris Jones',
    author_email='chris@brack3t.com',
    url='https://github.com/chrisjones-brack3t/django-redis-sessions',
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
