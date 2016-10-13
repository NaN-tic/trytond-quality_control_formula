# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval
from trytond.tools import safe_eval

__metaclass__ = PoolMeta


__all__ = ['Template', 'QuantitativeTemplateLine', 'Test',
    'QuantitativeTestLine']


class Template:
    __name__ = 'quality.template'

    formula = fields.Text('Formula')
    unit = fields.Many2One('product.uom', 'Unit',
        states={
            'required': Bool(Eval('formula')),
            },
        depends=['formula'])
    unit_digits = fields.Function(fields.Integer('Unit Digits'),
        'on_change_with_unit_digits')

    @fields.depends('unit')
    def on_change_with_unit_digits(self, name=None):
        if not self.unit:
            return 2
        return self.unit.digits


class QuantitativeTemplateLine:
    __name__ = 'quality.quantitative.template.line'

    formula_name = fields.Char('Formula Name',
        help='Name must follow the following rules: \n'
        '\t* Must begin with a letter (a - z, A - B) or underscore (_)\n'
        '\t* Other characters can be letters, numbers or _ \n'
        '\t* It is Case Sensitive and can be any (reasonable) length \n'
        '\t* There are some reserved words which you cannot use as a '
        'variable name because Python uses them for other other things')

    @classmethod
    def __setup__(cls):
        super(QuantitativeTemplateLine, cls).__setup__()
        cls._sql_constraints = [
            ('template_line_name_uniq', 'UNIQUE(template, formula_name)',
                'Formula Name of Line can be used only once on Template.'),
            ]


class Test:
    __name__ = 'quality.test'

    formula = fields.Text('Formula', readonly=True)
    unit = fields.Many2One('product.uom', 'Unit',
        states={
            'required': Bool(Eval('formula')),
            },
        depends=['formula'])
    unit_digits = fields.Function(fields.Integer('Unit Digits'),
        'on_change_with_unit_digits')
    formula_result = fields.Function(fields.Float('Formula Result',
            digits=(16, Eval('unit_digits', 2)), depends=['unit_digits']),
        'get_formula_result')

    @fields.depends('unit')
    def on_change_with_unit_digits(self, name=None):
        if not self.unit:
            return 2
        return self.unit.digits

    def get_formula_result(self, name=None):
        if not self.formula:
            return
        vals = {}
        for line in self.quantitative_lines:
            if line.formula_name:
                vals[line.formula_name] = line.value or 0
        try:
            value = safe_eval(self.formula, vals)
            return value
        except (NameError, ZeroDivisionError):
            pass

    def apply_template_values(self):
        super(Test, self).apply_template_values()
        for template in self.templates:
            if template.formula:
                self.formula = template.formula
                self.unit = template.unit
                break


class QuantitativeTestLine:
    __name__ = 'quality.quantitative.test.line'

    formula_name = fields.Char('Formula Name')

    @classmethod
    def __setup__(cls):
        super(QuantitativeTestLine, cls).__setup__()
        cls._sql_constraints = [
            ('test_line_name_uniq', 'UNIQUE(test, formula_name)',
                'Formula Name of Line can be used only once on Template.'),
            ]

    def set_template_line_vals(self, template_line):
        super(QuantitativeTestLine, self).set_template_line_vals(template_line)
        self.formula_name = template_line.formula_name
