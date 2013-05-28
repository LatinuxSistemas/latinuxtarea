# -*- coding: latin1 -*-

import base64
from openerp.osv import fields, osv
#from tools.translate import _
import time 
import openerp.netsvc as netsvc

class lt_task_report_wizard(osv.osv_memory):
    
    _name = "lt.task.report.wizard"
    _description = "Crear Reporte de Tareas"
    _columns = {
    		'data': fields.binary('Archivo',readonly=True),
                'name': fields.char('Nombre de Reporte',64, readonly=False),
                'state':fields.selection([('choose','choose'),('fin','fin')],string="estado"),
                }
                
    _defaults={
    		'state':'choose',
    		'name':lambda *a: 'task_report.csv'
    		}
    
    def create_task_report(self,cr,uid,ids,context={}):
	
	logger=netsvc.Logger()                
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Tareas'+';'+ fec_reporte +'\n'*2
        this=self.browse(cr,uid,ids)[0]
        output=header.encode('latin1')
        targs=self.pool.get('latinuxtarea.target')
        targids=targs.search(cr,uid,[])
        targets=self.pool.get('latinuxtarea.target').browse(cr,uid,targids)
	tasks=self.pool.get('latinuxtarea.tarea')
	resources=self.pool.get('latinuxtarea.recurso')
	
        ##### HOJA DE REPORTE #####
	
	for target in targets:		
            out='Nombre objetivo:'+';'+target.name+'\n'
	    actual_tasks=tasks.search(cr,uid,[('target_id','=',target.id)])
	    cont=0
	    print actual_tasks
            for task_id in actual_tasks:
            	task=tasks.browse(cr,uid,task_id)
            	#print task
            	out+=';'+'Tarea:'+';'+task.name+';'+task.date_create+'\n'
            	actual_resources=resources.search(cr,uid,[('task_id','=',task.id)])
            	i=1            	
            	for res_id in actual_resources:
            	    resource=resources.browse(cr,uid,res_id)
            	    out+=';'*2+'Recurso %i:' %i+';'+resource.name.name_template+';'+repr(resource.quantity)+'\n'
            	    i+=1
            	    cont+=resource.quantity
            
            out+=';'+'Total'+';'*3+str(cont)+'\n'*2
            
            try:
                if isinstance(out,unicode):
                    output+=out.encode('latin1')
                else:
                    output+=out
            except UnicodeEncodeError,data:                
                logger.notifyChannel("warning", netsvc.LOG_WARNING,'Problemas con caracteres ascii en la factura (id: %i), esta linea del reporte se pasa por alto!\n%s' % (idfac,data))
                     
        try:    
            salida=base64.encodestring(output)           
	except UnicodeEncodeError,data:
	    logger.notifyChannel("warning", netsvc.LOG_WARNING,"Error en el reporte, se deja sin completar!\n%s" % data)
	    salida=''
	    
        return self.write(cr, uid, ids, {'state':'fin', 'data':salida, 'name':this.name}, context=context)
       
lt_task_report_wizard()
