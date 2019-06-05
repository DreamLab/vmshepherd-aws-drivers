from aiounittest import AsyncTestCase, futurized
from unittest.mock import Mock, MagicMock, patch

from vmshepherd_aws_drivers import AwsPresetDriver


class TestAwsPresetDriver(AsyncTestCase):

    def setUp(self):
        self.mock_config = {}
        self.mock_defaults = {}
        self.mock_runtime = Mock()

    def tearDown(self):
        AsyncTestCase.tearDown()

    async def test_reload(self):
        self.assertTrue()