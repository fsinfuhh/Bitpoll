(($) ->
    i18n.ready (gettext) ->
        DATEFORMAT = gettext("{d} {Mon}, {yyyy}")

        $(".dateoffset-input").each ->
            # Get the DOM nodes
            $input       = $ this
            $preview     = $ "#dateoffset-preview"
            $currentFrom = $preview.find ".current .from"
            $currentTo   = $preview.find ".current .to"
            $newFrom     = $preview.find ".new .from"
            $newTo       = $preview.find ".new .to"

            # Get the current range
            currentFrom = Date.create $preview.data("from")
            currentTo   = Date.create $preview.data("to")

            # Update with format
            $currentFrom.text currentFrom.format(DATEFORMAT)
            $currentTo.text   currentTo.format(DATEFORMAT)

            # Update function
            update = ->
                value   = $input.val()
                days    = value.toNumber()
                newFrom = currentFrom.clone().addDays(days)
                newTo   = currentTo.clone().addDays(days)
                if newFrom instanceof Date and isFinite(newFrom)
                    $newFrom.text newFrom.format(DATEFORMAT)
                    $newTo.text   newTo.format(DATEFORMAT)
                else
                    $newFrom.text currentFrom.format(DATEFORMAT)
                    $newTo.text   currentTo.format(DATEFORMAT)

            # Hook up events
            $input.on "keyup", update
            update()
)(jQuery)