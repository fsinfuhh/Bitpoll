(function () {
    /**
     * Add a choice field.
     */
    function add_choice_field(event) {
        event.preventDefault();
        var new_entry = document.createElement('input');
        new_entry.name = "choice_text";
        get_elem('#choice_texts').appendChild(new_entry);
    }

    function move_choice_field_up(event) {
        move_choice_field(event, -1)
    }

    function move_choice_field_down(event) {
        move_choice_field(event, 1)
    }

    /**
     * Move a choice field up or down.
     *
     * @param event
     */
    function move_choice_field(event, direction) {
        event.preventDefault();
        var elem = this;
        var row = elem.parentNode.parentNode;

        var exchange, first, second;

        if (direction === 1) {
            exchange = row.nextElementSibling;
            first = exchange;
            second = row;
        } else {
            exchange = row.previousElementSibling;
            second = exchange;
            first = row;
        }
        if (!exchange.hasClass('choice-row')) {
            // can not be moved, already either first or last.
            return;
        }
        second.insertAfter(first);
        var first_sort_key_elem = first.querySelector('.choice-sort-key');
        var first_sort_key = first_sort_key_elem.value;
        var second_sort_key_elem = second.querySelector('.choice-sort-key');
        first_sort_key_elem.value = second_sort_key_elem.value;
        second_sort_key_elem.value = first_sort_key;
    }

    (function () {
        const choice_add = get_elem('#choice_add');
        if (choice_add){
            choice_add.addEventListener("click", add_choice_field);
            get_elem('.choice-move-up').addEventListener("click", move_choice_field_up);
            get_elem('.choice-move-down').addEventListener("click", move_choice_field_down);
        }
    })();
})();