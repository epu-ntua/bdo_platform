/**
 * Created by dimitris on 4/10/2016.
 */
$(function() {
    tokenize = function(expression) {
        var tokenTypes = ['symbol', 'property', 'function', 'numerical', 'invalid'];

        /* Helpers */
        var isSymbol = function(x) {
            return ['(', ')', '<', '>', '=', '!', '+', '-', '*', '/', ','].indexOf(x) >= 0
        };

        var isWhitespace = function(x) {
            return [' ', '\t', '\r', '\n'].indexOf(x) >= 0
        };

        var isListItem = function(token, selector, quote) {
            var result = false;
            if (typeof(quote) !== 'undefined') {
                token = token.substr(1, token.length - 2);
            }

            $.each($(selector).find('.item-value'), function(idx, iv) {
                if ($(iv).data('value') == token) {
                    result = true;
                }
            });

            return result
        };

        var isNumerical = function(token) {
            return !isNaN(Number(token))
        };

        var isProperty = function(token) {
            return isListItem(token, '.property-list .property-item', '`');
        };

        var isFunction = function(token) {
            return isListItem(token, '.function-list .function-item');
        };

        /* Adds token & resets current token */
        var tokens = [],
            currentToken = '';

        var addToken = function(tokenType) {
            // ignore token if empty
            if (currentToken === '') {
                return
            }

            // identify token type
            if (typeof(tokenType) === 'undefined') {
                if (isNumerical(currentToken)) {
                    tokenType = 'numerical'
                }
                else if (isFunction(currentToken)) {
                    tokenType = 'function'
                }
                else if (isProperty(currentToken)) {
                    tokenType = 'property';
                    currentToken = currentToken.substr(1, currentToken.length - 2);
                }
                else if (isSymbol(currentToken)) {
                    tokenType = 'symbol'
                } else {
                    tokenType = 'invalid'
                }

            }

            // add to token list
            tokens.push({
                text: currentToken,
                type: tokenType
            });

            // reset current token
            currentToken = '';
        };

        // loop the
        for (var c=0; c < expression.length; c++) {
            var x = expression[c];

            if (isSymbol(x)) {
                // add the previous token
                addToken();

                // add the symbol
                currentToken = x;
                addToken('symbol')
            }
            else if (isWhitespace(x)) {
                // add the previous token
                addToken();
            } else {
                currentToken += x
            }
        }
        // add the last token
        addToken();

        return tokens
    };

    toFormula = function($elems) {
        $.each($elems, function(idx, item) {
            var  $item = $(item);

            // tokenize content
            var tokens = tokenize($item.text());

            // empty content & mark as formula
            $item.empty();
            $item.addClass('formula');

            // add token elements
            $.each(tokens, function(idx, token) {
                var $elem = $('<span />').text(token.text).addClass('token token-' + token.type);
                $item.append($elem)
            });

        });
    };

    /* Add, edit, delete & save formulas */
    FormulaManager = {
        generateName: function() {
            // auto-generate name
            var fNameCnt = $('#formula-editor-main').find('tr').length;
            while (this.getFormulaByName('F' + fNameCnt) !== undefined) {
                fNameCnt++;
            }

            return 'F' + fNameCnt
        },

        /* Show an info message about the status of the editor */
        setStatus: function(message) {
            $('#formula-editor-status').find('.content').html(message);
        },

        /* Add a new formula */
        addFormula: function() {
            var fName = this.generateName();

            // create empty row
            var $tr = $('<tr><td class="formula-name"><span></span></td><td class="formula-value"><div class="formula"></div></td><td class="formula-unit"></td>');
            $tr.find('td.formula-name > span').text(fName);

            // set empty formula
            this.setFormula($tr, '');

            // add to table
            $('#formula-editor-main tbody').append($tr);

            // return new formula row
            return $tr
        },

        /* Edit formula */
        editFormula: function($tr) {
            // set editing
            var $td = $tr.find('.formula-value');
            $td.addClass('editing');

            // create input & prefill with formula
            var $input = $('<input type="text" class="formula-input" />');
            $input.val($td.data('value'));

            // replace cell with input
            $td.html($input);

            // append save button
            var $saveFormulaBtn = $('<button class="btn btn-sm btn-primary save-formula"><i class="fa fa-save"></i> Save formula</button>');
            $td.append($saveFormulaBtn);

            // set sidebar elements active & update info message
            $('ul.item-list').addClass('clickable');
            this.setStatus('<i class="fa fa-info-circle"></i> Click on properties or functions on the left to insert them to the formula');

            // focus input
            $input.focus()
        },

        /* Set formula value */
        setFormula: function($tr, formulaValue) {
            var $td = $tr.find('td.formula-value');
            $td.removeClass('editing');

            // set data attribute & content
            $td.html('<div class="formula" />');
            $td.find('.formula').text(formulaValue);
            $td.attr('data-value', formulaValue);
            $td.data('value', formulaValue);

            // format
            toFormula($td.find('.formula'));

            // set sidebar elements inactive
            $('ul.item-list').removeClass('clickable');

            // auto-save
            this.save();
        },

        /* Edit formula name */
        editFormulaName: function($tr) {
            // set editing
            var $td = $tr.find('.formula-name');
            $td.addClass('editing');

            // create input & pre-fill with formula
            var $input = $('<input type="text" class="formula-name-input" />');
            $input.val($td.text());

            // replace cell with input
            $td.html($input);

            // append save button
            var $saveFormulaBtn = $('<button class="btn btn-sm btn-primary save-formula-name"><i class="fa fa-save"></i></button>');
            $td.append($saveFormulaBtn);

            // focus input
            $input.focus()
        },

        /* Set formula name */
        setFormulaName: function($tr, formulaName) {
            var $td = $tr.find('td.formula-name');
            $td.removeClass('editing');

            // set content
            var $span = $('<span />').text(formulaName).attr('title', formulaName);
            $td.html($span);

            // auto-save
            this.save();
        },

        /* Get formula by name */
        getFormulaByName: function(formulaName) {
            var result = undefined;
            $.each($('#formula-editor-main').find('td.formula-name'), function(idx, td) {
                if ($(td).find('> span').text() == formulaName) {
                    result = $(td).closest('tr');
                }
            });

            return result
        },

        /* Set formula errors */
        setFormulaErrors: function($tr, error) {
            var $td = $tr.find('.formula-value');
            error = error || '';

            if (error.length == 0) {
                $tr.removeClass('with-error')
            } else {
                $tr.addClass('with-error')
            }

            // add error icon & info
            $td.find('.error-info').remove();

            if (error.length > 0) {
                var errorInfo = $('<span class="error-info pull-right"><i class="fa fa-exclamation-triangle"></i>');
                errorInfo.attr('title', error);
                $td.append(errorInfo);
            }
        },

        /* Set formula unit (currently read-only) */
        setFormulaUnit: function($tr, unit) {
            $tr.find('.formula-unit').text(unit);
        },

        addToFormulaInput: function(text) {
            var inputs = document.getElementsByClassName('formula-input');
            if (inputs.length === 0) {
                return
            }
            var input = inputs[0];

            var caretPos = input.selectionStart;
            var front = (input.value).substring(0, caretPos);
            var back = (input.value).substring(input.selectionEnd, input.value.length);

            input.value = front + text + back;
            caretPos = caretPos + text.length;
            input.selectionStart = caretPos;
            input.selectionEnd = caretPos;

            input.focus();
        },

        /* Save all formulas */
        save: function() {
            var formulas = [];

            this.setStatus('Saving <i class="fa fa-spin fa-spinner"></i>');

            // prepare data
            $.each($('#formula-editor-main').find('tbody tr'), function(idx, tr) {
                var $tr = $(tr),
                    formulaId = $tr.data('id') || '',
                    formulaName = $tr.find('.formula-name > span').text(),
                    formulaValue = $tr.find('.formula-value').data('value');

                if ((formulaName !== '') && (formulaValue != '')) {
                    formulas.push({
                        formulaId: formulaId,
                        formulaName: formulaName,
                        formulaValue: formulaValue
                    });
                }
            });

            // serialize & add csrf token
            var data = {
                formulas: JSON.stringify(formulas),
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            };

            // make request to save
            var that = this;
            $.ajax({
                url: '/queries/formulas/save/',
                method: 'POST',
                data: data,
                success: function(formulas) {
                    $.each(formulas, function(idx, formula) {
                        var formulaRow = that.getFormulaByName(formula.name);

                        // set formula ID
                        formulaRow.data('id', formula.id);
                        formulaRow.attr('data-id', formula.id);

                        // validation & measurement
                        that.setFormulaErrors(formulaRow, formula.errors.join(', '));
                        that.setFormulaUnit(formulaRow, formula.unit);
                    });

                    that.setStatus('Saved <i class="fa fa-check"></i>');
                }
            })
        },

        sidebar: {
            onSearchInputChange: function($searchInput) {
                var term = $searchInput.val().toLowerCase(),
                    $ul = $searchInput.closest('.item-box').find('.item-list');

                /* Hide elements without the term */
                $.each($ul.find('> li'), function(idx, item) {
                    var $item = $(item),
                        v = $item.find('.item-value').text().toLowerCase(),
                        descr = $item.find('.item-description').text().toLowerCase();

                    if (term === '' || v.indexOf(term) == 0 || descr.indexOf(term) >= 0) {
                        $item.removeClass('hidden');
                    } else {
                        $item.addClass('hidden');
                    }
                });

                /* Toggle between search & clear icon */
                if (term === '') {
                    $searchInput.closest('.search-input-container')
                        .find('.fa')
                        .removeClass('fa-times clear-search')
                        .addClass('fa-search');
                } else {
                    $searchInput.closest('.search-input-container')
                        .find('.fa')
                        .removeClass('fa-search')
                        .addClass('fa-times clear-search');
                }
            }
        }
    };

    /* Initialize formulas */
    onFormulaLoad = function() {
        toFormula($('.formula'));
    };

    /* Create new formula */
    $('body').on('click', '#formula-create', function() {
        // add & automatically edit
        var $tr = FormulaManager.addFormula();
        FormulaManager.editFormula($tr);
    });

    /* ************************************ */
    /* Editing formula content */

    /* On formula click open edit form */
    $('body').on('click', '#formula-editor-main td.formula-value:not(.editing)', function() {
        FormulaManager.editFormula($(this).closest('tr'));
    });

    /* On formula save button click */
    $('body').on('click', '#formula-editor-main td.formula-value.editing .save-formula', function() {
        FormulaManager.setFormula($(this).closest('tr'), $(this).closest('tr').find('.formula-input').val());
    });

    /* On formula edit key enter */
    $('body').on('keydown', '#formula-editor-main td.formula-value.editing .formula-input', function(e) {
        var keycode = e.keyCode || e.which;
        if(keycode == 13) {
            FormulaManager.setFormula($(this).closest('tr'), $(this).val());
        }
    });

    /* ************************************ */
    /* Editing formula name */

    /* On formula name click open edit form */
    $('body').on('click', '#formula-editor-main td.formula-name:not(.editing)', function() {
        FormulaManager.editFormulaName($(this).closest('tr'));
    });

    /* On formula name save button click */
    $('body').on('click', '#formula-editor-main td.formula-name.editing .save-formula-name', function() {
        FormulaManager.setFormulaName($(this).closest('tr'), $(this).closest('tr').find('.formula-name-input').val());
    });

    /* On formula edit key enter */
    $('body').on('keydown', '#formula-editor-main td.formula-name.editing .formula-name-input', function(e) {
        var keycode = e.keyCode || e.which;
        if(keycode == 13) {
            FormulaManager.setFormulaName($(this).closest('tr'), $(this).val());
        }
    });

    /* On property & function click add to editing formula */
    $('body').on('click', 'ul.item-list > li', function() {
        var value = $(this).find('.item-value').data('value');
        if ($(this).hasClass('property-item')) {
            value = '`' + value + '`';
        }

        FormulaManager.addToFormulaInput(value);
    });

    /* On sidebar search area click */
    $('body').on('click', '.search-input-container', function() {
        $(this).find('input').focus();
    });

    /* On sidebar search key press */
    $('body').on('keyup', '.search-input-container input', function() {
        // trigger search term change
        FormulaManager.sidebar.onSearchInputChange($(this));
    });

    /* On sidebar search clear */
    $('body').on('click', '.search-input-container .clear-search', function(e) {
        e.preventDefault();
        e.stopPropagation();

        // clear search term
        var $searchInput = $(this).closest('.search-input-container').find('input');
        $searchInput.val('');

        // trigger search term change
        FormulaManager.sidebar.onSearchInputChange($searchInput);
    });
});