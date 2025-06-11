
{
    'name': 'custom reports',
    'author': 'Ayesha Khalid ',
    'version': '1.0',
    'category': 'hr',
    'sequence': 95,
    'summary': 'custom reports',
    'description': "Custom reports",
    'website': '',
    'images': [
    ],
    'depends': ['base','hr','hr_payroll'],
    'data': [
        'reports/report_button.xml',
        'reports/report.xml',
        'reports/new_exp.xml',
        'reports/batch_payslip.xml',
        'views/print_report_button.xml'
        ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'hr_payroll/static/src/xml/**/*',
            'hr_payroll/static/src/**/*.xml',
        ],
        
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
    ],
    
    'license': 'LGPL-3',
}