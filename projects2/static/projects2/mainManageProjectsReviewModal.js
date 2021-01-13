Vue.component("modal", {
  template: "#review-modal-template",
  delimiters: ["${", "}"],
  props: {
    project_year: {
      type: Object,
      required: true,
    },
    approval_form: {
      type: Boolean,
      required: false,
    },
  },
  data() {
    return {
      errors: null,
      loading: false,
      rubric: reviewRubric,
    }
  },
  methods: {
    closeModal() {
      // if the form was not saved...
      if (!this.project_year.review.id) {
        this.project_year.review.collaboration_score = ""
        this.project_year.review.strategic_score = ""
        this.project_year.review.operational_score = ""
        this.project_year.review.ecological_score = ""
        this.project_year.review.scale_score = ""
      }
      this.$emit('close')
    },

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
      this.loading = true

      if (this.project_year.review.collaboration_score === "") this.project_year.review.collaboration_score = null
      if (this.project_year.review.strategic_score === "") this.project_year.review.strategic_score = null
      if (this.project_year.review.operational_score === "") this.project_year.review.operational_score = null
      if (this.project_year.review.ecological_score === "") this.project_year.review.ecological_score = null
      if (this.project_year.review.scale_score === "") this.project_year.review.scale_score = null
      if (this.project_year.review.approval_status === "") this.project_year.review.approval_status = null
      if (this.project_year.review.approval_level === "") this.project_year.review.approval_level = null

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
            this.loading = false

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
            this.loading = false

          }
        })
      }
    },
  },
  computed: {
    isOldReview() {
      return this.project_year.review && this.project_year.review.id
    },
    total_score() {
      collaboration_score = 0
      strategic_score = 0
      operational_score = 0
      ecological_score = 0
      scale_score = 0
      if (this.project_year.review.collaboration_score) collaboration_score = Number(this.project_year.review.collaboration_score)
      if (this.project_year.review.strategic_score) strategic_score = Number(this.project_year.review.strategic_score)
      if (this.project_year.review.operational_score) operational_score = Number(this.project_year.review.operational_score)
      if (this.project_year.review.ecological_score) ecological_score = Number(this.project_year.review.ecological_score)
      if (this.project_year.review.scale_score) scale_score = Number(this.project_year.review.scale_score)
      return scale_score + ecological_score + operational_score + strategic_score + collaboration_score
    },
    total_score_percentage() {
      value = this.total_score / 15
      if (!value) value = 0;
      value = value * 100;
      value = Math.round(value * Math.pow(10, 0)) / Math.pow(10, 0);
      value = value + '%';
      return value;
    },
  },
  created() {
    if (this.project_year.review.id) {
      if (!this.project_year.review.collaboration_score) this.project_year.review.collaboration_score = ""
      if (!this.project_year.review.strategic_score) this.project_year.review.strategic_score = ""
      if (!this.project_year.review.operational_score) this.project_year.review.operational_score = ""
      if (!this.project_year.review.ecological_score) this.project_year.review.ecological_score = ""
      if (!this.project_year.review.scale_score) this.project_year.review.scale_score = ""
    }

  },
});