.. _`Overview`:

Overview
--------

Important classes
^^^^^^^^^^^^^^^^^

To understand how to work with DjConChart you have to know some classes.
As a start I will introduce you this classes and afterwards I will describe
the workflow to see how the classes work together. For easier understanding I
will use the example of a restaurant which serves breakfast. Of course the best
selling dish are the famous Spam and Eggs.

.. _`ProductItem`:

Product and MeasurementItem
"""""""""""""""""""""""""""
The Product class represents the product not the single item you sell of a
product. In our example the product is the dish you offer for example
"Spam and egg" but not the plate you serve to your customer.

The plate on the other side is the MeasurementItem. So the MeasurementItem is
the instance of the a product with which you make the measurements.

.. _`MeasurementDevice`:

MeasurementDevice
"""""""""""""""""
Is simply the measurement device used to make a measurement like a scale to
measurement the amount of spam you serve.

.. _`CalculationRule`:

CalculationRule
"""""""""""""""
It is imported to be aware about the difference of raw data and the value you
want to control in a control chart. In DjConChart the values in the control
chart are called characteristic values. And the raw data are the results you
make in a measurement. For example the raw data can be the temperature profile
you recorded during frying the egg. Out of this values you can calculate some
different characteristic values like the average temperature, minimal
temperature or the duration of frying. The calculation rule wraps a python
function with calculates one characteristic value out of a set of raw data.

Of course if this rule changes all your existing value will be invalid and have
to be recalculated. This is handled by DjConChart. Also DjConChart has a
integrated versioning system for the calculation rules. So it is possible to see
who changed the rule and when as well as reverting the changing.

.. _`MeasurementTag`:

MeasurementTag
""""""""""""""
Some times you need more than one measurement to calculate a characteristic
value. For example you weight the spam and the eggs separately and out of this
values you want to calculate the weight of the whole dish. So you have two
measurements and to distinguish them you use the MeasurementTag. In our example
you could use the tags "spam" and "egg" to distinguish the two measurements.

If you don't need multiple measurements for a characteristic value you don't
have to add a tag to the measurement.

.. _`CharacteristicValue`:

CharacteristicValueDefinition and CharacteristicValue
"""""""""""""""""""""""""""""""""""""""""""""""""""""
The characteristic values are the value you want to control in a control chart.
Each value belongs to one measurement item and is one point in the graph.
CharacteristicValueDefinition defines a kind of charateristic values. For
example you would make one CharateristicValueDefinition for the weight of spam
and one for the weight of the eggs and one for the weight of the whole dish.
The definition has a name like "Weight of spam" and is connected to a
calculation rule.

.. _`MeasurementOrder`:

MeasurementOrderDefinition and MeasurementOrder
"""""""""""""""""""""""""""""""""""""""""""""""
The MeasurementOrderDefinition defines which measurement have to be made with
one measurement item and the MeasurementOrder links one measurement item with
one MeasurementOrderDefinition.
For our restaurant example we would create one MeasurementOrderDefinition for
all spam and eggs which defines that we have to weight the spam and the eggs but
not the whole dish because it will be calculated out of the sum. And than we
will create a MeasurementOrder for each dish we serve. So the dish is linked
with the order definition and it is defined which measurements have to be taken.

.. _`Measurement`:

Measurement
"""""""""""
Represents the real measurement with all information like the date, user,
used measurement device and so on and of course the raw data.





