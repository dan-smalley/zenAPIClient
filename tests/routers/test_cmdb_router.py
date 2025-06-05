import pytest
from zenossapi.routers.cmdb import CmdbRouter
from zenossapi.apiclient import ZenossAPIClientError
from zenossapi.routers.device import DeviceRouter

class TestCmdbRouter:
    @pytest.fixture
    def cmdb_router(self):
        """Fixture to create a CmdbRouter instance"""
        url = "https://zenoss.example.com"
        headers = {"Content-Type": "application/json"}
        ssl_verify = True
        return CmdbRouter(url, headers, ssl_verify)

    def test_cmdb_router_init(self, cmdb_router):
        """Test CmdbRouter initialization"""
        assert cmdb_router.api_url == "https://zenoss.example.com"
        assert cmdb_router.api_headers == {"Content-Type": "application/json"}
        assert cmdb_router.ssl_verify is True
        assert cmdb_router.uuid is None

    def test_repr(self, cmdb_router):
        """Test string representation of CmdbRouter"""
        # Test without uuid
        assert repr(cmdb_router).startswith("<CmdbRouter object at 0x")
        
        # Test with uuid
        cmdb_router.uuid = "test-uuid"
        assert repr(cmdb_router) == "<CmdbRouter object at test-uuid>"

    @pytest.mark.parametrize("config_data,expected", [
        (
            {"data": [
                {"enabled": True, "config": "active"},
                {"enabled": False, "config": "inactive"}
            ]},
            {"enabled": True, "config": "active"}
        ),
        (
            {"data": [
                {"enabled": False, "config": "inactive1"},
                {"enabled": False, "config": "inactive2"}
            ]},
            None
        ),
    ])
    def test_get_active_config(self, cmdb_router, mocker, config_data, expected):
        """Test getting active configuration"""
        mocker.patch.object(cmdb_router, 'list_configs', return_value=config_data["data"])
        result = cmdb_router.get_active_config()
        assert result == expected

    def test_get_stats(self, cmdb_router, mocker):
        """Test getting stats for active configuration"""
        mock_config = {
            "runInterval": 3600,
            "fullRunInterval": 86400,
            "nextRun": "2025-01-01",
            "nextFullRun": "2025-01-02",
            "lastRunStarted": "2024-12-31",
            "lastRunFinished": "2024-12-31",
            "lastRunSuccessFinished": "2024-12-31",
            "enabled": True
        }
        mocker.patch.object(cmdb_router, 'get_active_config', return_value=mock_config)
        
        result = cmdb_router.get_stats()
        expected_stats = {
            'run_interval': 3600,
            'full_run_interval': 86400,
            'next_run': "2025-01-01",
            'next_full_run': "2025-01-02",
            'last_run_started': "2024-12-31",
            'last_run_finished': "2024-12-31",
            'last_successful_run_finished': ['lastRunSuccessFinished']
        }
        assert result == expected_stats

    def test_get_stats_no_active_config(self, cmdb_router, mocker):
        """Test getting stats when no active configuration exists"""
        mocker.patch.object(cmdb_router, 'get_active_config', return_value=None)
        assert cmdb_router.get_stats() is None

    @pytest.mark.parametrize("uid,run_type", [
        ("device/123", ""),
        ("device/456", "Full"),
    ])
    def test_do_cmdb_run(self, cmdb_router, mocker, uid, run_type):
        """Test scheduling CMDB runs"""
        mock_request = mocker.patch.object(cmdb_router, '_router_request')
        cmdb_router.do_cmdb_run(uid, run_type)
        mock_request.assert_called_once()

    def test_get_cmdb_fields_with_uid(self, cmdb_router, mocker):
        """Test getting CMDB fields using UID"""
        expected_data = {"data": [{"field1": "value1"}]}
        mock_request = mocker.patch.object(
            cmdb_router, '_router_request', return_value=expected_data
        )
        
        result = cmdb_router.get_cmdb_fields(uid="device/123")
        assert result == expected_data["data"]

    def test_get_cmdb_fields_with_name(self, cmdb_router, mocker):
        """Test getting CMDB fields using device name"""
        mock_device_router = mocker.Mock(spec=DeviceRouter)
        mock_device_router.get_device_uid_by_name.return_value = "device/123"
        mocker.patch('zenossapi.routers.device.DeviceRouter', return_value=mock_device_router)
        
        expected_data = {"data": [{"field1": "value1"}]}
        mocker.patch.object(cmdb_router, '_router_request', return_value=expected_data)
        
        result = cmdb_router.get_cmdb_fields(name="test-device")
        assert result == expected_data["data"]

    def test_get_cmdb_fields_invalid_device_name(self, cmdb_router, mocker):
        """Test getting CMDB fields with invalid device name"""
        mock_device_router = mocker.Mock(spec=DeviceRouter)
        mock_device_router.get_device_uid_by_name.return_value = None
        mocker.patch('zenossapi.routers.device.DeviceRouter', return_value=mock_device_router)
        
        with pytest.raises(ZenossAPIClientError) as exc:
            cmdb_router.get_cmdb_fields(name="non-existent-device")
        assert "Device with name non-existent-device not found" in str(exc.value)

    def test_get_cmdb_fields_no_params(self, cmdb_router):
        """Test getting CMDB fields without required parameters"""
        with pytest.raises(ValueError) as exc:
            cmdb_router.get_cmdb_fields()
        assert "Either uid or name must be specified" in str(exc.value)