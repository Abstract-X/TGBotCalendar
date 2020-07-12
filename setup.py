import setuptools
from pathlib import Path
import re


LIB_NAME = "tgbotcalendar"
WORK_DIR = Path(__file__).parent


def fetch_version() -> str:

    content = (WORK_DIR / LIB_NAME / "__init__.py").read_text(encoding="UTF-8")
    try:
        version_string = re.findall(r'__version__ = "\d+\.\d+\.\d+"', content)[0]
        version = version_string.rsplit(" ")[-1].replace('"', "")
        return version
    except IndexError:
        raise RuntimeError("version not found!")


setuptools.setup(
    name=LIB_NAME,
    version=fetch_version(),
    packages=setuptools.find_packages(exclude=("examples",)),
    url="https://github.com/Abstract-X/tgbotcalendar",
    license="MIT",
    author="Abstract-X",
    author_email="abstract-x-mail@protonmail.com",
    description="The most flexible of Telegram bots calendars.",
    include_package_data=False
)
