Vue.component("modal", {
  template: "#review-modal-template",
  delimiters: ["${", "}"],
  props: {
    project_year: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      errors: null,
    }
  },
  methods: {

    onSubmit() {
      this.errors = null
      if (this.mtype === "staff") {
        if (this.my_staff) {
          let endpoint = `/api/project-planning/staff/${this.my_staff.id}/`;
          apiService(endpoint, "PATCH", this.staff).then(response => {
            if (response.id) this.$emit('close')
            else {
              var myString = "";
              for (var i = 0; i < Object.keys(response).length; i++) {
                key = Object.keys(response)[i]
                myString += String(key) + ": " + response[key] + "<br>"
              }
              this.errors = myString
            }
          })
        } else {
          let endpoint = `/api/project-planning/project-years/${this.year.id}/staff/`;
          apiService(endpoint, "POST", this.staff).then(response => {
            if (response.id) this.$emit('close')
            else {
              var myString = "";
              for (var i = 0; i < Object.keys(response).length; i++) {
                key = Object.keys(response)[i]
                myString += String(key) + ": " + response[key] + "<br>"
              }
              this.errors = myString
            }
          })
        }
      }
    },
  },
  computed: {},
  created() {
  },
});