from setuptools import setup, find_packages

setup(
    name="passman",
    version="0.1.0",
    description="Менеджер паролей с TUI-интерфейсом",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "python-gnupg>=0.5.0",
        "pyperclip>=1.8.2",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "windows": ["windows-curses"],
    },
    entry_points={
        "console_scripts": [
            "passman=passman.app:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Utilities",
        "Environment :: Console :: Curses",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
) 