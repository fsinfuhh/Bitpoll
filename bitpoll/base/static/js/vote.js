// language=JQuery-CSS
(function () {
    var setChoiceByCell, showComment;

    showComment = function () {
        $(this).hide().closest("td").find("input").css("width", 0).show().animate({
            width: "100%"
        }, 400, "linear").focus();
        return false;
    };

    setChoiceByCell = function (cell) {
        return cell.control.checked = true;
    };

    $(function () {
        var $table, draggingMouse, draggingStartCell, max, min, ref, ref1, ref2, step;

        $(".vote-choice-form").hide();
        // Buttons: "Show comment field"
        $(".vote-choice-edit").click(showComment);
        // Button: "Show all comment fields"
        $(".vote-choice-edit-all").click(function () {
            return $(".vote-choice-edit").each(function (i) {
                return setTimeout((function (_this) {
                    return function () {
                        return showComment.call($(_this));
                    };
                })(this), i * 50);
            });
        });
        // Hide comment fields, but show those that do have input
        $(".vote-comment .vote-choice-comment").hide();
        $(".vote-comment input[value!=\"\"]").each(function () {
            showComment.call($(this).closest(".vote-comment").find(".vote-choice-edit"));
            return showComment.call($(this).closest(".vote-comment").find(".vote-choice-comment"));
        });

        // Button: "all" (selecting the whole column)
        $(".vote-choice-column").click(function () {
            var choice;
            choice = $(this).data("choice");
            return $('.vote-choice input[value="' + choice + '"] ~ label').each(function () {
                return setChoiceByCell(this);
            });
        });

        // Fast selecting of voting cells
        draggingMouse = false;
        draggingStartCell = null;
        $("td.vote-choice label").mousedown(function () {
            draggingMouse = true;
            draggingStartCell = this;
            $('table.vote').disableSelect();
            return $('body').on('mouseup', function () {
                draggingMouse = false;
                return $('table.vote').enableSelect();
            });
        });
        $("td.vote-choice label").mouseenter(function () {
            if (draggingMouse) {
                if (draggingStartCell) {
                    setChoiceByCell(draggingStartCell);
                    draggingStartCell = null;
                }
                return setChoiceByCell(this);
            }
        });
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
        });
    });

}).call();
