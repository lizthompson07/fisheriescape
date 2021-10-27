Vue.component("staff-table", {
  template: "#staff-project-template",
  delimiters: ["${", "}"],
  props: {
    staff: {
      type: Object,
      required: true,
    },
  },
  methods: {
    goProjectDetail(projectYear) {
      url = `/ppt/projects/${projectYear.project.id}/view/?project_year=${projectYear.id}`;
      var win = window.open(url, '_blank');
    },
  }
});