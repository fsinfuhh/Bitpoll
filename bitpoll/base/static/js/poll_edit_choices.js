var times = [];
var dates = [];
var calendar;


/* ========================================================================== */
/* Checkbox stuff */

window.updateCheckbox = function(e) {
    $(this).closest(".checkbox-cell").removeClass("on off").addClass($(this).prop("checked") ? "on" : "off");
};

$(function() {
    calendar = $("#calendar");

    // Checkbox stuff
    $(".checkbox-cell :checkbox").on("click", updateCheckbox).on("click", function(e) {
        e.stopPropagation();
    });

    $(".checkbox-cell").on("click", function(e){
        var checkbox = $(this).find(":checkbox");
        checkbox.prop("checked", !checkbox.prop("checked"));
        updateCheckbox.call(checkbox);
    });

    $(".checkbox-cell :checkbox").each(updateCheckbox);

    // Checkbox all/none toggles
    $(".toggle").click(function() {
        // deselect or select
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
        return false;
    });

    // Calendar stuff
    $(".calendar").each(function() {
        initCalendar($(this));
    });

    // Time slider
    initTimeSlider();

    // Time remove buttons
    $(".time-slots").on("click", ".time-remove-button", function() {
        removeTime($(this).attr("data-time"));
        return false;
    });

    $("#calendar-list").on("click", ".date-remove-button", function() {
        removeDate($(this).attr("data-date"));
        return false;
    });

    $("#date-time-form-content").hide();

    // Load data
    if($("#id_times").val()) times = $("#id_times").val().split(",");
    if($("#id_dates").val()) dates = $("#id_dates").val().split(",");
    times.sort();
    dates.sort();
    updateDateTimeList();

});


/* ========================================================================== */
/* Time and date stuff */

function updateDateTimeList() {
    $("#id_times").val(times.join());
    $("#id_dates").val(dates.join());

    $(".time-slots").html("");
    times.forEach(function(time) {
        $(".time-slots").append('<li><button class="action time-remove-button" title="remove time" data-time="' + time + '"><span>' + time + '</span><i class="fa-solid fa-times"></i></button></li>');
    });

    $("#calendar-list").html("");
    dates.forEach(function(date) {
        var formatDate = moment(date).format("ddd D MMM");
        $("#calendar-list").append('<li><button class="action date-remove-button" title="remove date" data-date="' + date +'"><span>' + formatDate + '</span><i class="fa-solid fa-times"></i></button></li> ');
    });

    // $(".date-remove-button, .time-remove-button").tooltip({"placement": "right"});
    if (calendar.data("date")) {
        calendarSetDate(calendar.data("date"));
    }
}

function addTime(rawTime) {
    var time = moment(rawTime, "H:mm", true);
    if(time.isValid()) {
        times.push(time.format("HH:mm"));
        times = times.uniquify();
        times.sort();
        updateDateTimeList();
    }
}

function addDate(date) {
    dates.push(date);
    dates = dates.uniquify();
    dates.sort();
    updateDateTimeList();
}

function removeTime(time) {
    times.removeValue(time);
    updateDateTimeList();
}

function removeDate(date) {
    dates.removeValue(date);
    updateDateTimeList();
}

/* ========================================================================== */
/* Time Slider */

function initTimeSlider() {
    var buttonState = {'pressed': false};
    $("#time-slider").mousedown(function(e) {
        buttonState.pressed = true;
        $('body').one('mouseup', function(e) {
            buttonState.pressed = false;
        });
    }).mousemove(function(e) {
        if (buttonState.pressed) {
            sliderPosition.call(this, e);
        }
    });
    $("#time-minute, #time-hour").keyup(function() {
        var hour = $("#time-hour").val();
        var minute = $("#time-minute").val();
        if(!hour || !minute) return;
        if(!moment(hour + ":" + minute, "HH:mm", true).isValid()) return;
        setSliderPosition( parseInt(hour), parseInt(minute), true);
    }).focus(function(e) {
        $(this).select();
    }).mouseup(function(e) {
        e.preventDefault();
    });
    setSliderPosition(12, 0);

    // suppress initial animation
    setTimeout(function() {
        $(".time-slider-display .hour, .time-slider-display .minute").addClass("animated");
    }, 100);

    $("#time-add-button").click(function(event) {
        event.preventDefault();
        var hour = $("#time-hour").val();
        var minute = $("#time-minute").val();
        addTime(hour + ":" + minute);
        setSliderPosition(12, 0);
        $("#time-hour").focus();
        return false;
    });
}

function sliderPosition(e) {
    var offset = 8;
    var width = 384;
    var progress = (e.pageX - offset - $(this).offset().left) / width;
    progress = Math.min(1, Math.max(0, progress));
    var steps = 24 * 4;
    var step = Math.round(steps*progress);
    var hour = Math.floor(step/4);
    var minute = 15 * (step % 4);
    setSliderPosition(hour, minute);
}

function setSliderPosition(_hour, _minute, suppressValueUpdate) {
    var hour = (_hour + (_minute-(_minute%60))/60) % 24;
    // alert(hour + " // " + _hour);
    var minute = _minute % 60;

    var steps = 24 * 4 + 1;
    var offset = 8;
    var width = 384;

    var step = hour * 4 + minute/15;
    var pos = (step / (steps-1)) * width + offset;
    // $("#time-debug").text(step/4);
    $("#time-slider-knob").css("left", pos);

    $(".time-slider-display .hour").rotate(hour / 12 * 360 + minute / 60 / 12 * 360);
    $(".time-slider-display .minute").rotate(hour * 360 + minute / 60 * 360);

    if(!suppressValueUpdate || hour!=_hour || minute!=_minute) {
        $("#time-hour").val(hour);
        $("#time-minute").val(minute < 10 ? "0" + minute : minute);
    }
}

/* ========================================================================== */
/* Calendar */


function initCalendar(calendar) {
    var date = moment();
    calendarSetDate(date);

    $("#calendar-next-month").click(function() {
        calendarSetDate(calendar.data("date").add(1, "months"));
        return false;
    });

    $("#calendar-prev-month").click(function() {
        calendarSetDate(calendar.data("date").subtract(1, "months"));
        return false;
    });

    calendar.on("click", "button.day", function() {
        toggleDay($(this));
        return false;
    }).on("click", "button.week", function() {
        var off = $(this).closest("tr").find("button.day.default").length > 0;
        var cls = off ? ".default" : ".success";

        $(this).closest("tr").find("button.day" + cls).each(function() {
            toggleDay($(this));
        });
        return false;
    });
}

function toggleDay(btn) {
    var date = calendar.data("date");
    date.date(btn.text());
    var datetime = date.format("YYYY-MM-DD");
    if(dates.contains(datetime)) {
        removeDate(datetime);
    } else {
        addDate(datetime);
    }
}

function calendarSetDate(date) {
    date = date.startOf("month"); // first day of the month
    calendar.data("date", date);
    updateMonth();
}

function updateMonth() {
    var date = calendar.data("date");

    calendar.find(".title").text(date.format("MMMM YYYY"));
    calendar.find(".week").remove();

    var week = [];
    var start = date.isoWeekday();
    var endDay = date.endOf("month").date();
    var end = Math.ceil( (endDay + start) / 7 ) * 7;
    for(var i = 1; i <= end; ++i) {
        var day = i - start;
        week.push(day >= 0 && day < endDay ? day+1 : 0);
        if(i%7 == 0) {
            makeWeek(week);
            week = [];
        }
    }
}

function makeWeek(week) {
    var tr = $('<tr class="week"></tr>');

    var end = moment(calendar.data("date"));
    end.date(week[6]);
    var start = moment(calendar.data("date"));
    start.date(week[0]);
    var past = end.isBefore(moment());
    var future = start.isAfter(moment());
    if(past && !future) {
        tr.append($('<td class="left"></td>'))
    } else {
        tr.append($('<td class="left"><button class="week action icon default"><i class="fa-solid fa-angle-double-right"></i></button></td>'))
    }

    for(var i = 0; i < 7; ++i) {
        var btn = "";
        if(week[i] != 0) {
            var date = calendar.data("date");
            date.date(week[i]);
            var datetime = date.format("YYYY-MM-DD");
            // alert(datetime);
            var enabled = dates.contains(datetime);
            past = date.isBefore(moment());
            var t = (past && !enabled ? 'span' : 'button');
            btn = '<' + t + ' class="day ' + (enabled ? 'action icon success' : (past ? '' : 'action icon default')) + '">' + week[i] + '</' + t + '>';
        }
        tr.append($('<td>' + btn + '</td>'));
    }
    calendar.find("table").append(tr);
}
