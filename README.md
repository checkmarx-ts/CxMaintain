# CxMaintain
Checkmarx Data Retention Helper:


## Purpose

--- 

# Getting Started

## Wiki
- To get started, Please visit the [wiki](https://github.com/checkmarx-ts/CxMaintain/wiki). 

## Installation
To Install CxMaintain, Please follow the instructions here on [this page.](https://github.com/checkmarx-ts/CxMaintain/wiki/Installation)

## Usage Commands
```
Commands:
init            Create OR Reinitialize a configuration file to connect to Checkmarx cxsast v9.0
login           Authenticate user on Checkmarx
checktoken      Check token as unexpired. (Requires login --save to be used prior.)
retention       Check for CxSAST directories that can be deleted.
```

## Command Options
```
-s, --save               Save OAuth Token into configuration directory.
-h, --help               Help.
--delete                 Delete directories.
-v, --verbose            Display version of CxDir.
--days=days              Number of days to retain.
```

## The detection process.
Deletion process does not rely on `Microsoft Windows` `Directory date-modified` information as such detection is weak and cannot be helpful to determine locked-scan.

To know more, [Read information here.](https://github.com/checkmarx-ts/CxMaintain/wiki/Delete-detection)

## Docker
- At this stage, Dockerfile is for testing changes in code quickly.
- Please do not use it on a production machine.
---
