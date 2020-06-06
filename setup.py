from setuptools import setup, find_packages

version = '1.0'


setup(name='xabber_recipe',
      version=version,
      description="Xabber server panel buildout recipe",
      classifiers=[
        'Framework :: Buildout',
        'Framework :: Django',
        'Topic :: Software Development :: Build Tools',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ],
      package_dir={'': 'src'},
      packages=find_packages('src'),
      keywords='',
      author='Redsolution oU',
      author_email='info@redsolution.com',
      license='BSD',
      zip_safe=False,
      install_requires=[
        'zc.buildout',
        'zc.recipe.egg',
        'Django==1.11.29',
      ],
      extras_require={'test': ['coverage',
                               'mock']},
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = xabber_recipe.recipe:Recipe
      """,
)
