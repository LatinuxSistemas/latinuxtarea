# -*- coding: latin1 -*-

import base64
import time

from openerp.osv import fields, osv
import logging

class lt_target_report_wizard(osv.osv_memory):
    _name = "lt.target.report.wizard"
    _description = "Crear Reporte de Objetivos"

    def _get_min_date(self, cr, uid, ids, context={}):
        target_obj =  self.pool.get('lt.tarea')
        target_id = target_obj.search(cr, uid, [], order='date')
        if target_id:
            date_min = target_obj.read(cr, uid, [target_id[0]], ['date'])[0]['date']
        else:
            date_min = time.strftime("%Y-%m-%d %H:%M:%S")
        return date_min

    def _get_max_date(self, cr, uid, ids, context={}):
        target_obj =  self.pool.get('lt.tarea')
        target_id = target_obj.search(cr, uid, [], order='date')
        if target_id:
            date_max = target_obj.read(cr, uid, [target_id[-1]], ['date'])[0]['date']
        else:
            date_max = time.strftime("%Y-%m-%d %H:%M:%S")
        return date_max

    def default_get(self, cr, uid, ids, fields, context={}):
        file1 = 'target_report'
        res = {'state': 'choose', 'report_file': file1,
               'report_type': 'csv',
               'date_min': self._get_min_date(cr, uid, ids),
               'date_max': self._get_max_date(cr, uid, ids), 'detailed': False}
        return res

    _columns = {
            'report_file': fields.char('Report Name', 128, readonly=False,
                                       help='File extension is not needed'),
            'data': fields.binary('Reporte', readonly=True),
            'state': fields.selection([('choose','choose'), ('fin','fin')], string="State"),
            'report_type': fields.selection([('pdf', 'Print PDF'), ('csv', 'Print CSV')], string='Report Type'),
            'date_min': fields.date('Start Date'),
            'date_max': fields.date('Finish Date'),
            'detailed': fields.boolean('Print Resources ?'),
            'target_ids': fields.many2many('lt.target', 'wiz_target_rel', 'target_id', 'wiz_id',
                                           'Target Filter', readonly=False)
    }

    def create_target_report(self, cr, uid, ids, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Objetivos'+';'+ fec_reporte +'\n'*2
        this = self.browse(cr, uid, ids)[0]
        output = header.encode('latin1')
        targs = self.pool.get('lt.target')
        tasks = self.pool.get('lt.tarea')
        report_file = this.report_file + '.' + this.report_type
        if not this.target_ids:
            tarids = targs.search(cr, uid, [])
            targets = targs.browse(cr, uid, tarids)
        else:
            tarids = [target.id for target in this.target_ids]
            targids = targs.search(cr, uid, [('id', 'in', tarids)])
            targets = targs.browse(cr, uid, targids)
        if not this.date_min:
            this.date_min = self._get_min_date(cr, uid, ids)
        if not this.date_max:
            this.date_min = self._get_max_date(cr, uid, ids)
        if this.report_type == 'pdf':
            t = []
            for target in targets:
                [t.append(lt.id) for lt in target.task_ids if
                 time.strptime(lt.date[0:10], "%Y-%m-%d") >= time.strptime(this.date_min[0:10], "%Y-%m-%d")
                 and time.strptime(lt.date[0:10], "%Y-%m-%d") <= time.strptime(this.date_max[0:10], "%Y-%m-%d")]
            self.write(cr, uid, ids, {'state': 'fin', 'report_file': report_file},
                       context=context)
            return {
                    'type': 'ir.actions.report.xml',
                    'in-format': 'oo-odt',
                    'parser-state': 'default',
                    'tml-source': 'database',
                    'report_name': 'lt.target.jasper',
                    'datas': {
                        'model': 'lt.tarea',
                        'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                        'ids': t,
                        'report_type': this.report_type,
                    }
                   }

        ##### HOJA DE REPORTE CSV #####
        for target in targets:
            out = ('Target Name:' + ';' + target.name + '\n'+ ';' + 'Task Name' +
                   ';' + 'Description' + ';' + 'Task Date' + ';' + 'Order By' + ';' +
                   'Ref. Doc.' + '\n')
            task_ids = tasks.search(cr, uid, ['&', ('date', '>=', this.date_min), '&',
                                              ('date', '<=', this.date_max),
                                              ('target_id', '=', target.id),
                                             ]
                                   )
            tasks_filter = tasks.browse(cr, uid, task_ids)
            cont = 0

            for task in tasks_filter:
                cont += task.tarea_amount_total
                date = time.strftime('%d/%m/%Y', time.strptime(task.date, '%Y-%m-%d %H:%M:%S'))
                out += (';' + task.name + ';' + (task.description or '') +
                        ';' + date + ';' + (task.order_by or '') + ';' +
                        (task.reference or '') + '\n')
                if this.detailed:
                    out += ';'*2 + 'Resource Name' + ';' + 'Quantity'
                    for resource in task.resource_ids:
                        out += ';'*2 + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
            out += ';' + 'Total (target):' + ';'*5 + '$' + str(cont) + '\n'*2

            try:
                if isinstance(out, unicode):
                    output += out.encode('latin1')
                else:
                    output += output
            except UnicodeEncodeError:
                logger.warn("""Problemas con caracteres ascii en el objetivo (id: %i),
                               esta linea del reporte se pasa por alto!""" % target.id, exc_info=1)
        try:
            salida = base64.encodestring(output)
        except UnicodeEncodeError, data:
            logger.warn("Error en el reporte, se deja sin completar!\n%s" % data, exc_info=1)
            salida = ''
        return self.write(cr, uid, ids,
                          {'state': 'fin', 'data': salida, 'report_file': report_file},
                          context=context)

lt_target_report_wizard()
