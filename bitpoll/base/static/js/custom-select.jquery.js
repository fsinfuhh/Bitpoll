$.fn.customSelect = function ($items, options) {
    var $field = $(this);

    var it = {};

    options = $.extend({}, $.fn.customSelect.defaults, options);
    it.options = options;

    var setListCurrent = function (value) {
        $items.removeClass('current');
        $items.filter('[' + options.valueAttribute + '="' + value + '"]').addClass(options.currentClass);
    };

    // when the field value changes, update the list accordingly
    $field.change(function() {
        setListCurrent($field.val());
    });

    // when a list item is click, update the field and classes accordingly
    $items.click(function() {
        var value = $(this).attr(options.valueAttribute);
        setListCurrent(value);
        $field.val(value);
    });

    // initially, set the field's value
    setListCurrent($field.val());

    return it;
};

$.fn.customSelect.defaults = {
    // The attribute to fetch the item's value from
    valueAttribute: 'data-value',
    currentClass: 'current'
};
