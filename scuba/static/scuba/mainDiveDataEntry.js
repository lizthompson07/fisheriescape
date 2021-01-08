var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    currentUser: null,
    sections: [],
    loadingSections: false,
    editMode: false,
    sectionToEdit: null,
    unsavedSectionWork: false,
    sectionFormErrors: null,
  },
  methods: {
    getCurrentUser() {
      let endpoint = `/api/project-planning/user/`;
      apiService(endpoint)
          .then(response => {
            this.currentUser = response;
            this.isAdminOrMgmt = this.currentUser.is_admin || this.currentUser.is_management
          })
    },
    getSections() {
      this.loadingSections = true;
      let endpoint = `/api/scuba/sections/?dive=${diveId}`;
      apiService(endpoint)
          .then(response => {
            this.sections = response;
            this.loadingSections = false;
          })
    },
    closeEditMode() {
      var userInput = true;
      if (this.unsavedSectionWork) {
        msg = "Are you certain you want to leave with un-saved work?";
        userInput = confirm(msg);
      }
      if (userInput) {
        this.unsavedSectionWork = false;
        this.editMode = false;
        this.sectionToEdit = null;
      }
    },
    editSection(section) {
      if (section == null) {
        this.sectionToEdit = {
          comment: "",
          depth_ft: null,
          dive: diveId,
          interval: null,
          observations: [],
          percent_algae: 0,
          percent_cobble: 0,
          percent_gravel: 0,
          percent_hard: 0,
          percent_mud: 0,
          percent_pebble: 0,
          percent_sand: 0,
        }

      } else {
        this.sectionToEdit = section

      }
      this.editMode = true;

      // focus on the save button
      this.$nextTick(() => {
        this.$refs['top_of_form'].focus()
      })

    },
    submitSectionForm() {
      // this is an update
      if (this.sectionToEdit.id) {


      }
      // this is a new section being added
      else {
        let endpoint = `/api/scuba/sections/`;
        apiService(endpoint, "POST", this.sectionToEdit)
            .then(response => {
              console.log(response)
              // if the response does not have an id, it means there is an error...
              if (!response.id) {
                this.sectionFormErrors = response[Object.keys(response)[0]][0]
              } else {

                console.log(response)
              }

            })
      }

    },
    deleteSection(section) {
      let endpoint = `/api/scuba/sections/${section.id}`;
      apiService(endpoint, "DELETE")
          .then(response => {
            // if the response does not have an id, it means there is an error...
            if (response.detail) {
                this.sectionFormErrors = response["detail"]
            } else {
              this.$delete(this.sections, this.sections.indexOf(section))
              this.closeEditMode()
            }

          })

    },


  },
  filters: {
    floatformat: function (value, precision = 2) {
      if (value == null) return '';
      value = Number(value).toFixed(precision).toLocaleString("en");
      return value
    },
    currencyFormat: function (value, precision = 2) {
      if (value == null) return '';
      value = accounting.formatNumber(value, precision);
      return value
    },
    zero2NullMark: function (value) {
      if (!value || value === "0.00" || value == 0) return '---';
      return value
    },
    nz: function (value, arg = "---") {
      if (value == null || value === "None") return arg;
      return value
    },
    yesNo: function (value) {
      if (value == null || value == false || value == 0) return 'No';
      return "Yes"
    },
    percentage: function (value, decimals) {
      // https://gist.github.com/belsrc/672b75d1f89a9a5c192c
      if (!value) {
        value = 0;
      }

      if (!decimals) {
        decimals = 0;
      }

      value = value * 100;
      value = Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
      value = value + '%';
      return value;
    }
  },
  computed: {
    totalPercentage() {
      myString = ((Number(this.sectionToEdit.percent_sand) +
          Number(this.sectionToEdit.percent_mud) +
          Number(this.sectionToEdit.percent_hard) +
          Number(this.sectionToEdit.percent_algae) +
          Number(this.sectionToEdit.percent_gravel) +
          Number(this.sectionToEdit.percent_cobble) +
          Number(this.sectionToEdit.percent_pebble)) * 100).toFixed() + "%"
      if (myString === "99%") myString = "100%"
      return myString
    },
  },
  created() {
    this.getSections();
  },
  mounted() {
  },
});

