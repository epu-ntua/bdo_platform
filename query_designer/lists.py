AGGREGATES = (
    ('', '(No aggregate)', ['FLOAT', 'INT', 'STRING', 'TIMESTAMP']),
    ('AVG', 'Average', ['FLOAT', 'INT']),
    ('SUM', 'Sum', ['FLOAT', 'INT']),
    ('MIN', 'Minimum', ['FLOAT', 'INT', 'STRING', 'TIMESTAMP']),
    ('MAX', 'Maximum', ['FLOAT', 'INT', 'STRING', 'TIMESTAMP']),
    ('COUNT', 'Count', ['FLOAT', 'INT', 'STRING', 'TIMESTAMP']),
    ('PERCENTILE_CONT_10', "Percentile 10%", ['FLOAT', 'INT']),
    ('PERCENTILE_CONT_25', "Percentile 25%", ['FLOAT', 'INT']),
    ('PERCENTILE_CONT_50', "Median", ['FLOAT', 'INT']),
    ('PERCENTILE_CONT_75', "Percentile 75%", ['FLOAT', 'INT']),
    ('PERCENTILE_CONT_90', "Percentile 90%", ['FLOAT', 'INT']),
    ('STDDEV', "Standard Deviation", ['FLOAT', 'INT']),
)
