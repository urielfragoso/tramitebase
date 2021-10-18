{
    'name': 'FLUJO TRAMITE BASE',
    'version': '1.0',
    'category': 'TRAMITE BASE IAP',
    'sequence': 15,
    'author':'DTIC JAPCDMX',
    'summary': 'Base para los tramites JAP',
    'description': 'Modulo para ver tramites',


    'depends': ['base','mail'],

    'data': [
        'views/solicitud_tramite_view.xml',
        'views/requerimiento_tramite_view.xml',
        'views/analisis_tramite_view.xml',
        'views/ficha_ejecutiva_tramite_view.xml',
        'views/gestion_tramite_view.xml',
        'views/tiempos_tramite_view.xml',
        'views/finaliza_tramite_view.xml',
        'security/tramite_jap_security.xml',
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'datas/template_mail_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}