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

import time
from openerp.osv import osv,fields

class lt_tarea(osv.osv):
    """ latinuxtarea """

    _name = 'lt.tarea'
    _columns = {
        'user_id': fields.many2one('res.users', 'Creator', required=True, readonly=True),
        'name': fields.char('Task Name', size=128, required=True, select=True),
        'date_create': fields.date('Create Date', select=True),
        'date_deadline': fields.date('Deadline', select=True),
        'description': fields.text('Description', help='Task contents'),
        'target_id': fields.many2one('lt.target', 'Target', required=True),
        'resource_ids': fields.one2many('lt.recurso', 'task_id', 'Recursos'),
        'state': fields.selection([('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'),
                                   ('done', 'Done'), ('cancelled', 'Cancelled')
                                  ], 'State', readonly=True, required=True,
                                  help="""When the task is created the state is \'Draft\'.
                                  If the task is started, the state becomes \'In Progress\'.
                                  If review is needed the task is in \'Pending\' state.
                                  If the task is over, the states is set to \'Done\'."""
                                 ),
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    _order = 'date_create desc'

    def do_open(self, cr, uid, ids, context={}):
        data = {'state': 'open'}
        self.write(cr, uid, ids, data, context=context)
        return True

    def do_draft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

lt_tarea()

class lt_recurso(osv.osv):
    """ recursos usados en una tarea """

    def _get_resource_price(self, cr, uid, ids, res_id=False, product_id=False, quantity=1.0, context={}):
        products = self.pool.get('product.product')
        resources = self.pool.get('lt.recurso')
        lt_res = resources.browse(cr, uid, ids)
        res = {}
        for r in lt_res:
            product = products.browse(cr, uid, r.name.id)
            standard_price = product.product_tmpl_id.standard_price
            res[r.id] = standard_price*r.quantity
        return res

    _name = 'lt.recurso'
    _columns = {
        'name': fields.many2one('product.product', 'Product', required=True),
     	'task_id': fields.many2one('lt.tarea', 'Task', ondelete='cascade', select=True),
 	    'quantity': fields.integer('Quantity', required=True),
        'resource_price': fields.function(_get_resource_price, string='Price', type='float', method=True, store=True),
    }

    _defaults = {
        'quantity': lambda *a :1.0,
    }

    def name_change(self, cr, uid, ids, prodid, qty, context={}):
        product = self.pool.get('product.product').browse(cr, uid, prodid)
        standard_price = product.product_tmpl_id.standard_price
        data = {'resource_price': standard_price*qty}
        return {'value': data}

lt_recurso()

class lt_target(osv.osv):
    """ objetivos de las tareas """

    def _get_progress_status(self, cr, uid, ids, fields, args, context):
        """ calculate target's progress status """
        res = {}
        this = self.browse(cr, uid, ids, context=context)
        tasks = self.pool.get('lt.tarea')
        for obj in this:
            total = len(obj.task_ids) or 1.0
            res[obj.id] = 0.0
            cont = 0
            for tid in obj.task_ids:
                task = tasks.read(cr, uid, tid.id, ['state'])
                if task['state'] in ('cancelled', 'done'):
                    cont += 1
                elif task['state'] in ('open', 'pending'):
                    cont += 0.5
            res[obj.id] = (cont/total)*100
        return res

    _name = 'lt.target'
    _columns = {
       'name': fields.char('Name', size=64, required=True),
       'task_ids': fields.one2many('lt.tarea', 'target_id', 'Task', required=False),
       'description': fields.text('Description'),# readonly=True, states={('draft','open','pending'): [('readonly', False)]}),
       'partner_id': fields.many2one('res.partner', 'Partner', required=True),
       'location': fields.char('Ubicación', size=150, required=False),
       'progress': fields.function(_get_progress_status, string='Progress State', type='float', digits=(4,2)),
    }

    def onchange_partner(self, cr, uid, ids, partner_id, context={}):
        """ set partner address when updating partner in form """
        addresses = self.pool.get('res.partner.address')
        location = 'sin definir'
        if addresses:
            address_id = addresses.search(cr, uid, [('partner_id', '=', partner_id)])
            address = addresses.browse(cr, uid, address_id)[0]
            lista = [(str(address.city or 'sin definir')), (str(address.state_id.name or 'sin definir')),
                     (str(address.country_id.name or 'sin definir'))]
            coma = ", "
            location = coma.join(lista)
        return {'value': {'location': location}}

lt_target()
