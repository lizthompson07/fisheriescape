Vue.component("modal", {
  template: "#review-modal-template",
  delimiters: ["${", "}"],
  props: {
    project_year: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      errors: null,
    }
  },
  methods: {
    deleteReview() {
      msg = deleteReviewMsg
      userInput = confirm(msg)
      if (userInput) {
        let endpoint = `/api/project-planning/reviews/${this.project_year.review.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              this.project_year.review = null
              this.$emit('close', this.project_year)
            })
      }

    },
    onSubmit() {
      this.errors = null
      if (this.isOldReview) {
        let endpoint = `/api/project-planning/reviews/${this.project_year.review.id}/`;
        apiService(endpoint, "PUT", this.project_year.review).then(response => {
          if (response.id) this.$emit('close', this.project_year)
          else {
            var myString = "";
            for (var i = 0; i < Object.keys(response).length; i++) {
              key = Object.keys(response)[i]
              myString += String(key) + ": " + response[key] + "<br>"
            }
            this.errors = myString
          }
        })
      } else {
        let endpoint = `/api/project-planning/project-years/${this.project_year.id}/reviews/`;
        apiService(endpoint, "POST", this.project_year.review).then(response => {
          if (response.id) {
            this.project_year.review = response
            this.$emit('close', this.project_year)
          } else {
            var myString = "";
            for (var i = 0; i < Object.keys(response).length; i++) {
              key = Object.keys(response)[i]
              myString += String(key) + ": " + response[key] + "<br>"
            }
            this.errors = myString
          }
        })
      }
    },
  },
  computed: {
    isOldReview() {
      return this.project_year.review && this.project_year.review.id
    }
  },
  created() {
  },
});