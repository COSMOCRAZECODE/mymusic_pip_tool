from setuptools import setup, find_packages

setup(
    name="mymusic-dl-Rajthespaceman", 
    version="1.2.2",  # Bumped to 1.2.2 to resolve the PyPI 403/Conflict error
    author="Raj Gohel",
    author_email="rajgohel202004@gmail.com",
    description="A silent, professional CLI tool to download Spotify playlists using Exportify CSVs.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True, # Ensures non-python files are included
    install_requires=[
        'yt-dlp',
        'mutagen',
        'tqdm',
        'musicbrainzngs',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'music=mymusic.main:main', 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)