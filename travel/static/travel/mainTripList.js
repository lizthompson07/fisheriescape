var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    currentUser: {},
    hover: false,

    currentSort: 'name',
    currentSortDir: 'asc',

    trips_loading: true,
    trips: [],
    next: null,
    previous: null,
    count: 0,

    // filters
    filter_fiscal_year: "",
    filter_trip_title: "",
    filter_regional_lead: "",
    filter_adm_approval: "",
    filter_status: "",
    filter_subcategory: "",

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
    goRow(trip) {
      if (this.pageType.search("verification") > -1) {
        url = `/travel-plans/trips/${trip.id}/verify/?${this.pageType}=true`;
        window.location.href = url;
      }else if (this.pageType.search("hit-list") > -1) {
        url = `/travel-plans/trips/${trip.id}/review-process/?${this.pageType}=true`;
        window.location.href = url;
      } else {
        url = `/travel-plans/trips/${trip.id}/view/`;
        var win = window.open(url, '_blank');

      }
    },
    getFilterData() {
      apiService(`/api/travel/fiscal-years/`).then(response => this.fiscalYears = response)
      apiService(`/api/travel/regions/`).then(response => this.regions = response)
    },
    getTrips(endpoint) {
      this.trips_loading = true;
      if (!endpoint) {
        endpoint = `/api/travel/trips/?`;
        if (this.pageType === 'all') endpoint += 'all=true;'
        else if (this.pageType === 'adm-hit-list') endpoint += 'adm-hit-list=true;'
        else if (this.pageType === 'adm-verification') endpoint += 'adm-verification=true;'
        else if (this.pageType === 'regional-verification') endpoint += 'regional-verification=true;'

        // apply filters
        endpoint += `trip_title=${this.filter_trip_title};` +
            `regional_lead=${this.filter_regional_lead};` +
            `status=${this.filter_status};` +
            `fiscal_year=${this.filter_fiscal_year};` +
            `adm_approval=${this.filter_adm_approval};` +
            `subcategory=${this.filter_subcategory};`
      }

      apiService(endpoint)
          .then(response => {
            if (response.results) {
              this.trips_loading = false;
              this.trips.push(...response.results);
              this.next = response.next;
              this.previous = response.previous;
              this.count = response.count;
            }
          })
    },
    clearTrips() {
      this.trips = []
      this.next = null
      this.count = 0
    },
    loadMoreResults() {
      if (this.next) {
        this.getTrips(this.next)
      }
    },
    clearFilters() {
      this.filter_fiscal_year = "";
      this.filter_trip_title = null;
      this.filter_regional_lead = null;
      this.filter_adm_approval = "";
      this.filter_status = "";
      this.filter_subcategory = "";
      this.updateResults()
    },
    updateResults() {
      this.clearTrips();
      this.getTrips();
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
    sortedTrips() {
      return this.trips.sort((a, b) => {
        let modifier = 1;
        if (this.currentSortDir === 'desc') modifier = -1;

        if (this.currentSort && this.currentSort.search("fiscal") > -1) {
          if (a["fiscal_year"] < b["fiscal_year"]) return -1 * modifier;
          if (a["fiscal_year"] > b["fiscal_year"]) return 1 * modifier;
        } else if (this.currentSort && this.currentSort.search("title") > -1) {
          if (a["name"] < b["name"]) return -1 * modifier;
          if (a["name"] > b["name"]) return 1 * modifier;
        } else {
          if (a[this.currentSort] < b[this.currentSort]) return -1 * modifier;
          if (a[this.currentSort] > b[this.currentSort]) return 1 * modifier;
        }
        return 0;
      });
    },
    pageType() {
      let uri = window.location.search.substring(1);
      let params = new URLSearchParams(uri);
      params.get("all");
      if (params.get("all")) return 'all';
      else if (params.get("regional-verification")) return 'regional-verification';
      else if (params.get("adm-verification")) return 'adm-verification';
      else if (params.get("adm-hit-list")) return 'adm-hit-list';
      else return "upcoming";
    }

  },
  created() {
    this.getCurrentUser()
    this.getTrips()
    this.getFilterData()
  },
  mounted() {
  },
});

