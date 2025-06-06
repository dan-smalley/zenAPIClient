# -*- coding: utf-8 -*-

"""
Zenoss CMDBIntegrationNGRouter
"""

from zenossapi.routers import ZenossRouter
from zenossapi.routers.device import DeviceRouter
from zenossapi.apiclient import ZenossAPIClientError


class CmdbRouter(ZenossRouter):
    """
    Class for interacting with the Zenoss cmdb router
    """

    def __init__(self, url, headers, ssl_verify):
        super(CmdbRouter, self).__init__(url, headers, ssl_verify, 'CMDBIntegrationNGRouter', 'CMDBIntegrationNGRouter')
        self.uuid = None

    def __repr__(self):
        if self.uuid:
            identifier = self.uuid
        else:
            identifier = hex(id(self))

        return '<{0} object at {1}>'.format(
            type(self).__name__, identifier
        )

    def list_configs(self):
        """
        List all CMDB configurations

        Returns:
            list[dict]: List of dicts containing config data for each CMDB config

        """

        config_data = self._router_request(
            self._make_request_data(
                'getInfos'
            )
        )

        return config_data['data']

    def get_active_config(self):
        """
        Return object of the currently active config (Zenoss only allows one active config)
        (calls list_configs and returns only active config)

        Returns:
            dict: Dictionary of active config data  (if any)

        """

        config_data = self.list_configs()

        for config in config_data:
            if config['enabled'] is True:
                return config

        return None

    def get_stats(self):
        """
        Return stats for the currently active config (calls get_active_config and returns stats)

        Returns:
            dict: Dictionary of stats for currently active config (if any)

        """
        active_config = self.get_active_config()
        if active_config is None:
            return None
        stats = {
            'run_interval': active_config['runInterval'],
            'full_run_interval': active_config['fullRunInterval'],
            'next_run': active_config['nextRun'],
            'next_full_run': active_config['nextFullRun'],
            'last_run_started': active_config['lastRunStarted'],
            'last_run_finished': active_config['lastRunFinished'],
            'last_successful_run_finished': active_config['lastRunSuccessFinished']
        }

        return stats

    def do_cmdb_run(self, uid, type=""):
        """
        Schedules an immediate run of the specified type for the given UID.
        If type isn't given a regular run is performed.

        Args:
            uid (str): The UID of the CMDB configuration to run
            type (str): Type of CMDB sync job to schedule, not needed for regular, "Full" for full.

        Returns:
             none
        """
        cmdb_run_status = self._router_request(
            self._make_request_data(
                'doCMDBRun',
                dict(uid=uid, runType=type)
            )
        )

    def get_cmdb_fields(self, uid=None, name=None):
        """
        Return list of cmdb fields for the given uid or name
        Note: instantiantes a DeviceRouter object to get the uid for a device name

        Arguments:
            uid (str): UID of the cmdb config to get fields for
            name (str): Name of the cmdb config to get fields for

        Returns:
            list[dict]: List of dicts containing cmdb fields for the given uid or name

        """

        if uid is None and name is None:
            raise ValueError('Either uid or name must be specified')

        if uid is not None:
            pass
        elif name is not None:
            dr = DeviceRouter(self.api_url, self.api_headers, self.ssl_verify)
            uid = dr.get_device_uid_by_name(name)
            if uid is None:
                raise ZenossAPIClientError('Device with name {0} not found'.format(name))

        cmdb_fields_data = self._router_request(
            self._make_request_data(
                'getCmdbFields',
                dict(uid=uid)
            )
        )

        return cmdb_fields_data['data']
