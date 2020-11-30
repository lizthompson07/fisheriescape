var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    currentUser: {},
    isAdmin: false,
    isSectionHead: false,
    canModify: false,

    // files
    file_loading: false,
    files: [],
    fileToEdit: {},
    showNewFileModal: false,
    showOldFileModal: false,

    // updates
    update_loading: false,
    updates: [],
    updateToEdit: {},
    showNewUpdateModal: false,
    showOldUpdateModal: false,

  },
  methods: {
    getCurrentUser() {
      let endpoint = `/api/project-planning/user/?status_report=${statusReportId}`;
      apiService(endpoint)
          .then(response => {
            this.currentUser = response;
            this.isAdmin = this.currentUser.is_admin
            this.isSectionHead = this.currentUser.is_section_head
            this.canModify = this.currentUser.can_modify
          })
    },


    getProjectYear(yearId) {
      this.py_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/`;
      apiService(endpoint)
          .then(response => {
            this.py_loading = false;
            this.projectYear = response;
            // now let's get all the related data
          })
    },
    getProject(projectId) {
      this.project_loading = true;
      let endpoint = `/api/project-planning/projects/${projectId}/`;
      apiService(endpoint)
          .then(response => {
            this.project_loading = false;
            this.project = response;
          })
    },


    // File
    getFiles() {
      this.file_loading = true;
      let endpoint = `/api/project-planning/project-years/${projectYearId}/files/?status_report=${statusReportId}`;
      apiService(endpoint)
          .then(response => {
            this.file_loading = false;
            this.files = response;
          })
    },
    deleteFile(file) {
      userInput = confirm(deleteMsg + file.name)
      if (userInput) {
        let endpoint = `/api/project-planning/files/${file.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              if (!response.detail) this.$delete(this.files, this.files.indexOf(file));
            })
      }
    },

    openFileModal(file) {
      if (!file) {
        this.showNewFileModal = true;
      } else {
        this.fileToEdit = file;
        this.showOldFileModal = true;
      }
    },


    // update
    getUpdates() {
      this.update_loading = true;
      let endpoint = `/api/project-planning/status-reports/${statusReportId}/updates/`;
      apiService(endpoint)
          .then(response => {
            this.update_loading = false;
            this.updates = response;
          })
    },

    openUpdateModal(update) {
      if (!update) {
        this.showNewUpdateModal = true;
      } else {
        this.updateToEdit = update;
        this.showOldUpdateModal = true;
      }
    },

    closeModals() {
      this.showNewFileModal = false;
      this.showOldFileModal = false;

      this.showNewUpdateModal = false;
      this.showOldUpdateModal = false;

      this.$nextTick(() => {
        this.getFiles()
        this.getUpdates()
        this.getCurrentUser()
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
  computed: {},
  created() {
    this.getCurrentUser()
    this.getFiles()
    this.getUpdates()
  },
  mounted() {
  },
});

