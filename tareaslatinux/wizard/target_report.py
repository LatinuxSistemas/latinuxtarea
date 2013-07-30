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
               'report_type': 'pdf',
               'date_min': self._get_min_date(cr, uid, ids),
               'date_max': self._get_max_date(cr, uid, ids), 'detailed': False}
        return res

    _columns = {
            'report_file': fields.char('Nombre de Reporte', 128, readonly=False,
                                       help='No es necesario agregar la extensión del archivo'),
            'data': fields.binary('Reporte', readonly=True),
            'state': fields.selection([('choose','choose'), ('fin','fin')], string="estado"),
            'report_type': fields.selection([('pdf', 'Imprimir PDF'), ('csv', 'Imprimir CSV')], string='Tipo de reporte'),
            'date_min': fields.date('Fecha desde'),
            'date_max': fields.date('Fecha hasta'),
            'detailed': fields.boolean('Imprimir recursos?'),
            'target_ids': fields.many2many('lt.target', 'wiz_target_rel', 'target_id', 'wiz_id',
                                           'Filtar Objetivos', readonly=False)
    }

    def create_pdf(self, cr, uid, ids, context={}):
        this = self.browse(cr, uid, ids)[0]
        report_file = this.report_file + '.' + this.report_type
        self.write(cr, uid, ids, {'state': 'fin', 'report_file': report_file},
                   context=context)
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'lt.recurso.report.jasper',
                'datas': {
                    'model': 'lt.target',
                    'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                    'ids': context.get('active_ids') or [],
                    'report_type': this.report_type,
                    'form': this
                }
               }


    def create_target_report(self, cr, uid, ids, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Objetivos'+';'+ fec_reporte +'\n'*2
        this = self.browse(cr, uid, ids)[0]
        output = header.encode('latin1')
        targs = self.pool.get('lt.target')
        tasks = self.pool.get('lt.tarea')
        if not this.target_ids:
            tids = targs.search(cr, uid, [])
            targets = targs.browse(cr, uid, tids)
        else:
            tarids = [target.id for target in this.target_ids]
            targids = targs.search(cr, uid, [('id', 'in', tarids)])
            targets = targs.browse(cr, uid, targids)
        if not this.date_min:
            this.date_min = self._get_min_date(cr, uid, ids)
        if not this.date_max:
            this.date_min = self._get_max_date(cr, uid, ids)

        ##### HOJA DE REPORTE #####
        for target in targets:
            out = ('Nombre objetivo:' + ';' + target.name + '\n'+ ';' + 'Nombre Tarea' + ';'
            + 'Fecha Tarea' + ';' + 'Pedida por' + ';' + 'Doc. Ref.' + '\n')
            task_ids = tasks.search(cr, uid, ['&', ('date', '>=', this.date_min), '&',
                                              ('date', '<=', this.date_max),
                                              ('target_id', '=', target.id),
                                             ]
                                   )
            tasks_filter = tasks.browse(cr, uid, task_ids)
            cont = 0

            for task in tasks_filter:
                cont += task.tarea_amount_total
                out += (';' + task.name + ';' + task.date + ';' + (task.order_by or '')
                        + ';' + (task.reference or '') + '\n')
                if this.detailed:
                    out += ';'*2 + 'Nombre Recurso' + ';' + 'Cantidad'
                    for resource in task.resource_ids:
                        out += ';'*2 + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
            out += ';' + 'Total objetivo:' + ';'*5 + '$' + str(cont) + '\n'*2

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
        report_file = this.report_file + '.' + this.report_type
        return self.write(cr, uid, ids,
                          {'state': 'fin', 'data': salida, 'report_file': report_file},
                          context=context)

lt_target_report_wizard()
