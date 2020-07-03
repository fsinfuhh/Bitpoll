(function () {
    let setChoiceByCell, showComment;

    showComment = function (el) {
        const td = el.closest("td");
        show_elem(td.getElementsByTagName('input')[0]);
        hide_elem(td.getElementsByTagName('button')[0]);
        return false;
    };

    setChoiceByCell = function (cell) {
        return cell.control.checked = true;
    };

    let draggingMouse, draggingStartCell;

    hide_elems_selector(".vote-choice-form");

    // Buttons: "Show comment field"
    get_elems(".vote-choice-edit").forEach(function (elem) {
        elem.addEventListener("click", function (e) {
            e.preventDefault();
            return showComment(e.target)
        });
    });

    // Button: "Show all comment fields"
    get_elem(".vote-choice-edit-all").addEventListener("click", function (e) {
        return get_elems(".vote-choice-edit").forEach(function (el) {
            return showComment(el);
        });
    });


    // Hide comment fields, but show those that do have input
    get_elems(".vote-comment").forEach(function (elem) {
        const input = elem.getElementsByTagName('input')[0];
        const button = elem.getElementsByTagName('button')[0];
        if (input.value === "") {
            hide_elem(input);
            show_elem(button)
        }
    });


    // Button: "all" (selecting the whole column)
    get_elems(".vote-choice-column").forEach(function (el) {
        el.addEventListener('click', function (e) {
            const choice = e.target.getAttribute("data-choice");
            return get_elems('.vote-choice input[value="' + choice + '"] ~ label').forEach(function (elem) {
                return setChoiceByCell(elem);
            });
        });
    });
    // Fast selecting of voting cells
    draggingMouse = false;
    draggingStartCell = null;
    get_elems("td.vote-choice label").forEach(function (el) {
        el.addEventListener('mousedown', function () {
            draggingMouse = true;
            draggingStartCell = el;
            addClass(get_elem('table.vote'), 'user-select-none');
            return false;
        });
        el.addEventListener('mouseenter', function (e) {
            if (draggingMouse) {
                if (draggingStartCell) {
                    setChoiceByCell(draggingStartCell);
                    draggingStartCell = null;
                }
                return setChoiceByCell(e.target);
            }
        });
    });
    get_elem('body').addEventListener('mouseup', function (el) {
        if (draggingMouse) {
            draggingMouse = false;
            removeClass(get_elem('table.vote'), 'user-select-none');
            return false;
        }
    });

    /* code for numeric polls
    let $table, max, min, ref, ref1, ref2, step;
    $table = $("table.vote");
    min = ((ref = $table.attr("data-minimum")) != null ? ref.toNumber() : void 0) || 0;
    max = ((ref1 = $table.attr("data-maximum")) != null ? ref1.toNumber() : void 0) || 100;
    step = ((ref2 = $table.attr("data-step")) != null ? ref2.toNumber() : void 0) || 1;
    return $(".numeric").each(function () {
        var $field;
        $field = $(this);
        return $field.change(function () {
            var val;
            val = $(this).val();
            val = val.toNumber();
            console.log(val);
            if (min && val < min) {
                val = min;
            }
            if (max && val > max) {
                val = max;
            }
            console.log(val);
            if (step) {
                val = Math.round((val - min) / step) * step + min;
            }
            console.log(val);
            return $(this).val(val);
        });
    });*/

}).call();
