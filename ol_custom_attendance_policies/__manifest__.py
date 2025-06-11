{
    'name': "Attendance Policies",
    'version': '17.0.1.0',
    'author': "Huzaifa",
    'sequence': 100,
    'description': """
        Description text
    """,
    'depends': ['base', 'hr', 'hr_holidays', 'hr_attendance','field_timepicker'],
    'data': [
        'views/ol_custom_policies.xml',
        'views/ol_custom_time_off.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    'license': 'LGPL-3',
}
