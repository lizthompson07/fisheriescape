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
    errorMsgReviewer: null,
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
    skipReviewer(reviewer) {
      userInput = prompt(skipReviewerMsg);
      if (userInput) {
        reviewer.comments = userInput;
        console.log(reviewer)
        let endpoint = `/api/travel/request-reviewers/${reviewer.id}/?skip=true`;
        apiService(endpoint, "PUT", reviewer)
            .then(response => {
              if (response.id) {
                this.getRequest();
              } else {
                console.log(response)
                this.errorMsgReviewer = this.groomJSON(response)
              }
            })
      }
    },
    moveReviewer(reviewer, direction) {
      if (direction === 'up') reviewer.order -= 1.5;
      else if (direction === 'down') reviewer.order += 1.5;
      this.request.reviewers.sort((a, b) => {
        if (a["order"] < b["order"]) return -1
        if (a["order"] > b["order"]) return 1
      });
      // reset the order numbers based on position in array
      for (var i = 0; i < this.request.reviewers.length; i++) {
        r = this.request.reviewers[i]
        if (r.status === 4 || r.status === 20) r.order = i;
        else r.order = i - 1000;
        this.updateReviewer(this.request.reviewers[i])
      }
    },
    addReviewer() {
      this.request.reviewers.push({
        request: this.request.id,
        order: this.request.reviewers.length + 1,
        role: null,
        status: 4,  // this will be updated by the model save method. setting status == 4 just allows to show in list
      })
    },
    closeReviewerForm() {
      this.getRequest();
      this.reviewerEditMode = false;
    },
    collapseTravellers() {
      for (var i = 0; i < this.request.travellers.length; i++) this.request.travellers[i].hide_me = true;
      this.$forceUpdate()
    },
    deleteReviewer(reviewer) {
      if (reviewer.id) {
        userInput = confirm(deleteReviewerMsg);
        if (userInput) {
          let endpoint = `/api/travel/request-reviewers/${reviewer.id}/`;
          apiService(endpoint, "DELETE")
              .then(response => {
                this.$delete(this.request.reviewers, this.request.reviewers.indexOf(reviewer))
              })
        }
      } else {
        this.$delete(this.request.reviewers, this.request.reviewers.indexOf(reviewer))
      }
    },
    deleteTraveller(traveller) {
      var userInput = false;
      if (this.request.status === 8) userInput = confirm(travellerDeleteMsgLITE);
      else userInput = confirm(travellerDeleteMsg);
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
    fetchDMAppsUsers() {
      this.loadingDMAppsUsers = true;
      let endpoint = `/api/shared/users/?page_size=50000`;
      apiService(endpoint).then(data => {
        this.dmAppsUsers = data.results;
        this.loadingDMAppsUsers = false;
      });
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
    getFileMetadata() {
      let endpoint = `/api/travel/meta/models/file/`;
      apiService(endpoint).then(data => {
        this.fileLabels = data.labels;
      });
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
    goRequestReviewerReset() {
      userInput = confirm(requestReviewerResetMsg)
      if (userInput) {
        window.location.href = `/travel-plans/requests/${tripRequestId}/reset-reviewers/`;
      }
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
    updateReviewer(reviewer) {
      this.errorMsgReviewer = null;
      if (reviewer.id) {
        let endpoint = `/api/travel/request-reviewers/${reviewer.id}/`;
        apiService(endpoint, "PUT", reviewer)
            .then(response => {
              if (response.id) {
                reviewer = response;
                this.errorMsgReviewer = null;
              } else {
                console.log(response)
                this.errorMsgReviewer = this.groomJSON(response)
              }

            })
      } else {
        let endpoint = `/api/travel/request-reviewers/`;
        apiService(endpoint, "POST", reviewer)
            .then(response => {
              console.log(response)
              if (response.id) {
                this.$delete(this.request.reviewers, this.request.reviewers.indexOf(reviewer))
                this.request.reviewers.push(response)
                this.errorMsgReviewer = null;
              } else {
                this.errorMsgReviewer = this.groomJSON(response)
              }
            })
      }
    },
    groomJSON(json) {
      return JSON.stringify(json).replaceAll("{", "").replaceAll("}", "").replaceAll("[", " ").replaceAll("]", " ").replaceAll('"', "")
    },
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
    editableReviewers() {
      myArray = []
      for (var i = 0; i < this.request.reviewers.length; i++) {
        if (this.request.reviewers[i].status === 4 || this.request.reviewers[i].status === 20) {
          myArray.push(this.request.reviewers[i])
        }
      }
      return myArray
    }
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
