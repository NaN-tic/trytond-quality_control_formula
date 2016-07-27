# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from simpleeval import simple_eval
from trytond.model import fields, Unique
from trytond.pool import PoolMeta
from trytond.pyson import Bool, Eval

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
        help='Name must follow the next rules: \n'
        '\t* Must begin with a letter (a - z, A - B) or underscore (_)\n'
        '\t* Other characters can be letters, numbers or _ \n'
        '\t* It iss Case Sensitive and can be any (reasonable) length \n'
        '\t* There are some reserved words which you cannot use as a '
        'variable name because Python uses them for other other things')

    @classmethod
    def __setup__(cls):
        super(QuantitativeTemplateLine, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('template_line_name_uniq', Unique(t, t.template, t.formula_name),
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
            return None
        vals = {}
        for line in self.quantitative_lines:
            if line.formula_name:
                vals[line.formula_name] = line.value or 0
        try:
            value = simple_eval(self.formula, *vals)
            return value
        except NameError:
            pass

    def set_template_vals(self):
        super(Test, self).set_template_vals()
        self.formula = self.template.formula
        self.unit = self.template.unit

    def apply_template_values(self):
        super(Test, self).apply_template_values()
        for template in self.templates:
            self.formula = template.formula
            self.unit = template.unit


class QuantitativeTestLine:
    __name__ = 'quality.quantitative.test.line'

    formula_name = fields.Char('Formula Name')

    @classmethod
    def __setup__(cls):
        super(QuantitativeTestLine, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('test_line_name_uniq', Unique(t, t.test, t.formula_name),
                'Formula Name of Line can be used only once on Template.'),
            ]

    def set_template_line_vals(self, template_line):
        super(QuantitativeTestLine, self).set_template_line_vals(template_line)
        self.formula_name = template_line.formula_name
