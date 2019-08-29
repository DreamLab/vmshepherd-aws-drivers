import datetime
from unittest.mock import MagicMock, Mock, patch

from aiounittest import AsyncTestCase
from aiounittest.mock import AsyncMockIterator
from asynctest import CoroutineMock

from vmshepherd_aws_drivers import AwsIaaSDriver
from vmshepherd.iaas.vm import Vm

ec2_created_at_mock = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

ec2_mock = {
    'InstanceId': 'someinstanceid',
    'PrivateIpAddress': '10.188.25.12',
    'LaunchTime': ec2_created_at_mock,
    'InstanceType': 't5-large',
    'ImageId': 'someimageid',
    'State': {'Name': 'running'},
    'Tags': ['tag1', 'tag2']
}

mapping_ec2_mock = Vm(
    'someinstanceid', 'someinstanceid', ['10.188.25.12'], ec2_created_at_mock, 'running', ['tag1', 'tag2'],
    ['tag1', 'tag2'], 't5-large', 'someimageid'
)


class MockSession(MagicMock):

    async def __aenter__(self, a, b):
        return self

    def __aexit__(self):
        return self


class MockAWSServices(MagicMock):

    async def __aenter__(self):
        return self

    async def __aexit__(self, a, b, c):
        return self

    def get_paginator(self, method):
        return self

    def paginate(self, PaginationConfig={}, Filters={}):
        return AsyncMockIterator([{
            'Reservations': [{'Instances': [ec2_mock]}]
        }])


class TestAwsIaaSDriver(AsyncTestCase):

    def setUp(self):
        self.aiobotocore_mock = Mock()
        self.session_mock = MockSession()
        self.aws_services_mock = MockAWSServices()
        self.session_mock.create_client.return_value = self.aws_services_mock
        self.aiobotocore_mock.get_session = MagicMock(return_value=self.session_mock)
        patch('vmshepherd_aws_drivers.aws_iaas_driver.aiobotocore', self.aiobotocore_mock).start()
        self.aws_driver = AwsIaaSDriver({})

    def test_map_vm_structure(self):
        structure = self.aws_driver._map_vm_structure(ec2_mock)
        self.assertEqual(structure, mapping_ec2_mock)

    async def test_get_vm(self):
        ec2_result = {
                'Reservations': [{
                    'Instances': [ec2_mock]
                        }]}
        self.aws_services_mock.describe_instances = CoroutineMock(return_value=ec2_result)
        vm = await self.aws_driver.get_vm('someinstanceid')
        self.assertEqual(vm, mapping_ec2_mock)

    async def test_list_vms(self):
        vms = await self.aws_driver.list_vms('somepresetname')
        self.assertEqual(vms[0], mapping_ec2_mock)
