var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    fte_table_loading: false,
    fte_table: [],
  },
  methods: {
    getFTETable() {
      this.fte_table_loading = true;
      let endpoint = `/api/project-planning/fte-breakdown/`;
      apiService(endpoint)
          .then(response => {
            this.fte_table_loading = false;
            this.fte_table = response;
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
    this.getFTETable()
  },
  mounted() {
  },
});

