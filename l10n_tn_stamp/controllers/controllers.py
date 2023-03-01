# -*- coding: utf-8 -*-
# from odoo import http


# class TimbreFiscal(http.Controller):
#     @http.route('/timbre_fiscal/timbre_fiscal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/timbre_fiscal/timbre_fiscal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('timbre_fiscal.listing', {
#             'root': '/timbre_fiscal/timbre_fiscal',
#             'objects': http.request.env['timbre_fiscal.timbre_fiscal'].search([]),
#         })

#     @http.route('/timbre_fiscal/timbre_fiscal/objects/<model("timbre_fiscal.timbre_fiscal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('timbre_fiscal.object', {
#             'object': obj
#         })
