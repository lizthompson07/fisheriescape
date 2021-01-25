var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    citations_loading: false,
    newPublication: false,
    project_citations_loading: false,
    publications: [],
    citations: [],
    project_citations: [],
    hasSearched: null,
    searchTerm: null,
    editMode: false,
    citationToEdit: {
      name: null,
      nom: null,
      authors: null,
      year: null,
      new_publication: null,
      publication: null,
      pub_number: null,
      url_en: null,
      url_fr: null,
      abstract_en: null,
      abstract_fr: null,
      series: null,
      region: null,
    },
  },
  methods: {
    getProjectCitations() {
      this.project_citations_loading = true;
      let endpoint = `/api/project-planning/citations/?project=${projectId}`;
      apiService(endpoint)
          .then(response => {
            this.project_citations_loading = false;
            this.project_citations = response;
          })
    },
    getPublications() {
      this.citations_loading = true;
      let endpoint = `/api/project-planning/publications/`;
      apiService(endpoint)
          .then(response => {
            this.citations_loading = false;
            this.publications = response;
          })
    },
    getCitations() {
      this.hasSearched = true;
      this.citations_loading = true;
      let endpoint = `/api/project-planning/citations/?search=${this.searchTerm}`;
      apiService(endpoint)
          .then(response => {
            this.citations_loading = false;
            if (response.length) {
              for (var i = 0; i < response.length; i++) {
                c = response[i]
                if (!this.project_citation_ids.includes(c.id)) {
                  this.citations.push(c)
                }
              }
            } else {
              this.citations = []
            }
          })
    },
    addCitation(citation) {
      let endpoint = `/api/project-planning/projects/${projectId}/reference/add/`;
      apiService(endpoint, "POST", {citation: citation.id})
          .then(response => {
            this.getProjectCitations()
          })
    },
    removeCitation(citation) {
      this.searchTerm = null
      let endpoint = `/api/project-planning/projects/${projectId}/reference/remove/`;
      apiService(endpoint, "POST", {citation: citation.id})
          .then(response => {
            this.getProjectCitations()
          })
    },
    deleteCitation(citation) {
      msg = "Are you sure you want to DELETE this citation? \n\nIt will be removed from the dmapps database, not just your project."
      userInput = confirm(msg)
      if (userInput) {
        this.searchTerm = null
        let endpoint = `/api/project-planning/citations/${citation.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              this.getProjectCitations()
            })
      }
    },
    submitSearch() {
      if (this.searchTerm.length > 4) {
        this.getCitations()
      } else {
        this.citations = [];
      }
    },
    editCitation(citation) {
      this.editMode = true;
      this.newPublication = false;
      if (citation) {
        this.citationToEdit = citation;
      } else {
        this.citationToEdit = {
          name: null,
          nom: null,
          authors: null,
          year: null,
          publication: null,
          pub_number: null,
          url_en: null,
          url_fr: null,
          abstract_en: null,
          abstract_fr: null,
          series: null,
          region: null,
        }
      }
      this.$nextTick(() => {
        this.$refs.edit_home.focus()
      })
    },
    cancelEditCitation() {
      this.editMode = false;
      this.citationToEdit = {};
      this.newPublication = false;
    },
    toggleNewPublication() {
      this.newPublication = !this.newPublication;
    },
    submitCitationForm() {
      if (this.citationToEdit.id) {
        let endpoint = `/api/project-planning/citations/${this.citationToEdit.id}/`;
        apiService(endpoint, "PUT", this.citationToEdit)
            .then(response => {
              this.getProjectCitations()
              if (this.citationToEdit.new_publication) {
                this.publications.push({id: response.publication, name: this.citationToEdit.new_publication})
              }
            })

      } else {
        let endpoint = `/api/project-planning/citations/?project=${projectId}`;
        apiService(endpoint, "POST", this.citationToEdit)
            .then(response => {
              this.getProjectCitations()
              this.searchTerm = null
              this.citations = []
              if (this.citationToEdit.new_publication) {
                this.publications.push({id: response.publication, name: this.citationToEdit.new_publication})
              }
            })
      }
      this.editMode = false;
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
    project_citation_ids() {
      myArray = []
      for (var i = 0; i < this.project_citations.length; i++) {
        myArray.push(this.project_citations[i].id)
      }
      return myArray
    }
  },
  created() {
    this.getProjectCitations()
    this.getPublications()
  },
  mounted() {
  },
});

