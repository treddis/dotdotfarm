# Change log
All notable changes to this project will be documented in this file.


## v1.7.1 - 2024-04-19
### Added
- Regex for filter parameters
- Proxy support
### Fixed
- output flood while stopping program (KeyboardInterrupt)
- some exceptions

## v1.6.0 - 2023-09-25
### Added
- Modified HTTP engine for mor instantly starting
- Added argument groups in help
- More readable output
### Fixed
- Fixed known files regex for proper PT validation
- Fixed delay between requests
- Fixed inconsistent callbacks working

## v1.5.2 - 2023-07-02
### Fixed
- fixed continuous requests after timeout/refused connection

## v1.5.1 - 2023-04-16
### Fixed
- fixed invalid timeout exception while connection to target is established.
- removed "--method" parameter because they are calculated automatically.
- fixed invalid regexp checking for known standard OS files.

## v1.5.0 - 2023-03-13
### Added
- detection mode as default for dotdotweb
- added delay parameter in CLI & http engine for slowing down requests speed
### Fixed
- error while printing files content

## v1.4.2 - 2023-03-13
### Added
- proper handling of timeout exceptions
### Fixed
- unused websocket library import
- notation of CLI parameters

## v1.4.1 - 2023-02-22
### Fixed
- entry point in setup.py
- valid structure of callbacks module

## v1.4.0 - 2023-02-18
### Added
- version via --version parameter
- version to README
- specifying of depth for generator
- specifying max depth of PT for generator
- preparations for callbacks
### Fixed
- typo in README & CHANGELOG

## v1.3.0 (BETA) - 2023-01-27
### Added
- testing of all available files for windows and linux by default, thus closing the limitation of OS type requirement
- added a default timeout of 60 seconds
### Fixed
- README typo
- project tree

## v1.2.0 (BETA) - 2023-01-23
### Added
- Features to README
- Fixed TQDM status bar
- Reading of files after succeeding the payload

## v1.1.0 (BETA) - 2023-01-22
### Added
- limitations of the tool to README
### Fixed
- typo in README

## v1.0.0 (BETA) - 2023-01-22
### Added
- support of setup.py
- project as package
- callbacks for requests

## v0.3.0 (ALPHA) - 2023-01-18
### Added
- support for attacks via HTTP headers
- status bar (tqdm) for monitoring results
- some results of working
### Fixed
- invalid handling of input for payloads generator

## v0.2.0 (ALPHA) - 2023-01-17
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
- added handlers for graceful shutdown of coroutines after receiving reset&timeout errors

## v0.1.1 (ALPHA) - 2023-01-16
### Fixed
- updating README

## v0.1.0 (ALPHA) - 2023-01-16
- initial commit
