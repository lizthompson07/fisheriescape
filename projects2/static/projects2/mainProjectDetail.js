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
    },

    closeModals(projectYear = null) {
      this.showStaffModal = false;

      if (projectYear) {
        this.$nextTick(() => {
          this.getStaff(projectYear.id)

        })
      }
    },


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
      if (value == null) return '';
      value = Number(value).toFixed(precision);
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
    year: {
      type: Object,
      required: true,
    }
  },
  data() {
    return {
      staff: {
        name: null,
        user: null,
        funding_source: null,
        is_lead: null,
        employee_type: null,
        level: null,
        duration_weeks: null,
        overtime_hours: null,
        overtime_description: null,
        student_program: null,
        amount: 0,
        form_error: null
      },
      disableNameField: false,
      disableStudentProgramField: false,
      disableAmountField: false,
      disableLevelField: false,
      projectLeadWarningIssued: false,
    }
  },
  methods: {
    onSubmit() {
      if (this.type === "staff") {

        let endpoint = `/api/project-planning/project-years/${this.year.id}/staff/`;
        apiService(endpoint, "POST", this.staff).then(response => {
          console.log(response)
          
          // this.$emit('close')
        })
      }

      // regardless of what happens, emit a `close` signal
      // this.$emit('close')

    },
    adjustStaffFields() {


      // if not a student, disable the student program field
      if (this.staff.employee_type !== "4") {
        this.staff.student_program = null;
        this.disableStudentProgramField = true;
      } else {
        this.disableStudentProgramField = false;
      }

      // if employee type is fte, disable "cost" field and the "level" field.
      // do the same If they are a seasonal indeterminate  paid from a-base
      if (this.staff.employee_type === "1" || (this.staff.employee_type === "6" && this.staff.funding_source === "1")) {
        this.staff.amount = null;
        this.disableAmountField = true;
        this.staff.level = null;
        this.disableLevelField = true;
      } else {
        this.disableAmountField = false;
        this.disableLevelField = false;
      }


      // if there is a DFO user, disable the text name field
      if (this.staff.user && this.staff.user.length) {
        this.staff.name = null;
        this.disableNameField = true;
      } else {
        this.disableNameField = false;
      }
      // if the current user is changing themselves away from project lead, give them a warning
      if (currentUser === this.staff.user && !this.staff.is_lead && !this.projectLeadWarningIssued) alert(warningMsg);

    }
  },
  created() {
    this.$nextTick(() => {
      this.adjustStaffFields()
      activateChosen()
    })

  }
});