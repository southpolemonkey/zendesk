from setuptools import setup

setup(
    name="zendesk_bot",
    version="1.0",
    py_modules=["zendesk_bot"],
    install_requires=[
        'click',
        'pyfiglet',
        'pylint',
        'mypy'
    ],
    entry_points='''
          [console_scripts]
          zbot=app:main
    '''
)
