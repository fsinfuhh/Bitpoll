function get_slug(s) {
    s = s.replace(/[\s+]+/g, '-');
    s = s.replace(/[^a-zA-Z0-9_-]+/g, '');
    s = s.replace(/-+/g, '-');
    s = s.replace(/(^\-*|\-*$)/g, '');
    s = s.toLowerCase();
    return s;
}

Array.prototype.uniquify = function() {
    return this.filter(function(elem, pos, self) {
        return self.indexOf(elem) === pos;
    });
};

Array.prototype.removeValue = function(item) {
    for(let i = this.length; i--;) {
        if(this[i] === item) {
            this.splice(i, 1);
        }
    }
};

Array.prototype.contains = function(item) {
    return this.indexOf(item) !== -1;
};

function rotate_element(element, degrees) {
    element.style.cssText =
        'transform: rotate(' + degrees + 'deg);' +
        'zoom: 1;';
}

function get_elem(selector) {
    return document.querySelector(selector);
}

function get_elems(selector) {
    return document.querySelectorAll(selector);
}

// Class Handlers
function hasClass(elem, className) {
    return new RegExp(' ' + className + ' ').test(' ' + elem.className + ' ');
}

function addClass(elem, className) {
    if (!hasClass(elem, className)) {
        elem.className += ' ' + className;
    }
}

function removeClass(elem, className) {
    let newClass = ' ' + elem.className.replace( /[\t\r\n]/g, ' ') + ' ';
    if (hasClass(elem, className)) {
        while (newClass.indexOf(' ' + className + ' ') >= 0 ) {
            newClass = newClass.replace(' ' + className + ' ', ' ');
        }
        elem.className = newClass.replace(/^\s+|\s+$/g, '');
    }
}

function hide_elems_selector(selector) {
    get_elems(selector).forEach(function (el) {
        hide_elem(el);
    })
}

function hide_elem(el) {
    addClass(el, 'd-hide');
}

function show_elem(el) {
    removeClass(el, 'd-hide');
}