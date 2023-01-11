$(".under-dev").click(function (e) {
  alert("This feature is still under development.");
  e.preventDefaults();
  e.stopPropagation();
  e.stopImmediatePropagation();
})
