var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    loading_request: true,
    loading_user: false,

    isReview: isReview,  // declared in template SCRIPT tag

    currentUser: {},
    request: {},
  },
  methods: {
    getCurrentUser(request) {
      this.loading_user = true;
      let endpoint = `/api/travel/user/?request=${request.id}`;
      apiService(endpoint)
          .then(response => {
            this.loading_user = false;
            this.currentUser = response;
          })
    },
    getRequest() {
      this.loading_costs = true;
      let endpoint = `/api/travel/requests/${tripRequestId}/`;
      apiService(endpoint)
          .then(response => {
            this.loading_request = false;
            this.request = response;
            this.getCurrentUser(response);
          })
    },
    deleteTraveller(traveller) {
      let userInput = confirm(travellerDeleteMsg);
      if (userInput) {
        let endpoint = `/api/travel/travellers/${traveller.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              console.log(response);
              this.getRequest();
            })
      }
    },
    expandTravellers() {
      for (var i = 0; i < this.request.travellers.length; i++) this.request.travellers[i].hide_me = false;
      this.$forceUpdate()
    },
    collapseTravellers() {
      for (var i = 0; i < this.request.travellers.length; i++) this.request.travellers[i].hide_me = true;
      this.$forceUpdate()
    }
  },
  filters: {
    floatformat: function (value, precision = 2) {
      if (!value) return '---';
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
    canModify(){
      if(this.currentUser && this.currentUser.can_modify) {
        return this.currentUser.can_modify;
      }
      return false;
    },
  },
  created() {
    this.getRequest();
  },
  mounted() {
  },
});
