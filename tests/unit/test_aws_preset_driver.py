from aiounittest import AsyncTestCase, futurized
from unittest.mock import Mock, MagicMock, patch
from asynctest import CoroutineMock
from vmshepherd_aws_drivers import AwsPresetDriver


class MockSession(MagicMock):

    async def __aenter__(self, a, b):
        return self

    def __aexit__(self):
        return self


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
                    'LaunchConfigurationName': 'test-lcn'
                }]
        }
        lc_mock = {
                'LaunchConfigurations': [
                    {
                        'InstanceType': 't5-large',
                        'ImageId': 'someimageid',
                        'SecurityGroups': ['sg_id_1', 'sg_id_2']
                    }]}

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
                        }
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
                Versions=['1234'])
        expected_preset_spec = {
          'count': 3,
          'flavor': 't5-large',
          'image': 'someimageid',
          'name': 'testasg',
          'network': {
              'availability_zone': 'eu-central-1',
              'security_groups': ['sg_id_1', 'sg_id_2']
              },
          'unmanaged': True
        }
        self.assertEqual(await instance._get_preset_spec(preset_name='testasg'), expected_preset_spec)
