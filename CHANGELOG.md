# Change log
All notable changes to this project will be documented in this file

## [[1.0.0] - 2023-01-22] ALPHA
## Added
- support of setup.py
- project as package
- callbacks for requests

## [[0.3.0] - 2023-01-18] BETA
### Added
- support for attacks via HTTP headers
- status bar (tqdm) for monitoring results
- some results of working
### Fixed
- invalid handling of input for payloads generator

## [[0.2.0] - 2023-01-17] BETA
### Added
- first view of project structure
- TODO comments
- moved payloads generator to module
- first logics of payloads generator
- engines module (empty)
- setup.py
- more informative output
- acceleration via increasing of available simultaneous TCP connections
### Fixed
- added handlers for graceful shutdown of coroutins after receiving reset&timeout errors

## [[0.1.1] - 2023-01-16] BETA
### Fixed
- updating README

## [[0.1.0] - 2023-01-16] BETA
- initial commit