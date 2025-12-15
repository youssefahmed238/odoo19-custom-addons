{
    'name': 'Nesting Optimizer Engine',
    'author': 'Youssef Ahmed',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Optimize cutting of material pieces',
    'description': """
        This module integrates Nest2D C++ library for cutting optimization.
    """,
    'depends': ['base', 'product', 'sale', 'stock'],
    'data': [
        'views/product_product_view.xml',
        'views/product_template_view.xml',
        'views/sale_order_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'nesting_optimizer/static/src/js/dxf_file_uploader.js',
            'nesting_optimizer/static/src/xml/dxf_file_uploader.xml',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
