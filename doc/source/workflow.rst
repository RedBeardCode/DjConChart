.. _`workflow`:

Workflow for creating control charts for new product
-----------------------------------------------------


To structure the different object I would seperate the objects in two levels. The
first is the product level this are more global datas which doesn't depend on
a single item furthermore they describe the item or the measurement.
The second level is the item level meaning this are data which are representing
a single item with the related measurement.

Objects which are belong to the product level are
 - :class:`~control_chart.models.Product`
 - :class:`~control_chart.models.MeasurementDevice`
 - :class:`~control_chart.models.MeasurementTag`
 - :class:`~control_chart.models.CalculationRule`
 - :class:`~control_chart.models.CharateristicValueDefinition`
 - :class:`~control_chart.models.MeasurementOrderDefinition`

And on the item level there are:
 - :class:`~control_chart.models.MeasurementItem`
 - :class:`~control_chart.models.MeasurementOrder`
 - :class:`~control_chart.models.Measurement`


Preparing the product level
^^^^^^^^^^^^^^^^^^^^^^^^^^^
To prepare DjConChart for measurements with a product you first have to fill the
data on product level. To give you a hint here is is a useful order. To get
a idea of the meaning of the different tables please have a look at :ref:`Overview`:

 - :ref:`Product <ProductItem>`
 - :ref:`MeasurementDevice <MeasurementDevice>`
 - :ref:`MesaurementTag <MeasurementTag>`
 - :ref:`CalculationRule <CalculationRule>`
 - :ref:`CharacteristicValueDefinition <CharacteristicValue>`
 - :ref:`MeasurementOrderDefinition <MeasurementOrder>`