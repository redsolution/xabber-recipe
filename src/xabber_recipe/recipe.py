import os
import logging
import sys

from zc.buildout import UserError
import pkg_resources
import zc.recipe.egg

from xabber_recipe.templates import WSGI_TEMPLATE, WSGI_HEADER


class Recipe(object):
    def __init__(self, buildout, name, options):
        self.log = logging.getLogger(name)

        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.name, self.options = buildout, name, options

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], name)
        options['bin-directory'] = buildout['buildout']['bin-directory']

        options.setdefault('project', 'project')
        options.setdefault('extra-paths', '')
        options.setdefault('settings', 'development')
        options.setdefault('external-runner', '')
        options.setdefault('deploy-script-extra', '')
        options.setdefault('initialization', '')
        options.setdefault('coverage', '')

        # options.setdefault('wsgi', 'false')
        options.setdefault('logfile', '')

        options['buildout-directory'] = buildout['buildout']['directory']
        self._relative_paths = options['buildout-directory']

    def install(self):
        extra_paths = self.get_extra_paths()
        ws = self.egg.working_set(['xabber_recipe'])[1]

        script_paths = []
        script_paths.extend(self.create_manage_file(extra_paths, ws))
        script_paths.extend(self.create_test_runner(extra_paths, ws))
        script_paths += self.create_external_runner(
            extra_paths, ws)

        return script_paths

    def create_manage_file(self, extra_paths, ws):
        settings = self.get_settings()
        return zc.buildout.easy_install.scripts(
            [(self.options.get('control-script', self.name),
              'xabber_recipe.binscripts', 'manage')],
            ws, sys.executable, self.options['bin-directory'],
            extra_paths=extra_paths,
            relative_paths=self._relative_paths,
            arguments="'%s'" % settings,
            initialization=self.options['initialization'])

    def create_test_runner(self, extra_paths, working_set):
        settings = self.get_settings()
        coverage_functions = self.options.get('coverage', '')

        if coverage_functions.lower() == 'true':
            coverage_functions = 'report html_report xml_report'
        apps = self.options.get('test', '').split()

        if apps:
            return zc.buildout.easy_install.scripts(
                [(self.options.get('testrunner', 'test'),
                  'xabber_recipe.binscripts', 'test')],
                working_set, sys.executable,
                self.options['bin-directory'],
                extra_paths=extra_paths,
                relative_paths=self._relative_paths,
                arguments="'%s', '%s', %s" % (
                    settings,
                    coverage_functions,
                    ', '.join(["'%s'" % app for app in apps])),
                initialization=self.options['initialization'])
        else:
            return []

    # def create_wsgi(self, extra_paths, ws):
    #     scripts = []
    #
    #     _script_template = zc.buildout.easy_install.script_template
    #     settings = self.get_settings()
    #
    #     zc.buildout.easy_install.script_template = (
    #         WSGI_HEADER +
    #         WSGI_TEMPLATE +
    #         self.options['deploy-script-extra']
    #     )
    #
    #     if self.options.get('wsgi', '').lower() == 'true':
    #         scripts.extend(
    #             zc.buildout.easy_install.scripts(
    #                 [(self.options.get('wsgi-script') or
    #                   '%s.%s' % (self.options.get('control-script',
    #                                               self.name),
    #                              'wsgi'),
    #                   'xabber_recipe.binscripts', 'wsgi')],
    #                 ws,
    #                 sys.executable,
    #                 self.options['bin-directory'],
    #                 extra_paths=extra_paths,
    #                 relative_paths=self._relative_paths,
    #                 arguments="'%s', logfile='%s'" % (
    #                     settings, self.options.get('logfile')),
    #                 initialization=self.options['initialization'],
    #             ))
    #     zc.buildout.easy_install.script_template = _script_template
    #     return scripts

    def create_external_runner(self, extra_paths, ws):

        zc.buildout.easy_install.script_template = (
                WSGI_HEADER +
                WSGI_TEMPLATE +
                self.options['deploy-script-extra']
        )

        script_names = [entrypoint.strip() for entrypoint in
                        self.options.get('external-runner').splitlines()
                        if entrypoint.strip()]
        if not script_names:
            return []
        settings = self.get_settings()
        initialization = self.options['initialization']
        initialization += (
            "\n" +
            "os.environ['DJANGO_SETTINGS_MODULE'] = '%s'" % settings)
        created_scripts = []
        known_entrypoints = list(ws.iter_entry_points('console_scripts'))
        to_create = [entrypoint for entrypoint in known_entrypoints
                     if entrypoint.name in script_names]
        for entrypoint in to_create:
            script_name = entrypoint.name
            dotted_path = entrypoint.module_name
            function_name = entrypoint.attrs[0]
            self.log.debug("Creating entrypoint %s:%s as %s",
                           dotted_path, function_name, script_name)
            zc.buildout.easy_install.scripts(
                [(script_name, dotted_path, function_name)],
                ws, sys.executable, self.options['bin-directory'],
                extra_paths=extra_paths,
                relative_paths=self._relative_paths,
                initialization=initialization)
            created_scripts.append(script_name)

        known_names = [entrypoint.name for entrypoint in known_entrypoints]

        unkown_script_names = [name for name in script_names
                               if name not in known_names]
        if unkown_script_names:
            raise UserError("Some script names couldn't be found: %s" % (
                ', '.join(unkown_script_names)))
        return created_scripts

    def get_extra_paths(self):
        extra_paths = [self.buildout['buildout']['directory']]
        pythonpath = [p.replace('/', os.path.sep) for p in
                      self.options['extra-paths'].splitlines() if p.strip()]
        extra_paths.extend('')
        return extra_paths

    def update(self):
        extra_paths = self.get_extra_paths()
        ws = self.egg.working_set(['xabber_recipe'])[1]

        self.create_manage_file(extra_paths, ws)
        self.create_test_runner(extra_paths, ws)
        self.create_external_runner(extra_paths, ws)

    def create_file(self, filename, template, options):
        if os.path.exists(filename):
            return

        f = open(filename, 'w')
        f.write(template % options)
        f.close()

    def get_settings(self):
        settings = '%s.%s' % (self.options['project'], self.options['settings'])
        settings = self.options.get('dotted-settings-path', settings)
        return settings
