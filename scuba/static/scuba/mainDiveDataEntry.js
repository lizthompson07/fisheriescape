var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    currentUser: null,
    sections: [],
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
      let endpoint = `/api/scuba/sections/`;
      apiService(endpoint)
          .then(response => {
            this.sections = response;
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
  },
  created() {
  },
  mounted() {
  },
});

