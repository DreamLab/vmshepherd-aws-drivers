from itertools import chain
import aiobotocore
from botocore.exceptions import ClientError
from typing import Dict, List
from vmshepherd.iaas import AbstractIaasDriver, Vm, VmState


class AwsIaaSDriver(AbstractIaasDriver):

    _VM_STATUSES = {
         'shutting-down': VmState.TERMINATED,
         'terminated':  VmState.TERMINATED,
         'stopping':  VmState.TERMINATED,
         'stopped':  VmState.TERMINATED,
         'pending': VmState.PENDING,
         'running': VmState.RUNNING
    }

    def __init__(self, config):
        self.config = config

    async def list_vms(self, preset_name: str) -> List:
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
                PaginationConfig={'PageSize': self.config.get('ec2_page_size', 5)},
                Filters=filters
            ):
                instances = chain(instances, *[vms['Instances'] for vms in result['Reservations']])

        return [self._map_vm_structure(instance) for instance in instances]

    async def create_vm(self):
        '''
        NotImplemented - preset is managed by ASG
        '''
        raise Exception('Preset is managed by ASG')

    async def get_vm(self, vm_id: str) -> Vm:
        session = aiobotocore.get_session()
        async with session.create_client('ec2') as client:
            try:
                res = await client.describe_instances(
                    InstanceIds=[vm_id]
                )
            except ClientError:
                raise Exception(f'Vm (id: {vm_id} not found')
        return self._map_vm_structure(res['Reservations'][0]['Instances'][0])

    async def terminate_vm(self, vm_id: str):
        session = aiobotocore.get_session()
        async with session.create_client('ec2') as client:
            res = await client.terminate_instances(
                InstanceIds=[vm_id]
            )

    def _map_vm_structure(self, instance: Dict) -> Vm:
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

    def _map_vm_status(self, vm_status: str) -> str:
        '''
         Map AWS vm statuses to vmshepherd vm statuses
         AWS vm statuses: pending | running | shutting-down | terminated | stopping | stopped

         :arg string vm_status
         :returns string
        '''

        return self._VM_STATUSES.get(vm_status, VmState.UNKNOWN)
