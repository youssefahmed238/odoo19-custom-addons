{
    'name': 'Sale Order Nesting',
    'author': 'Youssef Ahmed',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Integrate Nesting Optimization with Sales Orders',
    'description': """
        This module integrates Nest2D C++ library for cutting optimization with Sales Orders.
    """,
    'depends': ['base', 'product', 'sale', 'stock', 'nester'],
    'data': [
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'views/sale_order_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_order_nesting/static/src/js/nesting_image_viewer.js',
            'sale_order_nesting/static/src/xml/nesting_image_viewer.xml',
            'sale_order_nesting/static/src/css/nesting_image_viewer.css',
            "sale_order_nesting/static/src/scss/sale_calculate.scss",
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
