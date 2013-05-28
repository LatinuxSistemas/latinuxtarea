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
from openerp.tools.translate import _
import time

class lt_tarea(osv.osv):
    
    """ latinuxtarea """
    
    _name = 'lt.tarea'
    _columns = {
        'user_id': fields.many2one('res.users', 'Creator', required=True, readonly=True),
        'name': fields.char('Task Name', size=128, required=True, select=True),
        'date_create': fields.date('Create Date', select=True),
        'date_deadline': fields.date('Deadline',select=True),        
        'description': fields.text('Description', help='Task contents'),
        'target_id': fields.many2one('lt.target','Target',required=True),
        'resource_ids': fields.one2many('lt.recurso','task_id','Recursos'),
        'state': fields.selection([('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')], 'State', readonly=True, required=True, help='When the task is created the state is \'Draft\'.\n If the task is started, the state becomes \'In Progress\'.\n If review is needed the task is in \'Pending\' state.\n If the task is over, the states is set to \'Done\'.'),    	
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

    _name = 'lt.recurso'
    _columns = {
 	       'name':fields.many2one('product.product', 'Product',required=True),
 	       'task_id':fields.many2one('lt.tarea','Task',ondelete='cascade', select=True),
 	       'quantity':fields.integer('Quantity'), 	       
 	       }

    _defaults = {
        	'quantity': lambda *a :1,
        	}
		
    _sql_constraints = [
    ('resource_uniq','unique(name,task_id)', "Resource must be unique per task!\nSUGERENCIA: hay un recurso ya ha sido agregado, solo modifique su cantidad"),
    ]
    
    #def onchange_name(self,cr,uid,ids,prod_id,tid,context={}):
    #	print "entra"
	#res={}
    	#objs=self.browse(cr,uid,ids)
    	#for obj in objs:
    	#    if (prod_id,tid) == (obj.name,obj.task_id):
    	#	res[obj.id]={'state':'error'}
    	#	break
    	#    else:
    	    	#self.write(cr,uid,obj.id,{'state':'done'},)
    	#	res[obj.id]={'state':'done'}    			
#    	task=self.pool.get('latinuxtarea.tarea').read(cr,uid,this.task_id,context=context)    	
    	#return res
    
    def accion(self,cr,uid,ids,context={}):
    	#this=self.browse(cr,uid,ids,context=context)[0]
        return True
    
lt_recurso()

class lt_target(osv.osv):

    """ objetivos de las tareas """	

    def _get_progress_status(self,cr,uid,ids,fields,args,context):
    	"""" calculate target's progress status """
    	res={}
    	this=self.browse(cr,uid,ids,context=context)
    	tasks=self.pool.get('lt.tarea')
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
    	
    _name = 'lt.target'
        
    _columns = {
            'name':fields.char('Name', size=64, required=True),
            'task_ids':fields.one2many('lt.tarea', 'target_id', 'Task', required=False),
            'description':fields.text('Description'),# readonly=True, states={('draft','open','pending'): [('readonly', False)]}),
            'partner_id': fields.many2one('res.partner', 'Partner', required=True),
            'location':fields.char('Ubicación',size=150,required=False),
            'progress':fields.function(_get_progress_status,string='Progress State',type='float',digits=(4,2)),
            }
            
    def onchange_partner(self,cr,uid,ids,partner_id,context={}):
    	
    	#partner=self.pool.get('res.partner').browse(cr,uid,partner_id,context)
    	addresses=self.pool.get('res.partner.address')
#    	print addresses
	location='sin definir'
	if addresses:
    	    address_id=addresses.search(cr,uid,[('partner_id','=',partner_id)])
    	    address=addresses.browse(cr,uid,address_id)[0]
    	    print address
    	    location=(address.city or '') + ((', ' + address.state_id.name )or '') + ((', ' + address.country_id.name )or '')
    	    print "HOLA!!", address, location
    	
	return {'value':{'location':location}}
lt_target()
