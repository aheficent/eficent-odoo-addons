# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm


class StockMove(orm.Model):

    _inherit = "stock.move"

    def create(self, cr, uid, vals, context=None):
        src_loc = self.pool.get('stock.location').browse(
            cr, uid, vals['location_id'])
        dest_loc = self.pool.get('stock.location').browse(
            cr, uid, vals['location_dest_id'])
        add_analytic_id = False
        # if both has AA error will raise so no need to check here
        if src_loc.analytic_account_id and src_loc.usage == 'internal':
            add_analytic_id = src_loc.analytic_account_id.id
        if dest_loc.analytic_account_id and dest_loc.usage == 'internal':
            add_analytic_id = dest_loc.analytic_account_id.id
        if add_analytic_id:
            vals['analytic_account_id'] = add_analytic_id
        return super(StockMove, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        check_analytic = False
        for move in self.pool.get('stock.move').browse(cr, uid, ids, context):
            if 'location_id' in vals:
                src_loc = self.pool.get('stock.location').browse(cr, uid, [vals['location_id']])[0]
                check_analytic = True
            else:
                src_loc = move.location_id

            if 'location_dest_id' in vals:
                dest_loc = self.pool.get('stock.location').browse(
                    cr, uid, [vals['location_dest_id']])[0]
                check_analytic = True
            else:
                dest_loc = move.location_dest_id

            if check_analytic:
                add_analytic_id = False
                # if both has AA error will raise so no need to check here
                if src_loc.analytic_account_id and src_loc.usage == 'internal':
                    add_analytic_id = src_loc.analytic_account_id.id
                if dest_loc.analytic_account_id and dest_loc.usage == 'internal':
                    add_analytic_id = dest_loc.analytic_account_id.id
                if add_analytic_id:
                    vals['analytic_account_id'] = add_analytic_id
        return super(StockMove, self).write(
            cr, uid, ids, vals, context=context)

    def _check_analytic_account(self, cr, uid, ids, context=None):
        # for move in self.browse(cr, uid, ids):
        #     if move.location_id and move.location_dest_id:
        #         if move.location_id.analytic_account_id and move.location_dest_id.analytic_account_id:
        #             if move.location_id.analytic_account_id.id != move.location_dest_id.analytic_account_id.id:
        #                 return False
        return True

    def _check_analytic(self, cr, uid, ids, context=None):
        # for move in self.browse(cr, uid, ids):
        #     if move.analytic_account_id:
        #         if ((move.location_id.analytic_account_id ==
        #                 move.analytic_account_id)
        #             or (move.location_dest_id.analytic_account_id ==
        #                 move.analytic_account_id)):
        #             return True
        #         else:
        #             return False
        return True

    _constraints = [(_check_analytic_account,
                     "Cannot move between different projects locations, "
                     "please move first to general stock",
                     ['location_id', 'location_dest_id']),
                    (_check_analytic,
                     "The analytic account in the move and in"
                     " the destination location does not match",
                     ['analytic_account_id', 'location_dest_id'])]
