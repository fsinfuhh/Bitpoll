new autoComplete({
    selector: search_selector,
    minChars: 3,
    source: function (term, suggest) {
        console.log(term);
        try {
            xhr.abort();
        } catch (e) {
        }
        console.log("request");
        xhr = $.getJSON(search_url, {term: term}, function (data) {
            suggest(data);
        });
    },
    renderItem: function (item, search) {
        console.log(item);
        search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
        return '<div class="autocomplete-suggestion" data-item="' + encodeURIComponent(JSON.stringify(item)) + '">' +
            item['displayname'] + ' (' + item['username'] + ') ' + '</div>';
    },
    onSelect: function ({event, value, choice, object, method}) {
        let person = JSON.parse(decodeURIComponent(choice.getAttribute('data-item')));
        document.querySelector("#personen-suche-id").value = person['id'];
        object.value = person['displayname'] + ' (' + person['username'] + ')';

        object.form.elements["submit"].click()
    }
});