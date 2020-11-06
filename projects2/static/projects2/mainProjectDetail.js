var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    showOverview: true,
    projectYear: {},
    py_loading: false,
    // specimenList: [],
    // specimenSummary: null,
    // error_msg: null,
    // startingBoxIsFocused: false,
    // currentItemId: 0,
    // modalIsOpened: false,
    // loading2: true,
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
      let endpoint = `/api/project-years/${yearId}/`;
      apiService(endpoint)
          .then(response => {
            this.py_loading = false;
            this.projectYear = response;
          })
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


