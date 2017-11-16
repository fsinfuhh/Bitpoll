$(document).ready(function() {
    // Show elements that were hidden by CSS `.script-only` class
    $(".script-only").css("display", "block");
    $("td.script-only").css("display", "table-cell");
    $("tr.script-only").css("display", "table-row");
    $("table.script-only").css("display", "table");
    $(".script-hidden").hide();

    $(".btn-js-back").click(function() {
        history.back();
    });

    // Enable bootstrap popovers
    $('[data-toggle="popover"]').popover({
        html: true
    });

    $(".toggle").click(function() {
        var selected = $(this).hasClass("toggle-select");
        var cells;
        if($(this).hasClass("toggle-column")) {
            var index = $(this).closest("td").index() + 1;
            cells = $(this).closest("table").find("tr td:nth-child(" + index + ")");
        } else if($(this).hasClass("toggle-row")) {
            cells = $(this).closest("tr").find("td");
        } else {
            cells = $(this).closest("table").find("td");
        }
        updateCheckbox.call(cells.find(":checkbox").prop("checked", selected));
    });

    $(".time-remove-button").click(function() {
        var split = $(this).val().split(":");
        $("#time-hour").val(split[0]);
        $("#time-minute").val(split[1]);
        $("#time-slider-form").submit();
    });

    $(".icon-preview button").click(function() {
        $("#id_icon").val($(this).data("icon"));
    }).each(function() {
        //$(this).find("span").text(ICONS[$(this).data("icon")]).hide();
    }).css("width", "28px");

    // Comment positioning
    // Relative positioning is not defined on elements with
    // display:table-cell. Therefore we wrap everything in a div
	// with position:relative and emulate table cell properties.
    // (see http://www.w3.org/TR/CSS21/visuren.html#choose-position)
    $('td.vote-choice:has(span.comment-icon)').each(function() {
        var cell = $(this);
        var cellHeight = cell.outerHeight() + 'px';
        var div = $('<div></div>').css({
            'position': 'relative',
            'padding': cell.css('padding'),
            'width': '100%',
            'height': cellHeight,
            'line-height': cellHeight
        });
        cell.css('padding', 0).wrapInner(div);
        cell.find('span.comment-icon').css('display', 'block');
    });

    $("select.make-button-group").each(function() {
        var select = $(this);
        select.hide();

        var group = $('<div class="types"></div>');
        select.after(group);

        select.find("option").each(function() {
            var option = $(this);
            var button = $('<button type="button" class="btn btn-sm btn-default"></button>');
            button.text(option.text());
            button.val(option.val());
            button.click(function() {
                group.find(".btn").removeClass("active");
                button.addClass("active");
                select.val(button.val());
                return false;
            });
            group.append(button);
            group.append(' ');
        });

        group.find(".btn[value='" + select.val() + "']").addClass("active");
    });

    $('#datetimepicker').datetimepicker({
        format: 'Y-m-d H:i' //TODO: can we localize the format?
    });

});

