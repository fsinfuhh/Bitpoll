makeRandomString = (length) ->
    text = ""
    possible = "ABCDEFGHJKLMNPQRTUVWXYZabcdefghjkmnpqrstuvwxyz0123456789"

    for i in [0...length]
        text += possible.charAt(Math.floor(Math.random() * possible.length))

    return text

$ ->
    $randomizeButton = $ '#slug-randomize'
    $title           = $ '#title-input'
    $slugInput       = $ '#slug-input'
    $randomSlug      = $ '#random_slug'

    # Check if we are on a page with a slug input
    return if $title.length == 0

    $randomSlug.prop('checked', RANDOM_SLUGS)

    update = (random) ->
        title     = $title.val()
        slug = $slugInput.val()

        if $randomSlug.prop('checked') or random or not title
            if not slug or random or slug == "None" #  Do not regenerate the slug if a random slug is already set
                slug = makeRandomString 8
        else
            slug = get_slug title

        $slugInput.val slug

    updateTitle = ->
        update(false)
        return false

    updateRandom = ->
        update(true)
        $randomSlug.prop('checked', true)
        return false

    updateRandomSlug = ->
        $slugInput.val '' #  reset the current slug
        update(false)
        return true


    # Bind events
    $randomizeButton.on "click", updateRandom
    $title.on "input", updateTitle
    $randomSlug.on "click", updateRandomSlug
    update(false)
