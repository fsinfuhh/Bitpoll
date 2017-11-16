// language=JQuery-CSS
(function () {
    var resetChoiceByCell, setChoice, setChoiceByCell, showComment;

    showComment = function () {
        $(this).hide().closest("td").find("input").css("width", 0).show().animate({
            width: "100%"
        }, 400, "linear").focus();
        return false;
    };

    setChoiceByCell = function (cell) {
        return setChoice($(cell).parents("tr").data("vote-choice"), $(cell).data("choice"));
    };

    resetChoiceByCell = function (cell) {
        return setChoice($(cell).parents("tr").data("vote-choice"), 0);
    };

    setChoice = function (voteChoice, choice) {
        var $tr;
        $tr = $("[data-vote-choice=\"" + voteChoice + "\"]");
        $tr.find("input[type=\"radio\"]").prop("checked", false);
        $tr.find("input[type=\"radio\"][value=\"" + choice + "\"]").prop("checked", true);
        $tr.find("td.vote-choice").addClass("off");
        return $tr.find("td.vote-choice[data-choice=\"" + choice + "\"]").removeClass("off");
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
            return $('.vote-choice[data-choice="' + choice + '"]').each(function () {
                return setChoiceByCell(this);
            });
        });

        // Fast selecting of voting cells
        draggingMouse = false;
        draggingStartCell = null;
        $("td.vote-choice").mousedown(function () {
            draggingMouse = true;
            draggingStartCell = this;
            $('table.vote').disableSelect();
            // set starting choice
            if ($(this).hasClass("off")) {
                setChoiceByCell(this);
            } else {
                resetChoiceByCell(this);
            }
            return $('body').on('mouseup', function () {
                draggingMouse = false;
                return $('table.vote').enableSelect();
            });
        });
        $("td.vote-choice").mouseenter(function () {
            if (draggingMouse) {
                if (draggingStartCell) {
                    setChoiceByCell(draggingStartCell);
                    draggingStartCell = null;
                }
                return setChoiceByCell(this);
            }
        });
        $(".vote-choice-radio").change(function () {
            return setChoice($(this).parents("tr").data("vote-choice"), $(this).val());
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
