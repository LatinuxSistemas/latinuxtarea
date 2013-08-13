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

    def _get_amount_total(self, cr, uid, ids, fields, args, context):
        this_task = self.browse(cr, uid, ids)[0]
        res= {this_task.id: 0.0}
        if this_task.resource_ids:
            for resource in this_task.resource_ids:
                res[this_task.id] += resource.resource_price
        return res

    _name = 'lt.tarea'
    _columns = {
        'user_id': fields.many2one('res.users', 'Creator', required=True, readonly=True),
        'name': fields.char('Task Name', size=128, required=True, select=True),
        'date': fields.datetime('Create Date', select=True),
        'date_deadline': fields.datetime('Deadline', select=True),
        'date_finish': fields.datetime('Finish Date', select=True),
        'date_cancel': fields.datetime('Cancel Date', select=True, readonly=True),
        'description': fields.text('Description', help='Task contents'),
        'target_id': fields.many2one('lt.target', 'Target', required=True),
        'resource_ids': fields.one2many('lt.recurso', 'task_id', 'Recursos'),
        'tarea_amount_total': fields.function(_get_amount_total, string='Total expenditure ($)', type='float', readonly=True, store=True),
        'reference': fields.char('Reference Doc', size=128, required=False),
        'order_by': fields.char('Order By', size=128, required=False),
        'delay': fields.float('Delay'),
        'priority': fields.selection([('1', 'Normal'),('2', 'Critical')], 'Priority', required=True),
        'state': fields.selection([('0', 'New'),('1', 'In Progress'),('2', 'Pending'),
                                   ('9', 'Done'), ('10', 'Cancelled')
                                  ], 'State', readonly=True, required=True,
                                  help="""When the task is created the state is \'Draft\'.
                                  If the task is started, the state becomes \'In Progress\'.
                                  If review is needed the task is in \'Pending\' state.
                                  If the task is over, the states is set to \'Done\'."""
                                 ),
    }

    _order = 'state asc,priority desc,date desc'

    _defaults = {
        'state': lambda *a: '0',
        'priority': lambda *a: '1',
        'user_id': lambda obj, cr, uid, context: uid,
        'delay': 1.0,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def do_done(self, cr, uid, ids, context={}):
        date_finish = time.strftime("%Y-%m-%d %H:%M:%S")
        data = {'state': '9', 'date_finish': date_finish}
        self.write(cr, uid, ids, data, context=context)
        return True

    def do_open(self, cr, uid, ids, context={}):
        data = {'state': '1'}
        self.write(cr, uid, ids, data, context=context)
        return True

    def do_cancel(self, cr, uid, ids, context={}):
        date_cancel = time.strftime("%Y-%m-%d %H:%M:%S")
        data = {'state': '10', 'date_cancel': date_cancel}
        self.write(cr, uid, ids, data, context=context)
        return True

    def do_draft(self, cr, uid, ids, context={}):
        data = {'state': '0'}
        self.write(cr, uid, ids, data, context=context)
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
        'resource_price': fields.function(_get_resource_price, string='Price', type='float', method=True, store=True, digits=(4,2)),
    }

    _defaults = {
        'quantity': lambda *a :1.0,
    }

    def name_change(self, cr, uid, ids, prodid, qty, context={}):
        data = {}
        if prodid:
            product = self.pool.get('product.product').browse(cr, uid, prodid)
            standard_price = product.product_tmpl_id.standard_price
            data = {'resource_price': standard_price*qty}
        return {'value': data}

lt_recurso()

class lt_target(osv.osv):
    """ objetivos sobre los que se aplican las tareas """

    def _get_progress_status(self, cr, uid, ids, fields, args, context):
        """ calculate target's progress status """
        res = {}
        this = self.browse(cr, uid, ids, context=context)
        for obj in this:
            total = len(obj.task_ids) or 1.0
            res[obj.id] = 0.0
            cont = 0
            for tid in obj.task_ids:
                if tid.state in ('10', '9'):
                    cont += 1
                elif tid.state in ('1', '2'):
                    cont += 0.5
            res[obj.id] = (cont/total)*100
        return res

    _name = 'lt.target'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'task_ids': fields.one2many('lt.tarea', 'target_id', 'Task', required=False),
        'description': fields.text('Description'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'location': fields.char('Ubicación', size=150, required=False),
        'file_ids': fields.one2many('ir.attachment', 'target_id', 'Adjunto', required=False),
        'progress': fields.function(_get_progress_status, string='Progress State(%)', type='float', digits=(4,2)),
    }

    def onchange_partner(self, cr, uid, ids, partner_id, context={}):
        """ set partner address when updating partner in form """
        addresses = self.pool.get('res.partner.address')
        location = 'not set'
        if addresses:
            address_id = addresses.search(cr, uid, [('partner_id', '=', partner_id)])
            address = addresses.browse(cr, uid, address_id)[0]
            lista = [(str(address.city or 'not set'))]
            if address.state_id.name:
                lista.append(str(address.state_id.name))
            if address.country_id.name:
                lista.append(str(address.country_id.name))
            if len(lista) > 1:
                coma = ", "
                location = coma.join(lista)
            else:
                location = lista[0]
        return {'value': {'location': location}}

lt_target()

class ir_attachment(osv.osv):
    _name = 'ir.attachment'
    _inherit = 'ir.attachment'
    _columns = {
        'target_id': fields.many2one('lt.target'),
    }

ir_attachment()
