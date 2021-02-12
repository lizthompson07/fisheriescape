var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    currentUser: {},
    hover: false,

    currentSort: 'name',
    currentSortDir: 'asc',

    requests_loading: true,
    requests: [],
    next: null,
    previous: null,
    count: 0,

    // filters
    filter_fiscal_year: "",
    filter_trip_title: "",
    filter_status: "",
    filter_traveller: "",
    filter_region: "",
    filter_division: "",
    filter_section: "",

    // dropdowns
    fiscalYears: [],
    regions: [],
    divisions: [],
    sections: [],

  },
  methods: {
    getCurrentUser() {
      let endpoint = `/api/travel/user/`;
      apiService(endpoint)
          .then(response => {
            this.currentUser = response;
          })
    },
    goRequestDetail(request) {
      url = `/travel-plans/requests/${request.id}/view/`;
      var win = window.open(url, '_blank');
    },
    getFilterData() {
      apiService(`/api/travel/fiscal-years/`).then(response => this.fiscalYears = response)
      apiService(`/api/travel/regions/`).then(response => this.regions = response)

      var query = "";
      if (this.filter_region && this.filter_region !== "") query = `?region=${this.filter_region}`
      apiService(`/api/travel/divisions/${query}`).then(response => this.divisions = response)

      if (this.filter_division && this.filter_division !== "") query = `?division=${this.filter_division}`
      apiService(`/api/travel/sections/${query}`).then(response => this.sections = response)

    },
    getRequests(endpoint) {
      this.requests_loading = true;
      if (!endpoint) {
        endpoint = `/api/travel/requests/?`;
        let uri = window.location.search.substring(1);
        let params = new URLSearchParams(uri);
        let typeParam = params.get("all");
        if (typeParam) {
          endpoint += 'all=true;'
        }
        // apply filters
        endpoint += `trip_title=${this.filter_trip_title};` +
            `traveller=${this.filter_traveller};` +
            `status=${this.filter_status};` +
            `fiscal_year=${this.filter_fiscal_year};` +
            `region=${this.filter_region};` +
            `division=${this.filter_division};` +
            `section=${this.filter_section};` +
            `status=${this.filter_status};`
      }

      apiService(endpoint)
          .then(response => {
            if (response.results) {
              this.requests_loading = false;
              this.requests.push(...response.results);
              this.next = response.next;
              this.previous = response.previous;
              this.count = response.count;
            }
          })
    },
    clearRequests() {
      this.requests = []
      this.next = null
      this.count = 0
    },
    loadMoreResults() {
      if (this.next) {
        this.getRequests(this.next)
      }
    },
    clearFilters() {
      this.filter_trip_title = null;
      this.filter_traveller = null;
      this.filter_fiscal_year = "";
      this.filter_status = "";
      this.filter_region = "";
      this.filter_division = "";
      this.filter_section = "";
      this.updateResults()
    },
    updateResults() {
      this.clearRequests();
      this.getRequests();
      this.getFilterData();
    },
    sort(s) {
      // from https://www.raymondcamden.com/2018/02/08/building-table-sorting-and-pagination-in-vuejs
      //if s == current sort, reverse
      if (s === this.currentSort) {
        this.currentSortDir = this.currentSortDir === 'asc' ? 'desc' : 'asc';
      }
      this.currentSort = s;
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
    sortedRequests() {
      return this.requests.sort((a, b) => {
        let modifier = 1;
        if (this.currentSortDir === 'desc') modifier = -1;

        if (this.currentSort && this.currentSort.search("fiscal") > -1) {
          if (a["fiscal_year"] < b["fiscal_year"]) return -1 * modifier;
          if (a["fiscal_year"] > b["fiscal_year"]) return 1 * modifier;
        } else {
          if (a[this.currentSort] < b[this.currentSort]) return -1 * modifier;
          if (a[this.currentSort] > b[this.currentSort]) return 1 * modifier;
        }
        return 0;
      });
    },
  },
  created() {
    this.getCurrentUser()
    this.getRequests()
    this.getFilterData()
  },
  mounted() {
  },
});

