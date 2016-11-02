(function() {
  /**
   * Add a choice field.
   */
  function add_choice_field(event) {
    event.preventDefault();
    $('#choice_texts').append('<input name="choice_text" />');
  }

  $(function() {
    $('#choice_add').on('click', add_choice_field);
  });
})();