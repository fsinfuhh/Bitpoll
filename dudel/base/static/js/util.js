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
        return self.indexOf(elem) == pos;
    });
};

Array.prototype.removeValue = function(item) {
    for(var i = this.length; i--;) {
        if(this[i] === item) {
            this.splice(i, 1);
        }
    }
};

Array.prototype.contains = function(item) {
    return this.indexOf(item) !== -1;
};

$.fn.rotate = function(degrees) {
    $(this).css({
  '-webkit-transform' : 'rotate('+degrees+'deg)',
     '-moz-transform' : 'rotate('+degrees+'deg)',
      '-ms-transform' : 'rotate('+degrees+'deg)',
       '-o-transform' : 'rotate('+degrees+'deg)',
          'transform' : 'rotate('+degrees+'deg)',
               'zoom' : 1
    });
};
    
$.fn.disableSelect = function() {
    return this
         .attr('unselectable', 'on')
         .css('user-select', 'none')
         .on('selectstart', false);
};

$.fn.enableSelect = function() {
    return this
         .attr('unselectable', 'off')
         .css('user-select', 'auto')
         .unbind('selectstart', false);
};
