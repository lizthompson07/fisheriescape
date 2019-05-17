// This file will prime any tagged elements

var config = {
    '.chosen-select': {placeholder_text_multiple: "Select multiple"},
    '.chosen-select-contains': {placeholder_text_multiple: "Select multiple", search_contains: true},
    '.chosen-select-deselect': {allow_single_deselect: true},
    '.chosen-select-no-single': {disable_search_threshold: 10},
    '.chosen-select-no-results': {no_results_text: 'Oops, nothing found!'},
    '.chosen-select-rtl': {rtl: true},
    '.chosen-select-width': {width: '95%'}
};
for (var selector in config) {
    $(selector).chosen(config[selector]);
}


var fpConfig = {
    '.fp-date': {},
    '.fp-date-time': {enableTime: true, time_24hr: true},
};
for (var selector in fpConfig) {
    $(selector).flatpickr(fpConfig[selector]);
}


// for . editable things i.e. medium-editor / medium-editor-table
var editor = new MediumEditor('.editable', {
    buttonLabels: 'fontawesome',
    extensions: {
        table: new MediumEditorTable()
    },
    toolbar: {
        buttons: [
            'h2',
            'bold',
            'italic',
            'unorderedlist',
            'orderedlist',
            'table'
        ],
        static: true,
        sticky: true
    }
});

// enable popovers everywhere
$(function () {
  $('[data-toggle="popover"]').popover();
  $('[data-toggle="popover"]')[0].style.cursor = "pointer";
});