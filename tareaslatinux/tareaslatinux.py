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

from openerp.osv import osv,fields
#from openerp.osv import fields
from openerp.tools.translate import _
import time

class latinuxtarea_tarea(osv.osv):
    
    """ latinuxtarea """
    
    _name = 'latinuxtarea.tarea'
    _columns = {
        'user_id': fields.many2one('res.users', 'Creator', required=True, readonly=True),
        'name': fields.char('Task Summary', size=128, required=True, select=True),
        'date_create': fields.date('Create Date', select=True),
        'date_deadline': fields.date('Deadline',select=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'description': fields.text('Description', help='Task contents'),
        'target_id': fields.many2one('latinuxtarea.target','Target',required=True),
        'resource_ids': fields.one2many('latinuxtarea.recurso','task_id','Recursos'),
        #'product_id':fields.many2one('product.product', 'Product'),
        #'quantity':fields.integer('Quantity'),
        'state': fields.selection([('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')], 'State', readonly=True, required=True,
                                  help='If the task is created the state is \'Draft\'.\n If the task is started, the state becomes \'In Progress\'.\n If review is needed the task is in \'Pending\' state.\
                                  \n If the task is over, the states is set to \'Done\'.'),
        
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        #'quantity': lambda *a :0,
    }
    _order = 'date_create desc'
    
    #_sql_constraints = [('resource_uniq','unique(task_id,resource_id)', "Resource can't be duplicated!!")] #or just constraints?

    def do_open(self, cr, uid, ids, context={}):
        data = {'state': 'open'}
        self.write(cr, uid, ids, data, context=context)
        return True

    def do_draft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True
    
latinuxtarea_tarea()

class latinuxtarea_recurso(osv.osv):

    """ recursos usados en una tarea """

    _name = 'latinuxtarea.recurso'
    _columns = {
 	       'name':fields.many2one('product.product', 'Product'),
 	       'task_id':fields.many2one('latinuxtarea.tarea','Task',ondelete='cascade', select=True),
 	       'quantity':fields.integer('Quantity'),
 	       }

    _defaults = {
        	'quantity': lambda *a :0,
		}
    
    def accion(self,cr,uid,ids,context={}):
    	this=self.browse(cr,uid,ids,context=context)[0]
        return True
    
latinuxtarea_recurso()

class latinuxtarea_target(osv.osv):

    """ objetivos de las tareas """	

    def _get_progress_status(self,cr,uid,ids,fields,args,context):
    	"""" calculate target's progress status """
    	res={}
    	this=self.browse(cr,uid,ids,context=context)
    	tasks=self.pool.get('latinuxtarea.tarea')
    	for obj in this:
    	    total=len(obj.task_ids) or 1.0
	    res[obj.id]=0.0
	    cont=0
	    for tid in obj.task_ids:
    		task=tasks.read(cr,uid,tid.id,['state'])
    		if task['state'] in ('cancelled','done'):
    		    cont+=1
    		elif task['state'] in ('open','pending'):
    		    cont+=0.5   		
 	    res[obj.id]=(cont/total)*100
    		
    	return res
    	
    _name = 'latinuxtarea.target'
        
    _columns = {
            'name':fields.char('Name', size=64, required=True),
            'task_ids':fields.one2many('latinuxtarea.tarea', 'target_id', 'Task', required=False),
            'description':fields.text('Description'),# readonly=True, states={('draft','open','pending'): [('readonly', False)]}),
            'progress':fields.function(_get_progress_status,string='Progress',type='float',digits=(4,2)),
            }

latinuxtarea_target()
