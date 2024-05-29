# Zenoss API Client

![Tests badge](https://github.com/dan-smalley/zenAPIClient/actions/workflows/test_and_lint.yml/badge.svg) 
[![Documentation Status](https://readthedocs.org/projects/zenapiclient/badge/?version=latest)](https://zenapiclient.readthedocs.io/en/latest/?badge=latest) 
[![Coverage Status](https://dan-smalley.github.io/zenAPIClient/coveragecoverage-badge.svg?dummy=8484744)](https://dan-smalley.github.io/zenAPIClient/index.html)
![PyPI - Version](https://img.shields.io/pypi/v/zenAPIClient?logo=pypi&label=PyPI)
![GitHub Release](https://img.shields.io/github/v/release/dan-smalley/zenAPIClient?include_prereleases&logo=github&label=Release)
![TestPyPI - Version](https://img.shields.io/pypi/v/zenAPIClient?pypiBaseUrl=https%3A%2F%2Ftest.pypi.org&logo=pypi&label=TestPyPI) 

> NOTE: This project is a fork of the excellent [ZenossAPIClient](https://github.com/Zuora-TechOps/ZenossAPIClient) by Zuora-TechOps and the [fork](https://github.com/boblickj/ZenossAPIClient) contributed by boblickj.
> 
>-dan-smalley

Python module for interacting with the Zenoss API in an object-oriented way.
Tested with Zenoss Cloud, no guarantees for earlier versions...

The philosophy here is to use objects to work with everything in the Zenoss API, and to try to normalize the various calls to the different routers.
Thus `get` methods will always return an object, `list` methods will return data.
All methods to add or create start with `add`, all remove or delete start with `delete`.
As much as possible the methods try to hide the idiosyncrasies of the JSON API, and to do the work for you, for example by letting you use a device name instead of having to provide the full device UID for every call.

## Installing

```
pip install zenAPIClient


## Using

In [1]: from zenossapi import apiclient as zapi

In [2]: zenoss_client = zapi.Client(host=zenurl, collection_zone='cz0', api_key=zenApiKey)
In [3]: device_router = zenoss_client.get_router('device')
In [4]: device_class = device_router.get_device_class('Server/SSH/Linux')
In [5]: my_server = device_class.get_device('my.server.example.com')
In [6]: remodel_job = my_server.remodel()
In [7]: print(remodel_job)
9ba5c8d7-58de-4f18-96fe-d362841910d3
```

Supports the Zenoss JobsRouter, DeviceRouter, TemplateRouter, EventsRouter, PropertiesRouter, MonitorRouter, CMDBRouter, and DeviceManagementRouter.
