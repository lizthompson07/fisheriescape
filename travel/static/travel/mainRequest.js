Vue.component('v-select', VueSelect.VueSelect);
var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    loading_request: true,
    loading_reviewers: false,
    loading_user: false,
    loadingDMAppsUsers: false,

    isReview: isReview,  // declared in template SCRIPT tag

    showAdminNotesForm: false,
    reviewerEditMode: false,

    currentUser: {},
    request: {},
    dmAppsUsers: [],

    reviewerLabels: {},
    travellerLabels: {},
    fileLabels: {},
    roleChoices: [],
  },
  methods: {
    deleteReviewer(reviewer) {
      userInput = confirm(deleteReviewerMsg);
      if (userInput) {
        let endpoint = `/api/travel/request-reviewers/${reviewer.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              this.$delete(this.request.reviewers, this.request.reviewers.indexOf(reviewer))
            })
      }
    },
    closeReviewerForm() {
      this.getRequest();
      this.reviewerEditMode = false;
    },
    updateReviewer(reviewer) {
      let endpoint = `/api/travel/request-reviewers/${reviewer.id}/`;
      apiService(endpoint, "PUT", reviewer)
          .then(response => {
            reviewer = response;
          })
    },
    getReviewerMetadata() {
      let endpoint = `/api/travel/meta/models/request-reviewer/`;
      apiService(endpoint).then(data => {
        this.reviewerLabels = data.labels;
        this.roleChoices = data.role_choices;
      });
    },
    getTravellerMetadata() {
      let endpoint = `/api/travel/meta/models/traveller/`;
      apiService(endpoint).then(data => {
        this.travellerLabels = data.labels;
      });
    },
    getFileMetadata() {
      let endpoint = `/api/travel/meta/models/file/`;
      apiService(endpoint).then(data => {
        this.fileLabels = data.labels;
      });
    },
    fetchDMAppsUsers() {
      this.loadingDMAppsUsers = true;
      let endpoint = `/api/shared/users/?page_size=50000`;
      apiService(endpoint).then(data => {
        this.dmAppsUsers = data.results;
        this.loadingDMAppsUsers = false;
      });
    },
    goRequestReviewerReset() {
      userInput = confirm(requestReviewerResetMsg)
      if (userInput) {
        window.location.href = `/travel-plans/requests/${tripRequestId}/reset-reviewers/`;
      }
    },
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
      this.loading_request = true;
      let endpoint = `/api/travel/requests/${tripRequestId}/`;
      apiService(endpoint)
          .then(response => {
            this.loading_request = false;
            this.request = response;
            this.getCurrentUser(response);
            this.$nextTick(() => {
              // enable popovers everywhere
              $('[data-toggle="popover"]').popover({html: true});
            })
          })
    },
    updateRequestAdminNotes() {
      if (this.currentUser.is_admin) {
        let endpoint = `/api/travel/requests/${tripRequestId}/`;
        apiService(endpoint, "PATCH", {admin_notes: this.request.admin_notes})
            .then(response => {
              this.getRequest()
              this.showAdminNotesForm = false;
            })
      }
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
    canModify() {
      if (this.currentUser && this.currentUser.can_modify) {
        return this.currentUser.can_modify;
      }
      return false;
    },
    isOwner() {
      if (this.currentUser && this.currentUser.is_owner) {
        return this.currentUser.is_owner;
      }
      return false;
    },
    isAdmin() {
      if (this.currentUser && this.currentUser.is_admin) {
        return this.currentUser.is_admin;
      }
      return false;
    },
  },
  created() {
    this.getRequest();
    this.fetchDMAppsUsers();
    this.getReviewerMetadata();
    this.getFileMetadata();
    this.getTravellerMetadata();
  },
  mounted() {
  },
});
