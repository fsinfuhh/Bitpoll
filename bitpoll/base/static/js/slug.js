// language=JQuery-CSS
(function () {
    var makeRandomString;

    makeRandomString = function (length) {
        var i, j, possible, ref, text;
        text = "";
        possible = "ABCDEFGHJKLMNPQRTUVWXYZabcdefghjkmnpqrstuvwxyz0123456789";
        for (i = j = 0, ref = length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    };

    $(function () {
        var $randomSlug, $randomizeButton, $slugInput, $title, update, updateRandom, updateRandomSlug, updateTitle;
        $randomizeButton = $('#slug-randomize');
        $title = $('#title-input');
        $slugInput = $('#slug-input');
        $randomSlug = $('#random_slug');

        // Check if we are on a page with a slug input
        if ($title.length === 0) {
            return;
        }

        $randomSlug.prop('checked', RANDOM_SLUGS);
        update = function (random) {
            var slug, title;
            title = $title.val();
            slug = $slugInput.val();
            if ($randomSlug.prop('checked') || random || !title) {
                // Do not regenerate the slug if a random slug is already set
                if (!slug || random || slug === "None") {
                    slug = makeRandomString(8);
                }
            } else {
                slug = get_slug(title);
            }
            return $slugInput.val(slug);
        };
        updateTitle = function () {
            update(false);
            return false;
        };
        updateRandom = function () {
            update(true);
            $randomSlug.prop('checked', true);
            return false;
        };
        updateRandomSlug = function () {
            $slugInput.val('');  // reset the current slug
            update(false);
            return true;
        };

        // Bind events
        $randomizeButton.on("click", updateRandom);
        $title.on("input", updateTitle);
        $randomSlug.on("click", updateRandomSlug);
        return update(false);
    });

}).call();
