import M from 'materialize-css/dist/js/materialize.js';


/*
*  materialize has got a bug with chip deletion. It's deleting chip on incorrect index
* 'materialize-css/dist/js/materialize.js' needs to be tweaked
*
* _handleChipClick():7752
* this.selectChip(index); replace with this.selectChip(index - 1);
*
* function deleteChip(chipIndex):7994
* after needs to be added chipIndex -= 1;
*
* function _handleChipsKeydown:8044
* on line 8065  var selectIndex = currChips.chipsData.length; after add selectIndex -= 1;
* currChips.selectChip(selectIndex) :8075 replace with currChips.selectChip(selectIndex-1);
*
* or replace fixed package 'materialize-css/dist/js/materialize.js' with './materialize/materialize.js'
*
* */

class RecipeChipFields {

    constructor(names) {
        /*
        * Initialize chip field
        *
        * */
        const chipOptions = {
            data: RecipeChipFields.getChipData(names.wtfFieldName),
            placeholder: names.placeholder,
            secondaryPlaceholder: names.secondaryPlaceholder,
            onChipAdd: (e, chip) => {
                RecipeChipFields.onChipAdded(names.wtfFieldName, chip);
            },
            onChipDelete: (e, chip) => {
                RecipeChipFields.onChipRemoved(names.wtfFieldName, chip);
            }
        };

        M.Chips.init(document.querySelectorAll(names.chipFieldSelector), chipOptions);
    };

    static onChipAdded(formSelector, chip) {
        /*
        * Add chip to input
        * */
        const chipValue = RecipeChipFields.getChipValue(chip);
        const list = $(`#${formSelector} li`);
        if (!chipValue) return false;

        // count the fields
        const ccField = list.length;

        // check if first value is empty if yes set the chip value
        if (ccField === 1) {
            const field = list.last().find('input');

            if (!field.val()) {
                field.val(chipValue);
                return false;
            }
        }

        // clone the last field of list
        const fieldToClone = list.last().clone();
        const fieldName = `${formSelector}-${ccField}`;

        fieldToClone.find('input').attr({
            id: fieldName,
            name: fieldName,
            value: chipValue
        });


        $(`#${formSelector}`).append(fieldToClone);
    }

    static onChipRemoved(formSelector, chip) {
        const chipValue = this.getChipValue(chip);
        const list = $(`#${formSelector} li`);
        if (!chipValue) return false;

        let cc = 0;
        list.each(function () {
            const _this = $(this);
            const input = _this.find('input');
            const label = _this.find('label');

            // prevent last element deletion
            if (list.length === 1) {
                input.val('');
                return false;
            } else if (input.val() === chipValue) {
                $(this).remove();
                cc -= 1;
            }

            const attrValue = label.attr('for').replace(/\d/, cc);

            label.attr('for', attrValue);
            input.attr({
                id: attrValue,
                name: attrValue
            });
            cc += 1;
        });
    }

    static getChipData(selector) {
        /*
        * function is getting values from hidden field and output as an array
        * */
        const list = $(`#${selector} li`);
        if (!list.length) return false;

        const data = [];

        list.each(function () {
            const input = $(this).find('input');
            try {
                if (input.val()) {
                    data.push({
                        tag: input.val()
                    });
                }
            } catch (e) {
                console.error('No value in input');
            }
        });
        return data;
    }

    static getChipValue(chip) {
        return (typeof chip !== 'undefined') ? chip.innerHTML.substring(0, chip.innerHTML.indexOf("<i")) : false;
    }
}


function convertFieldList(fieldType, selector) {
    /*
    * used to convert wtform FieldList to materialize appearance
    * set the correct label
    * and add delete button
    * */

    const fields = $(`${selector} li`);

    $(selector).attr('data-field-type', fieldType);

    if (!fields.length) return false;

    // need define a const jquery got a problem to handle this in each loop

    fields.each(function (index) {
        const _this = $(this);
        const label = _this.find('label');

        _this.addClass('input-field');

        // add more prominent label
        if (label) {
            label.html(`${index + 1}. ${label.text()}`);
        }

        // add delete button
        const button = `<button type="button" class="delete red darken-4" data-selector="${selector}" data-index="${index}">
<i class="material-icons">close</i></button>`;

        _this.append(button);

        if (fieldType === 'textarea') {
            const field = _this.find('textarea');
            if (field) {

                if (field.html() !== '') {
                    field.height(field[0].scrollHeight * 1.2);
                }

                field.addClass('materialize-textarea');
            }
        }
    });
}


function addField(button) {
    const listID = button.parent().find('ul').attr('id');
    const listToClone = $(`#${listID} li`).last().clone();
    const fieldType = $(`#${listID}`).attr('data-field-type');

    if (fieldType === 'textarea') {
        listToClone.find(fieldType).html('').removeAttr('style');
    } else if (fieldType === 'input') {
        listToClone.find(fieldType).val('');
    }

    listToClone.find('label').removeClass('active');


    $(`#${listID}`).append(listToClone);


    $('li button.delete').click(function () {
        deleteField($(this));
    });
    updateFieldsAttr(`#${listID}`);
}


function updateFieldsAttr(selector) {
    /*
    * function called to update list attributes
    * */
    const list = $(`${selector} li`);
    const firstLabel = list.first().find('label');
    const labelName = firstLabel.text().replace(/\d.\s/, '');
    const fieldName = firstLabel.attr('for').replace(/-\d/, '');
    const fieldType = $(selector).attr('data-field-type');


    list.each(function (index) {
        const _this = $(this);

        _this.find('.delete').attr('data-index', index);
        _this.find('label').attr('for', `${fieldName}-${index}`).text(`${index + 1}. ${labelName}`);

        const fieldAttr = `${fieldName}-${index}`;
        _this.find(fieldType).attr({
            id: fieldAttr,
            name: fieldAttr
        });

    });
}

let hold = false;

function deleteField(button) {
    /*
    * Used to delete field
    * */
    if (hold) return false;

    const selector = button.attr('data-selector');
    const index = button.attr('data-index');

    if (!index || !selector || $(`${selector} li`).length < 2) return false;
    $(selector).children().eq(index).remove();

    updateFieldsAttr(selector);

    /*
    * setTimeout is a tweak to prevent multiple deletion caused by
    * multiple instance of $('button.delete').click()
    * one on document load
    * second after new field creation
    */

    setTimeout(() => {
        hold = false;
    }, 500);
    hold = true;
}

export function recipeEdit() {
    // Define fields used as a chip field
    const chipFields = [
        {
            chipFieldSelector: '#categoryChips',
            placeholder: 'Add category',
            secondaryPlaceholder: '+Category',
            wtfFieldName: 'categories'
        },
        {
            chipFieldSelector: '#cuisineChips',
            placeholder: 'Add cuisine',
            secondaryPlaceholder: '+Cuisine',
            wtfFieldName: 'cuisines'
        },
        {
            chipFieldSelector: '#allergensChips',
            placeholder: 'Add allergen',
            secondaryPlaceholder: '+Allergen',
            wtfFieldName: 'allergens'
        },
    ];

    document.addEventListener('DOMContentLoaded', () => {
        chipFields.forEach((item) => {
            new RecipeChipFields(item);
        });

        convertFieldList('textarea', '#method');
        convertFieldList('input', '#ingredients');

        // create event on click delete button
        $('button.addField').click(function () {
            addField($(this));
        });

        $('li button.delete').click(function () {
            deleteField($(this));
        });
    });
}
