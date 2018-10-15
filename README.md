[![Build Status](https://travis-ci.com/ptrstn/python-runregistryclient.svg?branch=master)](https://travis-ci.com/ptrstn/python-runregistryclient)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# python-runregistryclient
Implements a simple Python client that accesses the [RunRegistry](https://cmswbmoffshift.web.cern.ch/cmswbmoffshift/runregistry_offline/index.jsf) through the [resthub](http://valdasraps.github.io/resthub/) interface.

## Install instructions
```bash
pip install git+https://github.com/ptrstn/python-runregistryclient.git
```

## Example usage

```python
from runregistry.client import RunRegistryClient

client = RunRegistryClient()
query = "select r.runnumber from runreg_global.runs r " \
        "where r.run_class_name = 'Collisions15'" \
        "and r.runnumber > 247070 and r.runnumber < 247081"
client.execute_query(query)
```
Output:
```python
{'data': [[247073], [247076], [247077], [247078], [247079]]}
```

## Command line interface
After installing the package, the *runreg* cli script is available.

### Help
```bash
runreg --help
```

```
usage: runreg [-h] [-i] [-q query] [-f {text,xml,json,json2,csv}]

Run Registry command line client.

optional arguments:
  -h, --help               show this help message and exit
  -i, --info               General information about the service
  -q query                 SQL query used to access the Run Registry.
  -f {xml,json,json2,csv}  Specify output format
```

### Example
```bash
runreg -q "select max(r.runnumber) as max_run from runreg_tracker.runs r where r.run_class_name = 'Collisions15'"
```

Output:
```csv
MAX_RUN
263757
```

## Retrieve lumi sections JSON
To retrieve lumi sections in a JSON format you can do the following:
```python
from runregistry.tracker.lumis import LumiSectionsRetriever
retriever = LumiSectionsRetriever()
retriever.get_json([321813, 323983])
```

Output:
```json
{"321813": [[20, 31], [32, 37], [38, 51], [52, 254], [255, 257], [258, 352], [353, 433]], "323983": [[1, 188]]}
```

This can be used as input for [brilcalc](https://cms-service-lumi.web.cern.ch/cms-service-lumi/brilwsdoc.html), to compute the integrated luminosity.
## Run tests
Make sure that you are within the CERN GPN.

```bash
python -m unittest
python -m doctest -v runregistry\client.py
python -m doctest -v runregistry\tracker\client.py
python -m doctest -v runregistry\tracker\lumis.py
```

## References
- https://github.com/valdasraps/resthub
- https://twiki.cern.ch/twiki/bin/viewauth/CMS/DqmRrApi
