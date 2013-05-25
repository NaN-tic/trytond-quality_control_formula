================
Test Scenario
================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install quality_test module::

    >>> Module = Model.get('ir.module.module')
    >>> quality_test_module, = Module.find(
    ...     [('name', '=', 'quality_control_formula')])
    >>> Module.install([quality_test_module.id], config.context)
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='US Dollar', symbol=u'$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[]',
    ...         mon_decimal_point='.')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find([])

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.cost_price = Decimal('25')
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Create Quality Configuration::

    >>> Sequence = Model.get('ir.sequence')
    >>> sequence = Sequence.find([('code','=','quality.test')])[0]
    >>> Configuration = Model.get('quality.configuration')
    >>> configuration = Configuration()
    >>> configuration.name = 'Configuration'
    >>> Product = Model.get('product.product')
    >>> ConfigLine = Model.get('quality.configuration.line')
    >>> config_line = ConfigLine()
    >>> configuration.allowed_documents.append(config_line)
    >>> config_line.quality_sequence = sequence
    >>> models = Model.get('ir.model')
    >>> allowed_doc, = models.find([('model','=','product.product')])
    >>> config_line.document = allowed_doc
    >>> configuration.save()

Create Quantitative Proof::
    
    >>> Proof = Model.get('quality.proof')
    >>> Method = Model.get('quality.proof.method')
    >>> qtproof = Proof(name='Quantitative Proof', type='quantitative')
    >>> method2 = Method(name='Method 2')
    >>> qtproof.methods.append(method2)
    >>> qtproof.save()

Look For Values::
    
    >>> method2, = Method.find([('name', '=', 'Method 2')])

Create Template, Template1::
    
    >>> Template = Model.get('quality.template')
    >>> template=Template()
    >>> template.name = 'Template 1'
    >>> template.document = product
    >>> template.internal_description='Internal description'
    >>> template.external_description='External description'
    >>> QtTemplateLine = Model.get('quality.quantitative.template.line')
    >>> qt_line = QtTemplateLine()
    >>> qt_line.name = 'line1'
    >>> qt_line.formula_name = 'line1'
    >>> qt_line.sequence = 1
    >>> qt_line.proof = qtproof
    >>> qt_line.method = method2
    >>> qt_line.unit = unit
    >>> qt_line.unit_range = unit
    >>> qt_line.internal_description = 'quality line intenal description'
    >>> qt_line.external_description = 'quality line external description'
    >>> qt_line.min_value = Decimal('1.00')
    >>> qt_line.max_value = Decimal('2.00')
    >>> template.quantitative_lines.append(qt_line)
    >>> QtTemplateLine = Model.get('quality.quantitative.template.line')
    >>> qt_line2 = QtTemplateLine()
    >>> qt_line2.name = 'line2'
    >>> qt_line2.formula_name = 'line2'
    >>> qt_line2.sequence = 1
    >>> qt_line2.proof = qtproof
    >>> qt_line2.method = method2
    >>> qt_line2.unit = unit
    >>> qt_line2.unit_range = unit
    >>> qt_line2.internal_description = 'quality line intenal description'
    >>> qt_line2.external_description = 'quality line external description'
    >>> qt_line2.min_value = Decimal('3.00')
    >>> qt_line2.max_value = Decimal('5.00')
    >>> template.quantitative_lines.append(qt_line2)
    >>> template.formula='(line1+line2)*2'
    >>> template.save()
    >>> template.reload()

Create And assing template to Test::
    
    >>> Test = Model.get('quality.test')
    >>> test=Test()
    >>> test.name = 'TEST/'
    >>> test.document = product
    >>> test.template = template 
    >>> test.save()
    >>> Test.set_template([test.id], config.context)

Check Unsuccess on Test Line::
    
    >>> test.reload()
    >>> test.quantitative_lines[0].success
    False
    >>> test.success
    False

Check Success on Test Line::
    >>> TestLines = Model.get('quality.quantitative.test.line')
    >>> line1,line2, = TestLines.find([])
    >>> line1.value = Decimal('1.00')
    >>> line1.unit = unit
    >>> line1.save()
    >>> line2.reload()
    >>> line1.success
    True
    >>> line2.value = Decimal('4.00')
    >>> line2.unit = unit
    >>> line2.save()
    >>> line2.reload()
    >>> line2.success
    True
    >>> line2.success
    True
    >>> test.save()
    >>> test.reload()
    >>> test.formula
    u'(line1+line2)*2'
    >>> test.formula_result
    10.0
   
Confirm Test::
    
    >>> test.save()
    >>> test.state
    u'draft'
    >>> Test.confirmed([test.id], config.context)
    >>> test.reload()
    >>> test.state
    u'confirmed'
