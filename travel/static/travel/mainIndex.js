var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    // loading flags
    loading_user: false,
    loading_adm_hit_list: false,
    loading_adm_verification_list: false,
    loading_regional_verification_list: false,
    loading_rdg_approval_list: false,

    // tabs
    showOverview: true,
    showTraveller: false,
    showReviewer: false,
    showRegions: false,
    showNCR: false,
    showSupport: false,

    currentUser: {},
    userRequests: [],
    userTripReviews: [],
    userTripRequestReviews: [],
    admVerificationCount: 0,
    admHitCount: 0,
    regionalVerificationCount: 0,
    regionalRDGApprovalCount: 0,

    // vuetify
    alignTop: false,
    avatar: false,
    dense: false,
    fillDot: false,
    hideDot: false,
    icon: false,
    iconColor: false,
    left: false,
    reverse: false,
    right: false,
    small: false,

  },
  methods: {
    getCurrentUser() {
      this.loading_user = true;
      let endpoint = `/api/travel/user/`;
      apiService(endpoint)
          .then(response => {
            this.loading_user = false;
            this.currentUser = response;
            if (this.currentUser.is_ncr_admin) this.getADMTrips();
            if (this.currentUser.is_regional_admin) this.getRegionalAdminStuff();
          })
    },
    getADMTrips() {
      this.loading_adm_verification_list = true;
      this.loading_adm_hit_list = true;
      apiService(`/api/travel/trips/?adm-verification=true`)
          .then(response => {
            this.loading_adm_verification_list = false;
            this.admVerificationCount = response.count;
          })
      apiService(`/api/travel/trips/?adm-hit-list=true`)
          .then(response => {
            this.loading_adm_hit_list = false;
            this.admHitCount = response.count;
          })
    },
    getRegionalAdminStuff() {
      this.loading_regional_verification_list = true;
      this.loading_rdg_approval_list = true;
      apiService(`/api/travel/trips/?regional-verification=true`)
          .then(response => {
            this.loading_regional_verification_list = false;
            console.log(response)
            this.regionalVerificationCount = response.count;
          })
      apiService(`/api/travel/request-reviewers/?rdg=true`)
          .then(response => {
            this.loading_rdg_approval_list = false;
            if (response.length) this.regionalRDGApprovalCount = response.length;
          })
    },
    changeTabs(tabFlag) {
      this.showOverview = false;
      this.showTraveller = false;
      this.showReviewer = false;
      this.showRegions = false;
      this.showNCR = false;
      this.showSupport = false;
      this[tabFlag] = true;
    }

    // openCostPopout(costId) {
    //   popitup(`/travel-plans/trip-request-cost/${costId}/edit/`)
    // }


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
    isAdmin() {
      return this.currentUser.is_regional_admin;
    },
    isNCRAdmin() {
      return this.currentUser.is_ncr_admin;
    },
  },
  created() {
    this.getCurrentUser()
  },
  mounted() {
  },
  vuetify: new Vuetify()
  // data: () => ({
  //   alignTop: false,
  //   avatar: false,
  //   dense: false,
  //   fillDot: false,
  //   hideDot: false,
  //   icon: false,
  //   iconColor: false,
  //   left: false,
  //   reverse: false,
  //   right: false,
  //   small: false,
  // }),

});
