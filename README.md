# quakexplore

Earthquake data exploration tool (in development)

Data sources:

- [U.S. Geological Survey (USGS)](https://earthquake.usgs.gov/earthquakes/feed/)
  - https://earthquake.usgs.gov/fdsnws/event/1/
  - https://earthquake.usgs.gov/data/comcat/index.php
- [European-Mediterranean Seismological Centre (EMSC)](https://www.emsc-csem.org/Earthquake_data/Data_queries.php)
- [GEOFON (GFZ German Research Center for Geosciences)](https://geofon.gfz-potsdam.de/eqinfo/)
- [Kövesligethy Radó Seismological Observatory (Institute of Earth Physics and Space Science, Eötvös Loránd Research Network)](http://www.seismology.hu/index.php/hu/)

GEOJson data format:

- https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
- https://geojson.org/
- https://geojson.io/#map=5.76/46.624/19.405

The [icons](https://store.kde.org/p/2068651) used in the project are open source.

## howto

### installation

The project is developed on Manjaro Linux, so any Linux distribution with [Python 3+](https://docs.python.org/3/using/index.html) and [Qt6](https://doc.qt.io/qt-6/get-and-install-qt.html) installed with the required dependencies should suffice. You can install these from the package manager.

The code should *somewhat* work on Windows as well, you can find installation guides through the links above.

You will need the [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) python package manager to set up the requiered packages ([pyside6](https://pypi.org/project/PySide6/), [requests](https://pypi.org/project/requests/)):

`pip install pyside6 requests`

Set the starting script to executable:

`chmod +x start.sh`

Additionally, if you want to stay up-to-date or participate in the development, you will need [git](https://git-scm.com/downloads) and clone the repo:

`git clone https://github.com/strugamano/quakexplore.git`

### usage

`./start.sh`

## todo

### earthquakes v0.1

- details
  - ids, sources: button opens a treeview
  - add remaining items
  - not implemented: tz, detail, tsunami?, code, types
- toolbar
  - about
- tweak status bar >> dValue class added: emits signal when variable value is changed
- spacer class?
- update readme, howto
- bash script to install/run
- future functions: location filter (coordinates, map), different data sources, quakeml-geojson integration
