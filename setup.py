from distutils.core import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="begood-forms",
    version="0.2.0",
    description="",
    author="AGoodId",
    author_email="teknik@agoodid.com",
    maintainer="AGoodId",
    maintainer_email="teknik@agoodid.se",
    url="https://github.com/agoodid/begood-forms",
    license="MIT",
    packages=[
        "begood_forms",
        "begood_forms.templatetags",
    ],
    include_package_data=True,
    long_description=read("README.markdown"),
    install_requires=['django-datatrans', 'django-bootstrap3', 'sendgrid'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
)
