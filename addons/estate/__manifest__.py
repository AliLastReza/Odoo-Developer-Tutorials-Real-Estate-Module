# -*- coding: utf-8 -*-

{
    'name': 'Real Estate',
    'version': '0.1',
    'summary': "Real Estate Management.",
    'description': "",
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/estate_property_views.xml',
        'view/estate_property_offer_views.xml',
        'view/estate_property_type_views.xml',
        'view/estate_property_tag_views.xml',
        'view/estate_users_views.xml',
        'view/estate_menus.xml',
    ],
    'demo': [],
    'css': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
