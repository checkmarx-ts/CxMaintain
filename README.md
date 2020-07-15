# CxMaintain
Checkmarx Data Retention Helper:


## Purpose

--- 

# Getting Started

## Wiki
- To get started, Please visit the [wiki](https://github.com/checkmarx-ts/CxMaintain/wiki/home). 

- For `Installation instructions` Please Visit [this section](https://github.com/checkmarx-ts/CxMaintain/wiki/Installation) in the Wiki.


## Docker
- At this stage, Dockerfile is for testing changes in code quickly.
- This Dockerfile can be extended to run `CxMaintain` toolkit, However, care must be taken to provide the yaml files.
- Please consider `fakeroot` if you use this dockerfile beyond testing code changes.
- Build command `docker build -t CxMaintain:0.0.1 path/to/dockerfile`.
- Run command `docker run -it CxMaintain`.
---
