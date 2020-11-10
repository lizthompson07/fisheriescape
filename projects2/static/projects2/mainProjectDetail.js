var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    showOverview: true,

    py_loading: false,
    projectYear: {},

    staff_loading: false,
    staff: [],
    showStaffModal: false,
  },
  methods: {
    displayOverview() {
      this.showOverview = true
    },
    displayProjectYear(yearId) {
      this.showOverview = false
      this.getProjectYear(yearId)
    },
    getProjectYear(yearId) {
      this.py_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/`;
      apiService(endpoint)
          .then(response => {
            this.py_loading = false;
            this.projectYear = response;
            // now let's get all the related data
            this.getStaff(yearId)


          })
    },
    getStaff(yearId) {
      this.staff_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/staff/`;
      apiService(endpoint)
          .then(response => {
            this.staff_loading = false;
            this.staff = response;
          })
    },
    deleteStaffMember(staffMember) {
      let endpoint = `/api/project-planning/staff/${staffMember.id}/`;
      apiService(endpoint, "DELETE")
          .then(response => {
            this.getStaff(staffMember.project_year);
          })
    },
    openStaffModal() {
      this.showStaffModal = true;
      this.$nextTick(() => this.activateChosen())

    },

    closeModals() {
      this.showStaffModal = false;
    },

    activateChosen() {
      var config = {
        '.chosen-select': {placeholder_text_multiple: "Select multiple", search_contains: false},
        '.chosen-select-contains': {placeholder_text_multiple: "Select multiple", search_contains: true},
      };
      for (var selector in config) {
        $(selector).chosen(config[selector]);
      }
    }



    // goBack() {
    //   this.$refs.back.click();
    // },
    // getCatch: function () {
    //   let endpoint = `/api/catch/${catch_id}/`;
    //   apiService(endpoint)
    //       .then(response => {
    //         this.catchObj = response;
    //         if (!this.startingBoxIsFocused) {
    //           this.getSpecimenSummary();
    //           this.$nextTick(() => this.$refs.back.focus());
    //           this.startingBoxIsFocused = true;
    //         }
    //         this.loading1 = false;
    //       }).finally(() => {
    //         // if ever we loose the connection to the api, we should reset the starting box focus flag
    //         if (!this.catchObj || !this.catchObj.is_set_active) {
    //           this.startingBoxIsFocused = false;
    //         }
    //       }
    //   )
    // },

  },
  filters: {
    floatformat: function (value, precision = 2) {
      if (!value) return '';
      value = value.toFixed(precision);
      return value
    },
    zero2NullMark: function (value) {
      if (!value || value === "0.00" || value == 0) return '---';
      return value
    },
    nz: function (value, arg = "---") {
      if (value == null) return arg;
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

    // isActive() {
    //   return this.catchObj && this.catchObj.is_set_active
    // }

  },
  created() {
    // this.getCatch();
    // this.getSpecimenSummary();

  },
  mounted() {
    // this.interval = setInterval(() => this.getCatch(), 15000);
  },
});


Vue.component("modal", {
  template: "#modal-template",
  delimiters: ["${", "}"],
  props: {
    type: {
      type: String,
      required: true,
    },
    projectYear: {
      type: Object,
      required: true,
    }
  },
  data() {
    return {
      species_query: "",
      species_list: [],
      loading: false,
      currentItemId: -1,
    }
  },
  methods: {
    onSubmit() {

    },
  }
});