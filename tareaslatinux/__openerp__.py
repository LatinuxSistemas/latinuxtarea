# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'tareas y mantenimiento',
    'version': '0.1',
    'category': 'TyM',
    'description': """
Módulo para manejar tareas de contratistas y tareas de mantenimiento

Este módulo pretende ser de uso sencillo y dar respuesta a las necesidades básicas
    de empresas contratistas y sectores de empresas que realizan tareas de mantenimiento
    sobre máquinas o locaciones.

""",
    'author': 'Latinux Sistemas',
    'website': '',
    'depends': ['base', 'product'],
    'init_xml': [],
    'update_xml': [
        'tareaslatinux_data.xml',
        'security/tareaslatinux_security.xml',
        'wizard/task_report_view.xml',
        'board_tareaslatinux_view.xml',
        'tareaslatinux_view.xml',
        'wizard/target_report_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test':[],
    'installable': True,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
