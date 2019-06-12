import base64
import aiobotocore
from vmshepherd.presets import AbstractConfigurationDriver


class AwsPresetDriver(AbstractConfigurationDriver):

    def __init__(self, config, runtime, defaults):
        super().__init__(runtime, defaults)
        self._presets = {}

    async def _get_preset_spec(self, preset_name: str):
        return self._specs[preset_name]

    async def _list(self):
        await self._reload()
        return self._specs.keys()

    async def _reload(self):

        session = aiobotocore.get_session()
        async with session.create_client('autoscaling') as asg, session.create_client('ec2') as ec2:
            res = await asg.describe_auto_scaling_groups()

            _tmp_specs = {}
            for preset in res['AutoScalingGroups']:
                config = {}
                config['name'] = preset_name = preset['AutoScalingGroupName']
                config['count'] = preset['DesiredCapacity']
                config['network'] = {}
                config['network']['availability_zone'] = ','.join(preset['AvailabilityZones'])

                # preset is managed by ASG
                config['unmanaged'] = True

                if 'LaunchConfigurationName' in preset:
                    res = await asg.describe_launch_configurations(
                        LaunchConfigurationNames=[preset['LaunchConfigurationName']]
                    )
                    launch_config = res['LaunchConfigurations'][0]
                    config['flavor'] = launch_config['InstanceType']
                    config['image'] = launch_config['ImageId']
                    config['network']['security_groups'] = launch_config['SecurityGroups']
                    if 'UserData' in launch_config:
                        config['user_data'] = base64.b64decode(launch_config['UserData']).decode('utf-8')

                elif 'LaunchTemplate' in preset:
                    version = '$Latest'
                    if 'Version' in preset['LaunchTemplate']:
                        version = preset['LaunchTemplate']['Version']
                    res = await ec2.describe_launch_template_versions(
                        LaunchTemplateId=preset['LaunchTemplate']['LaunchTemplateId'],
                        Versions=[version]
                    )

                    launch_config = res['LaunchTemplateVersions'][0]['LaunchTemplateData']
                    config['flavor'] = launch_config['InstanceType']
                    config['image'] = launch_config['ImageId']
                    config['network']['security_groups'] = launch_config['SecurityGroupIds']
                    if 'UserData' in launch_config:
                        config['userdata'] = base64.b64decode(launch_config['UserData']).decode('utf-8')

                _tmp_specs[preset_name] = config
        self._specs = _tmp_specs

    def reconfigure(self, config, defaults):
        super().reconfigure(config, defaults)
