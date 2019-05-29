vmshepherd-aws-drivers
======================

Introduction
------------

Provides plugin for ``VmShepherd`` - driver allows to store runtime data and lock management in postgres database.


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

