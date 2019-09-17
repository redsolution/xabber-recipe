# Buildout recipe for Xabber server panel

Sample config:

    [buildout]
    show-picked-versions = true
    parts =
        django
    extensions = mr.developer
    auto-checkout = xabber_recipe
    eggs =
        setuptools
        pytz
        requests
        gunicorn
        zope.interface
        Pillow
        whitenoise

    versions = versions

    [versions]
    Django = 1.11.20
    requests = 2.21.0
    gunicorn = 19.3.0
    pytz = 2019.1
    setuptools = 33.1.1
    zope.interface = 4.6.0
    Pillow = 6.1.0
    whitenoise = 4.1.3

    [sources]
    xabber_recipe = git git@github.com:redsolution/xabber-recipe.git

    [django]
    recipe = xabber_recipe
    settings = development
    eggs = ${buildout:eggs}
    project = yourprojectname
    external-runner = gunicorn
