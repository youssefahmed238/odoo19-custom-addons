{
    'name': 'Nesting Optimizer Engine',
    'author': 'Youssef Ahmed',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Optimize cutting of material pieces',
    'description': """
        This module integrates Nest2D C++ library for cutting optimization.
    """,
    'depends': ['base'],
    'external_dependencies': {
        'python': ['matplotlib', 'ezdxf'],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
