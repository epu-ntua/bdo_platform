# -*- coding: utf-8 -*-
from __future__ import unicode_literals


MATH_FUNCTIONS = [
 {'name': 'abs(x)', 'description': 'Absolute value. Example usage: abs(-17.4)=17.4'},
 {'name': 'cbrt(dp)', 'description': 'Cube root. Example usage: cbrt(27.0)=3'}, {'name': 'ceil(dpΒ\xa0orΒ\xa0numeric)',
                                                                                 'description': 'Nearest integer greater than or equal to argument. Example usage: ceil(-42.8)=-42'},
 {'name': 'ceiling(dpΒ\xa0orΒ\xa0numeric)',
  'description': 'Nearest integer greater than or equal to argument (same asΒ\xa0ceil). Example usage: ceiling(-95.3)=-95'},
 {'name': 'degrees(dp)', 'description': 'Radians to degrees. Example usage: degrees(0.5)=286.478.897.565.412'},
 {'name': 'div(yΒ\xa0numeric,Β\xa0xΒ\xa0numeric)',
  'description': 'Integer quotient ofΒ\xa0y/x. Example usage: div(9,4)=2'},
 {'name': 'exp(dpΒ\xa0orΒ\xa0numeric)', 'description': 'Exponential. Example usage: exp(1.0)=271.828.182.845.905'},
 {'name': 'floor(dpΒ\xa0orΒ\xa0numeric)',
  'description': 'Nearest integer less than or equal to argument. Example usage: floor(-42.8)=-43'},
 {'name': 'ln(dpΒ\xa0orΒ\xa0numeric)', 'description': 'Natural logarithm. Example usage: ln(2.0)=0.693147180559945'},
 {'name': 'log(dpΒ\xa0orΒ\xa0numeric)', 'description': 'Base 10 logarithm. Example usage: log(100.0)=2'},
 {'name': 'log(bΒ\xa0numeric,Β\xa0xΒ\xa0numeric)',
  'description': 'Logarithm to baseΒ\xa0b. Example usage: log(2.0, 64.0)=60.000.000.000'},
 {'name': 'mod(y,Β\xa0x)', 'description': 'Remainder ofΒ\xa0y/x. Example usage: mod(9,4)=1'},
 {'name': 'pi()', 'description': '"Ο€"Β\xa0constant. Example usage: pi()=314.159.265.358.979'},
 {'name': 'power(aΒ\xa0dp,Β\xa0bΒ\xa0dp)',
  'description': 'AΒ\xa0raised to the power ofΒ\xa0b. Example usage: power(9.0, 3.0)=729'},
 {'name': 'power(aΒ\xa0numeric,Β\xa0bΒ\xa0numeric)',
  'description': 'AΒ\xa0raised to the power ofΒ\xa0b. Example usage: power(9.0, 3.0)=729'},
 {'name': 'radians(dp)', 'description': 'Degrees to radians. Example usage: radians(45.0)=0.785398163397448'},
 {'name': 'round(dpΒ\xa0orΒ\xa0numeric)', 'description': 'Round to nearest integer. Example usage: round(42.4)=42'},
 {'name': 'round(vΒ\xa0numeric,Β\xa0sΒ\xa0int)',
  'description': 'Round toΒ\xa0sΒ\xa0decimal places. Example usage: round(42.4382, 2)=42.44'},
 {'name': 'sign(dpΒ\xa0orΒ\xa0numeric)',
  'description': 'Sign of the argument (-1, 0, +1). Example usage: sign(-8.4)=-1'},
 {'name': 'sqrt(dpΒ\xa0orΒ\xa0numeric)', 'description': 'Square root. Example usage: sqrt(2.0)=14.142.135.623.731'},
 {'name': 'trunc(dpΒ\xa0orΒ\xa0numeric)', 'description': 'Truncate toward zero. Example usage: trunc(42.8)=42'},
 {'name': 'trunc(vΒ\xa0numeric,Β\xa0sΒ\xa0int)',
  'description': 'Truncate toΒ\xa0sΒ\xa0decimal places. Example usage: trunc(42.4382, 2)=42.43'},
 {'name': 'width_bucket(operandΒ\xa0dp,Β\xa0b1Β\xa0dp,Β\xa0b2dp,Β\xa0countΒ\xa0int)',
  'description': 'Return the bucket number to whichΒ\xa0operandΒ\xa0would be assigned in a histogram havingΒ\xa0countΒ\xa0equal-width buckets spanning the rangeΒ\xa0b1Β\xa0toΒ\xa0b2; returnsΒ\xa00Β\xa0orΒ\xa0count+1Β\xa0for an input outside the range. Example usage: width_bucket(5.35, 0.024, 10.06, 5)=3'},
 {'name': 'width_bucket(operandΒ\xa0numeric,Β\xa0b1numeric,Β\xa0b2Β\xa0numeric,Β\xa0countΒ\xa0int)',
  'description': 'Return the bucket number to whichΒ\xa0operandΒ\xa0would be assigned in a histogram havingΒ\xa0countΒ\xa0equal-width buckets spanning the rangeΒ\xa0b1Β\xa0toΒ\xa0b2; returnsΒ\xa00Β\xa0orΒ\xa0count+1Β\xa0for an input outside the range. Example usage: width_bucket(5.35, 0.024, 10.06, 5)=3'},
 {'name': 'width_bucket(operandΒ\xa0anyelement,thresholdsΒ\xa0anyarray)',
  'description': "Return the bucket number to whichΒ\xa0operandΒ\xa0would be assigned given an array listing the lower bounds of the buckets; returnsΒ\xa00Β\xa0for an input less than the first lower bound; theΒ\xa0thresholdsΒ\xa0arrayΒ\xa0must be sorted, smallest first, or unexpected results will be obtained. Example usage: width_bucket(now(), array['yesterday', 'today', 'tomorrow']::timestamptz[])=2"}
]

RAND_FUNCTIONS = [
 {'name': 'random()', 'description': 'Random value in the range 0.0 <= x < 1.0.'}
]

TRIG_FUNCTIONS = [
 {'name': 'acos(x)', 'description': 'Inverse cosine'},
 {'name': 'asin(x)', 'description': 'Inverse sine'},
 {'name': 'atan(x)', 'description': 'Inverse tangent'},
 {'name': 'atan2(y, x)', 'description': 'Inverse tangent of y/x'},
 {'name': 'cos(x)', 'description': 'Cosine'},
 {'name': 'cot(x)', 'description': 'Cotangent'},
 {'name': 'sin(x)', 'description': 'Sine'},
 {'name': 'tan(x)', 'description': 'Tangent'},
]
