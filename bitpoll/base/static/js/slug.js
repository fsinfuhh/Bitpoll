(function () {
    let makeRandomString;

    makeRandomString = function (length) {
        let i, j, possible, ref, text;
        text = "";
        possible = "ABCDEFGHJKLMNPQRTUVWXYZabcdefghjkmnpqrstuvwxyz0123456789";
        for (i = j = 0, ref = length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    };

    (function () {
        let $randomSlug, $randomizeButton, $slugInput, $title, update, updateRandom, updateRandomSlug, updateTitle;
        $randomizeButton = get_elem('#slug-randomize');
        $title = get_elem('#id_title');
        $slugInput = get_elem('#slug-input');
        $randomSlug = get_elem('#random_slug');

        // Check if we are on a page with a slug input
        if ($title.length === 0) {
            return;
        }

        update = function (random) {
            let title = $title.value;
            let slug = $slugInput.value;
            if ($randomSlug.checked || random || !title) {
                // Do not regenerate the slug if a random slug is already set
                if (!slug || random || slug === "None") {
                    slug = makeRandomString(8);
                }
            } else {
                slug = get_slug(title);
            }
            return $slugInput.value = slug;
        };
        updateTitle = function (e) {
            update(false);
            return false;
        };
        updateRandom = function (e) {
            update(true);
            $randomSlug.checked = true;
            e.preventDefault()
        };
        updateRandomSlug = function (e) {
            $slugInput.value = '';  // reset the current slug
            update(false);
        };

        // Bind events
        $randomizeButton.addEventListener("click", updateRandom);
        $title.addEventListener("keyup", updateTitle);
        $randomSlug.addEventListener("click", updateRandomSlug);
    }).call();

}).call();
