# perfSONAR Microdep 

**IMPORTANT**: This project is still very much under development and will currently not build nor run effortlessly. It is recommended to wait with installation and test until a release branch is ready (hopefully 5.1.0).

This project provides a collection of tools realizing the *perfSONAR Microdep analytic system*.
*PS Microdep* provides
  * A set of analytic scripts which detects events in background latency data-sets and traceroue data-sets
  * Analytic scripts which search for corralations between events and report new corrolated events
  * A map-basded web-gui which presents overview and details of events reported by analysis
  * Charts and a traceroute topology viewer supporting the map-gui in presenting data

## Project structure

During the ongoing migration fase for *PS Microdep* the `/dev` folder holds misc subprojects the *PS Microdep analytic system* 
inherets its components from, i.e. `/dev` holds the legacy Microdep development environment. 

Other folders hold scripts and files applied by the perfsonar version of the system, i.e. files included in builds for different distributions.
Note that these files are typically copies of files under `/dev`. Run `make resync` to ensure perfsonar version is in sync with legacy version. 

## Building

Appling *unibuild*
  * Ensure *docker* is installed: `sudo apt install docker-ce-cli docker-compose-plugin`
  * Fetch *unibuild* compose file: `wget -O docker-compose.yml https://raw.githubusercontent.com/perfsonar/unibuild/main/docker-envs/docker-compose.yml`
  * el9: `docker compose run el9 unibuild build`

Updated rpm packages should become available in `<package-name>/unibuild-work/products/` (e.g `microdep/unibuild-work/products/`)

## Installation

A set of packages composes the overal analytic system

  * **perfsonar-microdep**     : Root packages depending on other perfsonar-microdep packages 
  * **perfsonar-microdep-map** : Web based map-gui
  * **perfsonar-tracetree**    : Web based graphical traceroute viewer
  * **perfsonar-microdep-ana** : Realtime analytics for event discovery

Note that currently PS Microdep depends on **perfsonar-toolkit**, i.e. it needs to be installed on a server running the full toolkit suit.

RPM-based distibutions
  * el7 (centos): `sudo yum install perfsonar-microdep` **NOT YET AVAILABLE**
  * el8, el9 (almalinux): `sudo dnf install perfsonar-microdep`
 
DEB-based distributions (Debian, Ubuntu) **NOT YET AVAILABLE**
  * `sudo apt install perfsonar-microdep`
  
From source **NOT YET AVAIABLE**
  * `tar zxvf perfsonar-microdep-xxx.yyy.zz.tar.gz`
  * `cd perfsonar-microdep`
  * `./configure`
  * `sudo make install`
  
  
  
