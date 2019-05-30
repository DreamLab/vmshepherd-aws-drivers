import asyncio
import aiobotocore
from typing import Any, Dict, List
from vmshepherd.iaas import AbstractIaasDriver, Vm, VmState


class AwsIaaSDriver(AbstractIaasDriver):

    def __init__(self, config):
        self.config = config

    async def list_vms(self, preset_name):
        '''
        List VMs by preset name
        :arg present_name: string
        '''
        session = aiobotocore.get_session()
        async with session.create_client('ec2') as client:
            paginator = client.get_paginator('describe_instances')
            filters = [
                {
                    'Name': 'tag:aws:autoscaling:groupName',
                    'Values': [preset_name]
                }
            ]
            instances = []
            async for result in paginator.paginate(
                PaginationConfig={'PageSize': self.config.get('ec2_page_size', 1000)},
                Filters=filters
            ):
                for vms in result['Reservations']:
                    instances.extend(vms['Instances'])

        return [self._map_vm_structure(instance) for instance in instances]

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
