from setuptools import setup


setup(name='sprite2',
      packages=['sprite2'],
      tests_require=[
        'pytest',
      ],
      entry_points={
          'console_scripts': [
              'sprite2 = sprite2.cli:cli'
          ]
      },
      )
