from setuptools import setup


setup(
    name="super",
    version="0.1.0",
    url="https://github.com/chauffer/super",
    author="Simone Esposito",
    author_email="chaufnet@gmail.com",
    download_url="https://github.com/chauffer/super",
    description="Yet Another Yet Another Discord Bot    ",
    packages=["super"],
    entry_points={"console_scripts": "super=super:main"},
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
