Vue.component("modal", {
  template: "#modal-template",
  delimiters: ["${", "}"],
  props: {
    mtype: {
      type: String,
      required: true,
    },
    my_file: {
      type: Object,
      required: false,
    },
    my_update: {
      type: Object,
      required: false,
    },
  },
  data() {
    return {
      errors: null,

      // files
      fileToUpload: null,
      file: {
        name: null,
        external_url: null,
      },

      // updates
      update: {
        status: "",
        notes: "",
      },

    }
  },
  methods: {
    onFileChange() {
      this.fileToUpload = this.$refs.file.files[0];
    },

    onSubmit() {
      this.errors = null;

      if (this.mtype === "file") {

        // file

        if (this.my_file) {
          // if there is a file attribute, delete it since we send back the file through a separate request
          if (this.file.file) delete this.file.file

          let endpoint = `/api/project-planning/files/${this.my_file.id}/?status_report=${statusReportId}`;
          apiService(endpoint, "PATCH", this.file).then(response => {
            if (response.id) {
              if (this.fileToUpload) {
                fileApiService(endpoint, "PATCH", "file", this.fileToUpload)
                this.fileToUpload = null
              }
              this.$emit('close')
            } else {
              var myString = "";
              for (var i = 0; i < Object.keys(response).length; i++) {
                key = Object.keys(response)[i]
                myString += String(key) + ": " + response[key] + "<br>"
              }
              this.errors = myString
            }
          })
        } else {
          let endpoint = `/api/project-planning/project-years/${projectYearId}/files/?status_report=${statusReportId}`;
          apiService(endpoint, "POST", this.file).then(response => {
            if (response.id) {
              // now we have to upload the file
              if (this.fileToUpload) {
                let endpoint = `/api/project-planning/files/${response.id}/`;
                fileApiService(endpoint, "PATCH", "file", this.fileToUpload)
                this.fileToUpload = null
              }
              this.$emit('close')
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
      } else if (this.mtype === "update") {
        if (this.my_update) {
          // should really only be one option here
          let endpoint = `/api/project-planning/activity-updates/${this.my_update.id}/`;
          apiService(endpoint, "PATCH", this.update).then(response => {
            if (response.id) {
              this.$emit('close')
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
      }

    },

    getCurrentUser() {
      let endpoint = `/api/project-planning/user/`;
      apiService(endpoint)
          .then(response => {
            this.currentUser = response;
          })
    },
  },
  computed: {},
  created() {

    this.getCurrentUser();

    this.$nextTick(() => {

      if (this.mtype === "update") {
        if (this.my_update && this.my_update.id) {
          this.update = this.my_update
        }
      } else if (this.mtype === "file") {
        if (this.my_file && this.my_file.id) {
          this.file = this.my_file
        }
      }
    })


  },

});