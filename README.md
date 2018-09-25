# python-runregistryclient
Implements a simple Python client that accesses the [RunRegistry](https://cmswbmoffshift.web.cern.ch/cmswbmoffshift/runregistry_offline/index.jsf) through the [resthub](http://valdasraps.github.io/resthub/) interface.

## Install instructions
```
pip install git+https://github.com/ptrstn/python-runregistryclient.git
```

## Example Usage

```python
from runregistryclient.RunRegistryClient import RunRegistryClient

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

## References
- https://github.com/valdasraps/resthub
- https://twiki.cern.ch/twiki/bin/viewauth/CMS/DqmRrApi
