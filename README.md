GimVičUrnik
===========

A system for a school timetable, substitutions and menus at Gimnazija Vič.

## Description

This repository contains a system for a Progressive Web App to show the timetable, substitutions, menus and lunch schedules for students and teachers at Gimnazija Vič.

It uses Python API built with Flask and SQLAlchemy to download and parse the data from the official sources (e-classroom, website) using pdf2docx and bs4. The website is built using Vue.js framework and Vuetify theme. The source code can be found in [`API`](API) and [`website`](website) subdirectories.

The website is currently deployed at [gimvicurnik.filips.si](https://gimvicurnik.filips.si).

**Warning:** This project is unofficial and may contain incomplete or incorrect information. To view the official data, use the official e-classroom of Gimnazija Vič.

## Usage

See the READMEs of the API and the website for more details and instructions how to set up them:

* [Python API](API/README.md)
* [JavaScript website](website/README.md)

## Versioning

The project uses [SemVer](https://semver.org/) for versioning. For the available versions and the changelog, see [the releases](https://github.com/filips123/GimVicUrnik/releases) on this repository.

The API and website at released tags are compatible with each other according to SemVer. The API and the website at non-tagged commits may *not* be compatible with each other, because it is possible that not both of them were updated at the same time.

## License

This project is licensed under the GPLv3+ license. See the [LICENSE](LICENSE) file for details.
