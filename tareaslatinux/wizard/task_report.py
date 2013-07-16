# -*- coding: latin1 -*-

import base64
import os
import subprocess
#import wizard
from openerp.osv import fields, osv
import time
#import openerp.netsvc as netsvc
import logging

class lt_task_report_wizard(osv.osv_memory):
    _name = "lt.task.report.wizard"
    _description = "Crear Reporte de Tareas"

    def _get_min_date(self, cr, uid, ids, context={}):
        target_obj =  self.pool.get('lt.tarea')
        target_id = target_obj.search(cr, uid, [], order='date_create')
        date_min = target_obj.read(cr, uid, [target_id[0]], ['date_create'])[0]['date_create']
        return date_min

    def _get_max_date(self, cr, uid, ids, context={}):
        target_obj =  self.pool.get('lt.tarea')
        target_id = target_obj.search(cr, uid, [], order='date_create')
        date_max = target_obj.read(cr, uid, [target_id[-1]], ['date_create'])[0]['date_create']
        return date_max

    def default_get(self, cr, uid, ids, fields, context={}):
        file1 = os.path.expanduser('~') + '/task_report.csv'
        if not os.path.exists(file1):
            os.system('touch %s' % file1)
        report_file = open(file1, 'rb')
        res = {'state': 'choose', 'data': base64.encodestring(report_file.read()),
               'report_file': file1, 'date_min': self._get_min_date(cr, uid, ids),
               'date_max': self._get_max_date(cr, uid, ids), 'detailed': False}
        return res

    _columns = {
            'report_file': fields.char('Nombre de Reporte', 64, readonly=False),
            'state': fields.selection([('choose','choose'), ('fin','fin')], string="estado"),
            'date_min': fields.date('Fecha desde'),
            'date_max': fields.date('Fecha hasta'),
            'detailed': fields.boolean('Imprimir recursos?'),
            'target_ids': fields.many2many('lt.target', 'wiz_target_rel', 'target_id', 'wiz_id',
                                           'Filtar Objetivos', readonly=False)
    }

    def onchange_report_file(self, cr, uid, ids, new_name, context={}):
        if not os.path.exists(new_name):
            os.system('touch %s' % new_name)
        res = { 'report_file': new_name }
        return res

    def _get_all_targets(self, cr, uid, ids, context={}):
        targets = self.pool.get('lt.target')
        tids = targets.search(cr, uid, [])
        target_obj = targets.browse(cr, uid, tids)
        return target_obj

    def open_report(self, cr, uid, ids, context={}):
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(cr, uid, [])

        this = self.browse(cr, uid, ids)[0]
        subprocess.Popen([config.path_to_office, this.report_file])
        pass

    def create_task_report(self, cr, uid, ids, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Tareas'+';'+ fec_reporte +'\n'*2 + ';'*3 + 'Fecha Tarea' + '\n'
        this = self.browse(cr, uid, ids)[0]
        output = header.encode('latin1')
        targs = self.pool.get('lt.target')
        tasks = self.pool.get('lt.tarea')
        if not this.target_ids:
            this.target_ids = self._get_all_targets(cr, uid, ids)
        tarids = [target.id for target in this.target_ids]
        print tarids
        targids = targs.search(cr, uid, [('id', 'in', tarids)])
        targets = targs.browse(cr, uid, targids)
        if not this.date_min:
            this.date_min = self._get_min_date(cr, uid, ids)
        if not this.date_max:
            this.date_min = self._get_max_date(cr, uid, ids)

        ##### HOJA DE REPORTE #####
        for target in targets:
            out = 'Nombre objetivo:' + ';' + target.name + '\n'
            task_ids = tasks.search(cr, uid, ['&', ('date_create', '>=', this.date_min), '&',
                                              ('date_create', '<=', this.date_max),
                                              ('target_id', '=', target.id),
                                             ]
                                   )
            print task_ids
            tasks_filter = tasks.browse(cr, uid, task_ids)
            cont = 0

            for task in tasks_filter:
                cont += task.tarea_amount_total
                out += ';' + 'Tarea:' + ';' + task.name + ';' + task.date_create + '\n'
                if this.detailed:
                    for resource in task.resource_ids:
                        out += ';'*2 + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
            out += ';' + 'Total:' + ';'*3 + '$' + str(cont) + '\n'*2

            try:
                if isinstance(out, unicode):
                    output += out.encode('latin1')
                else:
                    output += output
            except UnicodeEncodeError:
                logger.warn("""Problemas con caracteres ascii en el objetivo (id: %i),
                               esta linea del reporte se pasa por alto!""" % target.id, exc_info=1)

        with open(this.report_file, 'w') as report:
            report.write(output)
        dicc = {'state':'fin'}
        return self.write(cr, uid, ids, dicc, context=context)

lt_task_report_wizard()
