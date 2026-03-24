from setuptools import setup, find_packages

setup(
    name="mymusic-dl-Rajthespaceman", 
    version="1.2.0",
    author="Raj Gohel",
    author_email="rajgohel202004@gmail.com",
    description="A silent, professional CLI tool to download Spotify playlists using Exportify CSVs.",
    # Explicitly using utf-8 prevents the 'charmap' error on Windows
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    # Pip automatically installs these if the user's environment is missing them
    install_requires=[
        'yt-dlp',
        'mutagen',
        'tqdm',
        'musicbrainzngs',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            # This allows you to run 'music' from any terminal
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