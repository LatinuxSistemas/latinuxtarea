# -*- coding: latin1 -*-

import base64
import os
#import wizard
from openerp.osv import fields, osv
import time
#import openerp.netsvc as netsvc
import logging


class lt_task_report_wizard(osv.osv_memory):

    _name = "lt.task.report.wizard"
    _description = "Crear Reporte de Tareas"

    def default_get(self, cr, uid, ids, fields, context={}):
#        this = self.browse(cr, uid, ids)
#        print this
        file1 = os.path.expanduser('~') + '/task_report.csv'
        if not os.path.exists(file1):
            os.system('touch %s' % file1)
        report_file = open(file1, 'rb')
        res = {'state': 'choose', 'data': base64.encodestring(report_file.read()), 'report_file': file1}
        return res


    _columns = {
#            'data': fields.binary('Archivo', readonly=True),
            'report_file': fields.char('Nombre de Reporte', 64, readonly=False),
            'state': fields.selection([('choose','choose'), ('fin','fin')], string="estado"),
            'date_min': fields.date('Fecha desde'),
            'date_max': fields.date('Fecha hasta')
    }

    _defaults = {
            'state': 'choose',
            'report_file': lambda *a: 'task_report.csv'
    }

    def onchange_report_file(self, cr, uid, ids, new_name, context={}):
        if not os.path.exists(new_name):
            os.system('touch %s' % new_name)
        res = { 'report_file': new_name }
        return res

    def _get_min_and_max_dates(self, cr, uid, ids, context={}):
        pass

    def create_task_report(self, cr, uid, ids, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Tareas'+';'+ fec_reporte +'\n'*2 + ';'*2 + 'Fecha Tarea' + '\n'
        this = self.browse(cr,uid,ids)[0]
        output = header.encode('latin1')
        targs = self.pool.get('lt.target')
        tasks = self.pool.get('lt.tarea')
        targids = targs.search(cr,uid,[])
        targets = targs.browse(cr,uid,targids)
        if not this.date_min:
            this.date_min = self._get_min_and_max_dates()[0]
        if not this.date_max:
            this.date_min = self._get_min_and_max_dates()[1]

        ##### HOJA DE REPORTE #####
        for target in targets:
            out = 'Nombre objetivo:' + ';' + target.name + '\n'
            task_ids = tasks.search(cr, uid, ['&', ('date_create', '>=', this.date_min), '&',
                                              ('date_create', '<=', this.date_max),
                                              ('target_id', '=', target.id),
                                              ])
            print task_ids
            tasks_filter = tasks.browse(cr, uid, task_ids)
            cont = 0

            for task in tasks_filter:
                cont += task.tarea_amount_total
                out += ';' + 'Tarea:' + ';' + task.name + ';' + task.date_create + '\n'
#                i = 1
                for resource in task.resource_ids:
#                    out += ';'*2 + 'Recurso %i:'%i + ';' + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
                    out += ';'*2 + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
#                    i += 1
            out += ';' + 'Total:' + ';'*3 + '$' + str(cont) + '\n'*2

            try:
                if isinstance(out, unicode):
                    output += out.encode('latin1')
                else:
                    output += output
            except UnicodeEncodeError:
                logger.warn("""Problemas con caracteres ascii en el objetivo (id: %i),
                               esta linea del reporte se pasa por alto!""" % target.id, exc_info=1)
#        try:
#            salida = base64.encodestring(output)
#        except UnicodeEncodeError:
#            logger.warn("Error en el reporte, se deja sin completar!", exc_info=1)
#            salida = ''
#        print this.report_file
        with open(this.report_file, 'w') as report:
            report.write(output)

        #dicc = {'state':'fin', 'data': this.report_file, 'report_file': this.report_file}
        dicc = {'state':'fin'}
 #       return self.write(cr, uid, ids, {'state':'fin', 'data': salida, 'name': this.name}, context=context )
        return self.write(cr, uid, ids, dicc, context=context)
#        print dicc
#        return {'value': dicc}

lt_task_report_wizard()
