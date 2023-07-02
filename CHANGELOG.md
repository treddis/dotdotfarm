# Change log
All notable changes to this project will be documented in this file

## [[1.5.2] - 2023-07-02]
### Fixed
- fixed continuous requests after timeout/refused connection

## [[1.5.1] - 2023-04-16]
### Fixed
- fixed invalid timeout exception while connection to target is established.
- removed "--method" parameter because they are calculated automatically.
- fixed invalid regexp checking for known standart OS files.

## [[1.5.0] - 2023-03-13]
### Added
- detection mode as default for dotdotweb
- added delay parameter in CLI & http engine for slowing down requests speed
### Fixed
- error while printing files content

## [[1.4.2] - 2023-03-13]
### Added
- proper handling of timeout exceptions
### Fixed
- unused websocket library import
- notation of CLI parameters

## [[1.4.1] - 2023-02-22]
### Fixed
- entry point in setup.py
- valid structure of callbacks module

## [[1.4.0] - 2023-02-18]
### Added
- version via --version parameter
- version to README
- specifying of depth for generator
- specifying max depth of PT for generator
- preparations for callbacks
### Fixed
- typo in README & CHANGELOG

## [[1.3.0] - 2023-01-27] BETA
### Added
- testing of all available files for windows and linux by default, thus closing the limitation of OS type requirement
- added a default timeout of 60 seconds
### Fixed
- README typo
- project tree

## [[1.2.0] - 2023-01-23] BETA
### Added
- Features to README
- Fixed TQDM status bar
- Reading of files after succeeding the payload

## [[1.1.0] - 2023-01-22] BETA
### Added
- limitations of the tool to README
### Fixed
- typo in README

## [[1.0.0] - 2023-01-22] BETA
### Added
- support of setup.py
- project as package
- callbacks for requests

## [[0.3.0] - 2023-01-18] ALPHA
### Added
- support for attacks via HTTP headers
- status bar (tqdm) for monitoring results
- some results of working
### Fixed
- invalid handling of input for payloads generator

## [[0.2.0] - 2023-01-17] ALPHA
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

## [[0.1.1] - 2023-01-16] ALPHA
### Fixed
- updating README

## [[0.1.0] - 2023-01-16] ALPHA
- initial commit
