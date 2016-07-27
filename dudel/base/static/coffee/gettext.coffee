class Localisator
    readyListeners: []
    po: null
    default: "en"

    load: (locale) ->
        if locale == @default
            @_callReadyListeners()
            return

        self = this
        $.ajax
            url: "/static/translations/#{locale}.po"
            success: (data) =>
                @po = PO.parse(data)
                @_callReadyListeners()
            error: =>
                @_callReadyListeners()

    _callReadyListeners: ->
        @readyListeners.each (callback) =>
            callback(@gettext.bind(@))
        @readyListeners = null

    ready: (callback) ->
        if @po
            callback(@gettext.bind(@))
        else
            @readyListeners.push callback

    gettext: (key) ->
        if @po?
            items = @po.items.filter (item) ->
                item.msgid == key

            if items
                return items[0].msgstr[0]

        return key

i18n = new Localisator()
