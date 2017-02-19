(function() {
  /**
   * Add a choice field.
   */
  function add_choice_field(event) {
    event.preventDefault();
    $('#choice_texts').append('<input name="choice_text" />');
  }

  /**
   * Move a choice field up or down.
   *
   * @param event
   */
  function move_choice_field(event) {
    event.preventDefault();
    var elem = $(this);
    var direction = elem.hasClass('choice-move-up') ? -1 : 1;
    var row = elem.parent().parent();

    var exchange, first, second;

    if (direction === 1) {
      exchange = row.next();
      first = exchange;
      second = row;
    } else {
      exchange = row.prev();
      second = exchange;
      first = row;
    }
    if (!exchange.hasClass('choice-row')) {
      // can not be moved, already either first or last.
      return;
    }
    second.insertAfter(first);
    var first_sort_key_elem = first.find('.choice-sort-key');
    var first_sort_key = first_sort_key_elem.val();
    var second_sort_key_elem = second.find('.choice-sort-key');
    var second_sort_key = second_sort_key_elem.val();
    first_sort_key_elem.val(second_sort_key);
    second_sort_key_elem.val(first_sort_key);
  }

  $(function() {
    $('#choice_add').click(add_choice_field);
    $('.choice-move-up').click(move_choice_field);
    $('.choice-move-down').click(move_choice_field);
  });
})();