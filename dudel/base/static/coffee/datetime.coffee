i18n.ready (gettext) ->
    $(".datetime-input").each ->
        # Hide the original input
        hidden = $ this
        hidden.attr "type", "hidden"
        defaultValue  = hidden.val()

        timezone = hidden.attr "data-timezone"

        # Create the new input
        input = $ '<input type="text" />'
        input.addClass "form-control"
        input.attr "placeholder", hidden.attr "placeholder"
        input.attr "placeholder", gettext("e.g. \"in 2 weeks at 12:00\"")
        input.val defaultValue
        input.insertAfter hidden

        # Get translations and build template
        success          = if timezone \
            then gettext('Interpreted as %(date)s at %(time)s in timezone %(timezone)s.') \
            else gettext('Interpreted as %(date)s at %(time)s.')
        failure          = gettext('Could not parse date.')
        empty            = gettext('No date selected.')

        # Insert html stuff
        success = success.replace('%(date)s', '<span class="date"></span>')
        success = success.replace('%(time)s', '<span class="time"></span>')
        success = success.replace('%(timezone)s', '<span class="timezone"></span>')

        # Create the suggestion display
        display = $ "
        <div class='help-block datetime-input-suggest'>
            <div class='success'>#{success}</div>
            <div class='failure'>#{failure}</div>
            <div class='empty'>#{empty}</div>
        </div>"
        display.insertAfter input

        displayDate     = display.find ".date"
        displayTime     = display.find ".time"
        displayTimezone = display.find ".timezone"

        # Hook up date.js
        update = ->
            value = input.val()
            if not value
                display.find("div").hide()
                display.find(".empty").show()
                hidden.val ""
                return

            date = Date.future(value)
            if date instanceof Date and isFinite(date)
                displayDate.text date.format '{Weekday}, {d} {Month}, {yyyy}'
                displayTime.text date.format '{24hr}:{mm}'
                displayTimezone.text timezone if timezone
                display.find("div").hide()
                display.find(".success").show()
                hidden.val date.format '{yyyy}-{MM}-{dd} {HH}:{mm}'
            else
                display.find("div").hide()
                display.find(".failure").show()
                hidden.val defaultValue

        input.on "keyup", update
        update()
