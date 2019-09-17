import os
import sys
import unittest

import mock
from xabber_recipe import binscripts


class ScriptTestCase(unittest.TestCase):

    def setUp(self):
        self.settings = mock.sentinel.Settings
        self.settings.SECRET_KEY = 'Not super secret key'

        sys.modules['testpanel'] = mock.sentinel.testpanel
        sys.modules['testpanel.development'] = self.settings
        sys.modules['testpanel'].development = self.settings

        print("DJANGO ENV: %s" % os.environ.get('DJANGO_SETTINGS_MODULE'))

    def tearDown(self):
        for m in ['testpanel', 'testpanel.development']:
            del sys.modules[m]


class TestScript(ScriptTestCase):

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    def test_script(self, mock_setdefault, execute_from_command_line):
        with mock.patch.object(sys, 'argv', ['bin/test']):
            binscripts.test('testpanel.development', '', 'spamm', 'eggs')
            self.assertTrue(execute_from_command_line.called)
            self.assertEqual(execute_from_command_line.call_args[0],
                             (['bin/test', 'test', 'spamm', 'eggs'],))
            self.assertEqual(mock_setdefault.call_args[0],
                             ('DJANGO_SETTINGS_MODULE',
                              'testpanel.development'))

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    def test_script_with_args(self, mock_setdefault,
                              execute_from_command_line):
        with mock.patch.object(sys, 'argv', ['bin/test', '--verbose']):
            binscripts.test('testpanel.development', '', 'spamm', 'eggs')
            self.assertEqual(
                execute_from_command_line.call_args[0],
                (['bin/test', 'test', 'spamm', 'eggs', '--verbose'],))
            self.assertEqual(
                mock_setdefault.call_args[0],
                ('DJANGO_SETTINGS_MODULE', 'testpanel.development'))

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    def test_deeply_nested_settings(self, mock_setdefault,
                                    execute_from_command_line):
        settings = mock.sentinel.SettingsModule
        settings.SECRET_KEY = 'Not super secret key'

        nce = mock.sentinel.NCE
        nce.development = settings

        sys.modules['testpanel'].nce = nce
        sys.modules['testpanel.nce'] = nce
        sys.modules['testpanel.nce.development'] = settings

        binscripts.test('testpanel.nce.development', '', 'tilsit', 'stilton')
        self.assertEqual(
            mock_setdefault.call_args[0],
            ('DJANGO_SETTINGS_MODULE', 'testpanel.nce.development'))

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    @mock.patch('coverage.coverage.xml_report')
    def test_script_with_coverage(
            self, mock_xml_report, mock_setdefault, execute_from_command_line):
        with mock.patch.object(sys, 'argv', ['bin/test']):
            binscripts.test('testpanel.development',
                            'report xml_report', 'spamm', 'eggs')

            self.assertTrue(execute_from_command_line.called)
            self.assertTrue(mock_xml_report.called)

            self.assertEqual(execute_from_command_line.call_args[0],
                             (['bin/test', 'test', 'spamm', 'eggs'],))
            self.assertEqual(mock_setdefault.call_args[0],
                             ('DJANGO_SETTINGS_MODULE',
                              'testpanel.development'))


class TestManageScript(ScriptTestCase):

    @mock.patch('django.core.management.execute_from_command_line')
    @mock.patch('os.environ.setdefault')
    def test_script(self, mock_setdefault, mock_execute):
        binscripts.manage('testpanel.development')
        self.assertEqual(mock_execute.call_args,
                         ((sys.argv,), {}))
        self.assertEqual(
            mock_setdefault.call_args,
            (('DJANGO_SETTINGS_MODULE', 'testpanel.development'), {}))


