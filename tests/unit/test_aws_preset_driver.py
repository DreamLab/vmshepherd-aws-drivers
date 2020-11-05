from unittest.mock import MagicMock, Mock, call, patch

from aiounittest import AsyncTestCase
from asynctest import CoroutineMock

from vmshepherd_aws_drivers import AwsPresetDriver

from .common import MockSession


class MockAWSServices(MagicMock):

    async def __aenter__(self):
        return self

    def __aexit__(self, a, b, c):
        return self

    def __await__(self):
        return iter([])


class TestAwsPresetDriver(AsyncTestCase):

    def setUp(self):
        self.aiobotocore_mock = Mock()

        self.session_mock = MockSession()

        self.aws_services_mock = MockAWSServices()
        self.session_mock.create_client.return_value = self.aws_services_mock

        self.aiobotocore_mock.get_session = MagicMock(return_value=self.session_mock)
        patch('vmshepherd_aws_drivers.aws_preset_driver.aiobotocore', self.aiobotocore_mock).start()

    def tearDown(self):
        AsyncTestCase.tearDown(self)

    async def test_reload_launch_configuration(self):

        asg_mock = {
            'AutoScalingGroups': [{
                'AutoScalingGroupName': 'testasg',
                'DesiredCapacity': 3,
                'AvailabilityZones': ['eu-central-1'],
                'LaunchConfigurationName': 'test-lcn',
                'Tags': [
                    {
                        'PropagateAtLaunch': False,
                        'Value': 'value1',
                        'ResourceId': 'testasg',
                        'Key': 'key1',
                        'ResourceType': 'auto-scaling-group'
                    }
                ]
            }]
        }
        lc_mock = {
            'LaunchConfigurations': [
                {
                    'InstanceType': 't5-large',
                    'ImageId': 'someimageid',
                    'SecurityGroups': ['sg_id_1', 'sg_id_2']
                }]
        }

        self.aws_services_mock.describe_auto_scaling_groups = CoroutineMock(return_value=asg_mock)
        self.aws_services_mock.describe_launch_configurations = CoroutineMock(return_value=lc_mock)

        instance = AwsPresetDriver({}, {}, {})
        await instance._reload()
        self.aiobotocore_mock.get_session.assert_called()
        self.aws_services_mock.describe_auto_scaling_groups.assert_called()
        self.aws_services_mock.describe_launch_configurations.assert_called_with(LaunchConfigurationNames=['test-lcn'])
        expected_preset_spec = {
            'count': 3,
            'flavor': 't5-large',
            'image': 'someimageid',
            'name': 'testasg',
            'network': {
                'availability_zone': 'eu-central-1',
                'security_groups': ['sg_id_1', 'sg_id_2']
            },
            'meta_tags': {'key1': 'value1'},
            'unmanaged': True
        }
        self.assertEqual(await instance._get_preset_spec(preset_name='testasg'), expected_preset_spec)

    async def test_reload_launch_template(self):

        asg_mock = {
            'AutoScalingGroups': [{
                'AutoScalingGroupName': 'testasg',
                'DesiredCapacity': 3,
                'AvailabilityZones': ['eu-central-1'],
                'LaunchTemplate': {
                    'LaunchTemplateId': 'somelaunchtemplateid',
                    'Version': '1234'
                },
                'Tags': [
                    {
                        'PropagateAtLaunch': False,
                        'Value': 'value1',
                        'ResourceId': 'testasg',
                        'Key': 'key1',
                        'ResourceType': 'auto-scaling-group'
                    }
                ]
            }]
        }
        lt_mock = {
            'LaunchTemplateVersions': [{
                'LaunchTemplateData': {
                    'InstanceType': 't5-large',
                    'ImageId': 'someimageid',
                    'SecurityGroupIds': ['sg_id_1', 'sg_id_2']
                }
            }]
        }

        self.aws_services_mock.describe_auto_scaling_groups = CoroutineMock(return_value=asg_mock)
        self.aws_services_mock.describe_launch_template_versions = CoroutineMock(return_value=lt_mock)

        instance = AwsPresetDriver({}, {}, {})
        await instance._reload()
        self.aiobotocore_mock.get_session.assert_called()
        self.aws_services_mock.describe_auto_scaling_groups.assert_called()
        self.aws_services_mock.describe_launch_template_versions.assert_called_with(
            LaunchTemplateId='somelaunchtemplateid',
            Versions=['1234']
        )
        expected_preset_spec = {
            'count': 3,
            'flavor': 't5-large',
            'image': 'someimageid',
            'name': 'testasg',
            'network': {
                'availability_zone': 'eu-central-1',
                'security_groups': ['sg_id_1', 'sg_id_2']
            },
            'meta_tags': {'key1': 'value1'},
            'unmanaged': True
        }
        self.assertEqual(await instance._get_preset_spec(preset_name='testasg'), expected_preset_spec)

    async def test_reload_launch_configuration_with_marker(self):

        asg_mock_reponses = [{
            'AutoScalingGroups': [{
                'AutoScalingGroupName': 'aaaa',
                'DesiredCapacity': 3,
                'AvailabilityZones': ['eu-central-1a'],
                'LaunchConfigurationName': 'test-lcn-1',
                'Tags': []
            }], "NextToken": "1234"
        }, {
            'AutoScalingGroups': [{
                'AutoScalingGroupName': 'bbbb',
                'DesiredCapacity': 5,
                'AvailabilityZones': ['eu-central-1b'],
                'LaunchConfigurationName': 'test-lcn-2',
                'Tags': []
            }], "NextToken": "ASDF"
        }, {
            'AutoScalingGroups': [{
                'AutoScalingGroupName': 'cccc',
                'DesiredCapacity': 7,
                'AvailabilityZones': ['eu-central-1c'],
                'LaunchConfigurationName': 'test-lcn-3',
                'Tags': []
            }, {
                'AutoScalingGroupName': 'dddd',
                'DesiredCapacity': 11,
                'AvailabilityZones': ['eu-central-1d'],
                'LaunchConfigurationName': 'test-lcn-4',
                'Tags': [{'Key': 'my', 'Value': 'tag'}]
            }], "NextToken": ""
        }]
        lc_mock = {
            'LaunchConfigurations': [
                {
                    'InstanceType': 't5-large',
                    'ImageId': 'someimageid',
                    'SecurityGroups': ['sg_id_1', 'sg_id_2']
                }]
        }

        self.aws_services_mock.describe_auto_scaling_groups = CoroutineMock(side_effect=asg_mock_reponses)
        self.aws_services_mock.describe_launch_configurations = CoroutineMock(return_value=lc_mock)

        instance = AwsPresetDriver({}, {}, {})
        await instance._reload()
        self.aiobotocore_mock.get_session.assert_called()
        self.aws_services_mock.describe_auto_scaling_groups.assert_called()
        self.aws_services_mock.describe_launch_configurations.assert_has_calls([
            call(LaunchConfigurationNames=['test-lcn-1']),
            call(LaunchConfigurationNames=['test-lcn-2']),
            call(LaunchConfigurationNames=['test-lcn-3']),
            call(LaunchConfigurationNames=['test-lcn-4'])
        ])
        expected_preset_spec = {
            'count': 3,
            'flavor': 't5-large',
            'image': 'someimageid',
            'name': 'aaaa',
            'network': {
                'availability_zone': 'eu-central-1a',
                'security_groups': ['sg_id_1', 'sg_id_2']
            },
            'meta_tags': {},
            'unmanaged': True
        }
        self.assertEqual(await instance._get_preset_spec(preset_name='aaaa'), expected_preset_spec)

        expected_preset_spec = {
            'count': 11,
            'flavor': 't5-large',
            'image': 'someimageid',
            'name': 'dddd',
            'network': {
                'availability_zone': 'eu-central-1d',
                'security_groups': ['sg_id_1', 'sg_id_2']
            },
            'meta_tags': {'my': 'tag'},
            'unmanaged': True
        }
        self.assertEqual(await instance._get_preset_spec(preset_name='dddd'), expected_preset_spec)
