# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from trytond.pool import Pool
from . import quality


def register():
    Pool.register(
        quality.Template,
        quality.QuantitativeTemplateLine,
        quality.Test,
        quality.QuantitativeTestLine,
        module='quality_control_formula', type_='model')
