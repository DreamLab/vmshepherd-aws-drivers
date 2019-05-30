vmshepherd-aws-drivers
======================

Introduction
------------

Provides plugin for `VmShepherd <https://github.com/DreamLab/VmShepherd>`_ .
Drivers allows to view panel with autoscaling groups and use rpc api from vmshepherd


Installation
------------

Simply use ``pip``.

::

    pip install vmshepherd-aws-drivers

Library requires (as well as VmShepherd itself) python 3.6 or later.

Usage
-----

Install package (in the same environment as VmShepherd) and configure ``VmShepherd`` like:

::

    # ...

    iaas:
      driver: AwsIaaSDriver

    preset:
      driver: AwsPresetDriver
      ec2_page_size: 1000 (optional) - maximum number of instances returned in one call to aws ec2 api

    # ...



Develop
-------

Run tests:

::

    make test
    make develop


License
-------

`Apache License 2.0 <LICENSE>`_

