import os
import shutil
import sys
import tempfile
import unittest

import mock
import pkg_resources
from zc.buildout import UserError

from xabber_recipe.recipe import Recipe


class BaseTestRecipe(unittest.TestCase):

    def setUp(self):
        self.buildout_dir = tempfile.mkdtemp('xabber_recipe')

        self.bin_dir = os.path.join(self.buildout_dir, 'bin')
        self.develop_eggs_dir = os.path.join(self.buildout_dir,
                                             'develop-eggs')
        self.eggs_dir = os.path.join(self.buildout_dir, 'eggs')
        self.parts_dir = os.path.join(self.buildout_dir, 'parts')

        os.mkdir(self.bin_dir)

        self.recipe_initialisation = [
            {'buildout': {
                'eggs-directory': self.eggs_dir,
                'develop-eggs-directory': self.develop_eggs_dir,
                'bin-directory': self.bin_dir,
                'parts-directory': self.parts_dir,
                'directory': self.buildout_dir,
                'python': 'buildout',
                'executable': sys.executable,
                'find-links': '',
                'allow-hosts': ''},
             },
            'django',
            {'recipe': 'xabber_recipe'}]

        self.recipe = Recipe(*self.recipe_initialisation)

    def tearDown(self):
        shutil.rmtree(self.buildout_dir)


class TestRecipe(BaseTestRecipe):

    def test_consistent_options(self):
        self.assertEqual(Recipe(*self.recipe_initialisation).options,
                         Recipe(*self.recipe_initialisation).options)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    def test_update_smoketest(self, working_set):
        working_set

        self.recipe.install()
        self.recipe.update()

    def test_create_file(self):
        f, name = tempfile.mkstemp()
        os.remove(name)
        self.recipe.create_file(name, 'Spam %s', 'eggs')
        self.assertEqual(open(name).read(), 'Spam eggs')
        self.recipe.create_file(name, 'Spam spam spam %s', 'eggs')
        self.assertEqual(open(name).read(), 'Spam eggs')
        os.remove(name)

    @mock.patch('zc.recipe.egg.egg.Scripts.working_set',
                return_value=(None, []))
    @mock.patch('xabber_recipe.recipe.Recipe.create_manage_file')
    def test_extra_paths(self, manage, working_set):
        self.recipe.options['version'] = '1.0'
        self.recipe.options['extra-paths'] = 'somepackage\nanotherpackage'

        self.recipe.install()
        self.assertEqual(manage.call_args[0][0][-2:],
                         ['somepackage', 'anotherpackage'])

    def test_settings_option(self):
        self.assertEqual(self.recipe.options['settings'], 'development')
        self.recipe.options['settings'] = 'spameggs'
        self.recipe.create_manage_file([], [])
        manage = os.path.join(self.bin_dir, 'django')
        self.assertTrue("xabber_recipe.binscripts.manage('project.spameggs')"
                        in open(manage).read())

    def test_dotted_settings_path_option(self):
        self.assertEqual(self.recipe.options['settings'], 'development')
        self.recipe.options['dotted-settings-path'] = 'myproj.conf.production'
        self.recipe.create_manage_file([], [])
        manage = os.path.join(self.bin_dir, 'django')
        self.assertTrue("xabber_recipe.binscripts.manage('myproj.conf.production')"
                        in open(manage).read())


class TestRecipeScripts(BaseTestRecipe):

    @mock.patch('zc.buildout.easy_install.scripts',
                return_value=['some-path'])
    def test_make_protocol_scripts_return_value(self, scripts):
        self.recipe.options['wsgi'] = 'true'
        self.assertEqual(self.recipe.create_wsgi([], []),
                         ['some-path'])

    def test_create_manage_script(self):
        manage = os.path.join(self.bin_dir, 'django')
        self.recipe.create_manage_file([], [])
        self.assertTrue(os.path.exists(manage))

    def test_create_manage_file_with_initialization(self):
        manage = os.path.join(self.bin_dir, 'django')
        self.recipe.options['initialization'] = 'import os\nassert True'
        self.recipe.create_manage_file([], [])
        self.assertTrue('import os\nassert True\n\nimport xabber_recipe'
                        in open(manage).read())

    def test_dotted_settings_path_option(self):
        self.assertEqual(self.recipe.options['settings'], 'development')
        self.recipe.options['wsgi'] = 'true'
        self.recipe.options['dotted-settings-path'] = 'myproj.conf.production'
        self.recipe.create_wsgi([], [])
        wsgi_script = os.path.join(self.bin_dir, 'django.wsgi')
        self.assertTrue("application = "
                        "xabber_recipe.binscripts.wsgi('myproj.conf.production', "
                        "logfile='')"
                        in open(wsgi_script).read())

    def test_external_runner(self):
        ws = pkg_resources.WorkingSet()
        ws.require(['setuptools'])
        self.recipe.options['external-runner'] = 'unavailable'
        self.assertRaises(
            UserError,
            self.recipe.create_external_runner,
            *([], ws))

    def test_external_runner_2(self):
        ws = pkg_resources.WorkingSet()
        ws.require(['setuptools'])
        result = self.recipe.create_external_runner([], ws)
        self.assertEquals([], result)