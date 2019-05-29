import asyncio
import aiobotocore
from typing import Any, Dict, List
from vmshepherd.iaas import AbstractIaasDriver, Vm, VmState


class AwsIaaSDriver(AbstractIaasDriver):

    async def list_vms(self, preset_name):
        '''
        List VMs by preset name
        :arg present_name: string
        '''
        loop = asyncio.get_event_loop()
        session = aiobotocore.get_session(loop=loop)
        async with session.create_client('ec2') as client:
            res = await client.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:aws:autoscaling:groupName',
                        'Values': [preset_name]
                    }
                ]
            )
            instances = []
            for vms in res['Reservations']:
                instances.extend(vms['Instances'])
        result = []
        for instance in instances:
            result.append(self._map_vm_structure(instance))
        return result

    async def create_vm(self, preset_name: str, image: str, flavor: str, security_groups: List=None,
                        userdata: Dict=None, key_name: str=None, availability_zone: str=None,
                        subnets: List=None):
        pass

    async def get_vm(self, vm_id: Any):
        pass

    async def terminate_vm(self, vm_id: Any):
        pass

    def _map_vm_structure(self, instance):
        '''
        Vm unification
        :arg instance: object
        :returns object
        '''
        ip = [instance.get('PrivateIpAddress', '')]
        created = instance['LaunchTime']
        flavor = instance['InstanceType']
        image = instance['ImageId']
        state = self._map_vm_status(instance['State']['Name'])
        iaasvm = Vm(self, instance['InstanceId'], instance['InstanceId'], ip, created, state=state,
                    metadata=instance.get('Tags', []), tags=instance.get('Tags', []), flavor=flavor,
                    image=image, timed_shutdown_at=None)
        return iaasvm

    def _map_vm_status(self, vm_status):
        '''
         Map AWS vm statuses to vmshepherd vm statuses
         AWS vm statuses: pending | running | shutting-down | terminated | stopping | stopped

         :arg string vm_status
         :returns string
        '''
        statuses = {
            VmState.TERMINATED: [
                'shutting-down',
                'terminated',
                'stopping',
                'stopped'
            ],
            VmState.PENDING: ['pending'],
            VmState.RUNNING: ['running']
        }

        state = VmState.UNKNOWN
        for vmstate, value in statuses.items():
            if vm_status in value:
                state = vmstate
                break
        return state
