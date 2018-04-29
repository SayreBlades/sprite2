from setuptools import setup

install_requires = [
    'click',
    'cloudpickle',
    'boto3',
    'docker',
    ]

setup(name='sprite2',
      packages=['sprite2'],
      install_requires=install_requires,
      tests_require=[
        'pytest',
      ],
      entry_points={
          'console_scripts': [
              'sprite2 = sprite2.main:cli'
          ]
      },
      )
