<template>
  <div class="home">
    <v-container class="mt-2">
      <v-breadcrumbs
          :items="crumbs"
          divider=">"
      ></v-breadcrumbs>
      <div class="mt-2 mb-5">
        <div class="text-h3 text-muted mt-2 mb-2">
          Welcome to the DM Apps Event Planner
        </div>
      </div>
      <v-row>
        <v-col v-if="!loadingEvents">
          <v-card>
            <v-card-title>
              <v-text-field
                  v-model="search"
                  append-icon="mdi-magnify"
                  label="Search Events"
                  single-line
                  hide-details
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn
                  small
                  color="primary"
                  :to="{ name: 'event-new' }"
                  v-html="$t('New Event')"
              ></v-btn
              >
            </v-card-title>
            <v-data-table :headers="headers" :items="events" :search="search">
              <template v-slot:item.tname="{ item }">
                <router-link :to="{ name: 'event-detail', params: { id: item.id } }"
                >{{ item.tname }}
                </router-link>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
        <v-col v-else>
          <v-progress-circular
              indeterminate
              color="primary"
          ></v-progress-circular>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import {apiService} from "@/common/api_service";

export default {
  name: "home",
  data() {
    return {
      crumbs: [
        {
          text: "Home",
          disabled: true,
        },
      ],
      loadingEvents: true,
      events: [],
      tags: [],
      next: null,
      loadingRecipes: false,
      current_user: null,
      search: "",
      search_tag: "",
      headers: [
        {
          text: "Name",
          align: "start",
          value: "tname"
        },
        // {text: 'Author', value: 'author'},
        {text: "Type", value: "type_display"},
        {text: "Start date", value: "start_date_display"},
        {text: "Date created", value: "created_at_display"}
        // {text: "Tags", value: "hashtags_string"}
      ]

    };
  },
  methods: {
    getUserData() {
      let endpoint = `/api/user/`;
      apiService(endpoint).then(data => {
        this.current_user = data.username;
      });
    },
    getEvents() {
      let endpoint = "/api/events-planner/events/";
      if (this.next) {
        endpoint = this.next;
      }
      this.loadingEvents = true;
      apiService(endpoint).then(response => {
        this.events.push(...response.results);
        if (response.next) {
          this.next = response.next;
        } else {
          this.next = null;
        }
      });
      this.loadingEvents = false;
    },
    // getTags() {
    //   let endpoint = "api/hashtags/";
    //   apiService(endpoint).then(data => {
    //     this.tags = data.results;
    //   });
    // }
  },

  created() {
    this.getEvents();
    // this.getUserData();
    // this.getTags();
    document.title = this.$t("Event Planner");
  }
};
</script>

<style>
.author-name {
  font-weight: bold;
  color: #dc3545;
}

.recipe-link {
  font-weight: bold;
  color: black;
}

.recipe-link:hover {
  color: #343a40;
  text-decoration: none;
}
</style>
