(function () {
    /**
     * Add a choice field.
     */
    function add_choice_field(event) {
        event.preventDefault();
        const field = get_elem('#choice_texts');
        const new_field = field.cloneNode(true);
        field.id = "";
        new_field.querySelector('.choice-sort-key').value = field.querySelector('.choice-sort-key').value + 1;
        new_field.querySelector('.form-input').value = "";
        new_field.insertAfter(field)
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
        const elem = event.currentTarget;
        const row = elem.parentNode.parentNode;

        let exchange, first, second;

        if (direction === 1) {
            exchange = row.nextElementSibling;
            first = exchange;
            second = row;
        } else {
            exchange = row.previousElementSibling;
            second = exchange;
            first = row;
        }
        if (!hasClass(exchange, 'choice-row')) {
            // can not be moved, already either first or last.
            return;
        }
        second.insertAfter(first);
        const first_sort_key_elem = first.querySelector('.choice-sort-key');
        const first_sort_key = first_sort_key_elem.value;
        const second_sort_key_elem = second.querySelector('.choice-sort-key');
        first_sort_key_elem.value = second_sort_key_elem.value;
        second_sort_key_elem.value = first_sort_key;
    }

    (function () {
        const choice_add = get_elem('#choice_add');
        if (choice_add) {
            choice_add.addEventListener("click", add_choice_field);
        }
        const move_up = get_elems('.choice-move-up');
        if (move_up) {
            move_up.forEach(function (elem) {
                elem.addEventListener("click", move_choice_field_up)
            });
            get_elems('.choice-move-down').forEach(function (elem) {
                elem.addEventListener("click", move_choice_field_down)
            });
        }
    })();
})();