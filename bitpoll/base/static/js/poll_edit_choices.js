let times = [];
let dates = [];
let calendar;
let calendar_data = null;

/* ========================================================================== */
/* Checkbox stuff */

(function () {

    // Checkbox all/none toggles
    get_elems(".toggle").forEach(function (el) {
        el.addEventListener('click', function (ev) {
            // deselect or select
            const selected = hasClass(this, "toggle-select");
            let cells;
            if (hasClass(this, "toggle-column")) {
                const td = this.closest('td');
                const index = Array.from(td.parentNode.children).indexOf(td) + 1;
                cells = this.closest("table").querySelectorAll("tr td:nth-child(" + index + ")");
            } else if (hasClass(this, "toggle-row")) {
                cells = this.closest("tr").querySelectorAll("td");
            } else {
                cells = this.closest("table").querySelectorAll("td");
            }
            cells.forEach(function (el) {
                el.querySelectorAll("input[type=checkbox]").forEach(function (checkbox) {
                    checkbox.checked = selected;
                });
            });
            ev.preventDefault();
            return false;
        });
    });

    calendar = get_elem("#calendar");
    if (calendar) {
        initCalendar(calendar);

        get_elem("#calendar-list").addEventListener("click", function (e) {
            if (e.target.matches(".date-remove-button")) {
                removeDate(e.target.getAttribute("data-date"));
            }
            if (e.target.parentNode.matches(".date-remove-button")) {
                removeDate(e.target.parentNode.getAttribute("data-date"));
            }
            return false;
        });
    }

    if (get_elem('#time-slider-knob')) {
        // Time slider
        initTimeSlider();

        // Time remove buttons
        get_elem(".time-slots").addEventListener("click", function (e) {
            if (e.target.matches(".time-remove-button")) {
                removeTime(e.target.getAttribute("data-time"));
            }
            if (e.target.parentNode.matches(".time-remove-button")) {
                removeTime(e.target.parentNode.getAttribute("data-time"));
            }
            return false;
        });

    }


    // Load data
    const id_times = get_elem("#id_times");
    if (id_times && id_times.value) {
        times = id_times.value.split(",").map(function (item) {
            return item.trim();
        });
    }
    const id_dates = get_elem("#id_dates");
    if (id_dates && id_dates.value) {
        dates = id_dates.value.split(",").map(function (item) {
            return item.trim();
        });
    }
    times.sort();
    dates.sort();
    if (id_dates || id_times) get_elem("#date-time-form-content").style.display = "none";
    updateDateTimeList();

})();


/* ========================================================================== */

/* Time and date stuff */

function updateDateTimeList() {
    const id_times = get_elem("#id_times");
    if (id_times) id_times.value = times.join();
    const id_dates = get_elem("#id_dates");
    if (id_dates) id_dates.value = dates.join();
    const time_slots = get_elem(".time-slots");
    if (time_slots) {
        time_slots.innerHTML = "";
        times.forEach(function (time) {
            time_slots.insertAdjacentHTML('beforeend', '<li>' +
                '<button class="btn time-remove-button" title="remove time" data-time="' + time + '">' +
                '<span>' + time + '</span> <i class="fa fa-times"></i></button></li>');
        });
    }

    const calendar_list = get_elem("#calendar-list");
    if (calendar_list) {
        calendar_list.innerHTML = "";
        dates.forEach(function (date) {
            const format = "ddd D MMM";
            const date_obj = moment(date);
            if (date_obj.year() !== moment().year()) {
                format = "ddd D MMM YYYY"
            }
            const formatDate = date_obj.format(format);
            calendar_list.insertAdjacentHTML('beforeend', '<li>' +
                '<button class="btn date-remove-button" title="remove date" data-date="' + date + '">' +
                '<span>' + formatDate + '</span> <i class="fa fa-times"></i></button></li> ');
        });
    }

    if (calendar_data !== null) {
        calendarSetDate(calendar_data);
    }
}

function addTime(rawTime) {
    const time = moment(rawTime, "H:mm", true);
    if (time.isValid()) {
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
    let buttonState = {'pressed': false};
    const time_slider = get_elem("#time-slider");
    time_slider.addEventListener('mousedown', function () {
        buttonState.pressed = true;
        get_elem('body').addEventListener('mouseup', function () {
            buttonState.pressed = false;
        });
    });
    time_slider.addEventListener('mousemove', function (e) {
        if (buttonState.pressed) {
            sliderPosition.call(this, e);
        }
    });
    get_elems("#time-minute, #time-hour").forEach(function (el) {
        el.addEventListener('keyup', function () {
            const hour = get_elem("#time-hour").value;
            const minute = get_elem("#time-minute").value;
            if (!hour || !minute) return;
            if (!moment(hour + ":" + minute, "HH:mm", true).isValid()) return;
            setSliderPosition(parseInt(hour), parseInt(minute), true);
        });
        el.addEventListener('focus', function () {
            this.select();
        });
        el.addEventListener('mouseup', function (e) {
            e.preventDefault();
        });
    });
    setSliderPosition(12, 0);

    // suppress initial animation
    setTimeout(function () {
        get_elems(".time-slider-display .hour, .time-slider-display .minute").forEach(function (el) {
            addClass(el, "animated");
        });
    }, 100);

    get_elem("#time-add-button").addEventListener('click', function (event) {
        event.preventDefault();
        const hour = get_elem("#time-hour").value;
        const minute = get_elem("#time-minute").value;
        addTime(hour + ":" + minute);
        setSliderPosition(12, 0);
        get_elem("#time-hour").focus();
        return false;
    });
}

function sliderPosition(e) {
    const offset = 8;
    const width = 384;
    let progress = (e.pageX - offset - this.getBoundingClientRect().left + window.scrollX) / width;
    progress = Math.min(1, Math.max(0, progress));
    const steps = 24 * 4;
    const step = Math.round(steps * progress);
    const hour = Math.floor(step / 4);
    const minute = 15 * (step % 4);
    setSliderPosition(hour, minute);
}

function setSliderPosition(_hour, _minute, suppressValueUpdate) {
    const hour = (_hour + (_minute - (_minute % 60)) / 60) % 24;
    // alert(hour + " // " + _hour);
    const minute = _minute % 60;

    const steps = 24 * 4 + 1;
    const offset = 8;
    const width = 384;

    const step = hour * 4 + minute / 15;
    const pos = (step / (steps - 1)) * width + offset;
    get_elem("#time-slider-knob").style.left = "" + pos + "px";

    rotate_element(get_elem(".time-slider-display .hour"), hour / 12 * 360 + minute / 60 / 12 * 360);
    rotate_element(get_elem(".time-slider-display .minute"), hour * 360 + minute / 60 * 360);

    if (!suppressValueUpdate || hour !== _hour || minute !== _minute) {
        get_elem("#time-hour").value = hour;
        get_elem("#time-minute").value = (minute < 10 ? "0" + minute : minute);
    }
}

/* ========================================================================== */

/* Calendar */


function initCalendar(calendar) {
    const date = moment();
    calendarSetDate(date);

    get_elem('#calendar-next-month').addEventListener("click", function (e) {
        calendarSetDate(calendar_data.add(1, "months"));
        e.preventDefault();
        return false;
    });

    get_elem("#calendar-prev-month").addEventListener("click", function () {
        calendarSetDate(calendar_data.subtract(1, "months"));
        e.preventDefault();
        return false;
    });

    calendar.addEventListener("click", function (e) {
        if (e.target.matches('button.day')) {
            toggleDay(e.target);
        } else if (e.target.matches("button.week") || e.target.parentNode.matches("button.week")) {
            const tr = e.target.closest("tr");
            const cls = tr.querySelectorAll("button.day.default").length > 0 ? ".default" : ".btn-success";
            tr.querySelectorAll("button.day" + cls).forEach(function (el) {
                toggleDay(el)
            });
        }
        return false;
    });
}

function toggleDay(btn) {
    let date = calendar_data;
    date.date(btn.textContent);
    const datetime = date.format("YYYY-MM-DD");
    if (dates.contains(datetime)) {
        removeDate(datetime);
    } else {
        addDate(datetime);
    }
}

function calendarSetDate(date) {
    date = date.startOf("month"); // first day of the month
    calendar_data = date;
    updateMonth();
}

function updateMonth() {
    const date = calendar_data;

    calendar.querySelector(".title").textContent = date.format("MMMM YYYY");
    calendar.querySelectorAll(".week").forEach(function (el) {
        el.remove()
    });

    let week = [];
    const start = date.isoWeekday();
    const endDay = date.endOf("month").date();
    const end = Math.ceil((endDay + start) / 7) * 7;
    for (let i = 1; i <= end; ++i) {
        let day = i - start;
        week.push(day >= 0 && day < endDay ? day + 1 : 0);
        if (i % 7 === 0) {
            makeWeek(week);
            week = [];
        }
    }
}

function makeWeek(week) {
    const tr = document.createElement('tr');
    addClass(tr, 'week');

    let end = moment(calendar_data);
    end.date(week[6]);
    let start = moment(calendar_data);
    start.date(week[0]);
    let past = end.isBefore(moment());
    const future = start.isAfter(moment());
    if (past && !future) {
        tr.insertAdjacentHTML('beforeend', '<td class="left"></td>')
    } else {
        tr.insertAdjacentHTML('beforeend', '<td class="left"><button class="week btn btn-sm"><i class="fa fa-angle-double-right"></i></button></td>')
    }

    for (let i = 0; i < 7; ++i) {
        let btn = "";
        if (week[i] !== 0) {
            let date = calendar_data;
            date.date(week[i]);
            let datetime = date.format("YYYY-MM-DD");
            // alert(datetime);
            const enabled = dates.contains(datetime);
            past = date.isBefore(moment());
            const t = (past && !enabled ? 'span' : 'button');
            btn = '<' + t + ' class="day ' + (enabled ? 'btn btn-sm btn-success' : (past ? '' : 'btn btn-sm default')) + '">' + week[i] + '</' + t + '>';
        }
        tr.insertAdjacentHTML('beforeend', '<td>' + btn + '</td>');
    }
    calendar.querySelector("table tbody").append(tr);
}
