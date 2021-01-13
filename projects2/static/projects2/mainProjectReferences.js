var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    citations_loading: false,
    project_citations_loading: false,
    citations: [],
    project_citations: [],
    hasSearched: null,
    searchTerm: null,
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
                console.log(c)
                if(!this.project_citation_ids.includes(c.id)) {
                    this.citations.push(c)
                  console.log(123)
                }
              }

            } else {
              this.citations = []
            }
          })
    },
    addCitation(citation){
      let endpoint = `/api/project-planning/projects/${projectId}/add-reference/`;
      apiService(endpoint, "POST", {citation: citation.id})
          .then(response => {
            this.getProjectCitations()
            this.$delete(this.citations, this.citations.indexOf(citation))
          })
    },
    submitSearch() {
      if (this.searchTerm.length > 4) {
        this.getCitations()
      } else {
        this.citations = [];
      }
    }

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
    project_citation_ids () {
      myArray = []
      for (var i = 0; i < this.project_citations.length; i++) {
        myArray.push(this.project_citations[i].id)
      }
      return myArray
    }
  },
  created() {
    this.getProjectCitations()
  },
  mounted() {
  },
});

