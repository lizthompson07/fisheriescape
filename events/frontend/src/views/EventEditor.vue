<template>
  <div class="container mt-2">
    <h1 v-if="id" class="mb-3">Edit Event</h1>
    <h1 v-else class="mb-3">Create Event</h1>

    <form @submit.prevent="onSubmit">
      <v-text-field v-model="eventToEdit.name" :label="labels.name" required color="red"></v-text-field>
      <v-text-field v-model="eventToEdit.nom" :label="labels.nom"></v-text-field>
      <v-select v-model="eventToEdit.type" :items="typeChoices" :label="labels.type" required></v-select>
      <v-text-field v-model="eventToEdit.location" :label="labels.location"></v-text-field>
      <v-text-field v-model="eventToEdit.proponent" :label="labels.proponent"></v-text-field>
      <v-select v-model="eventToEdit.parent_event" :items="parentChoices" :label="labels.parent_event"></v-select>
<!--      <v-text-field v-model="eventToEdit.from_email" :label="labels.from_email" required></v-text-field>-->
      <v-text-field v-model="eventToEdit.rsvp_email" :label="labels.rsvp_email" required></v-text-field>

      <div class="row">
        <div class="col">
          <v-date-picker
              label="dates"
              v-model="eventToEdit.dates"
              range
          ></v-date-picker>
        </div>
      </div>
      <v-btn type="submit" color="success">
        <span v-if="id">Update</span>
        <span v-else>Create</span>
      </v-btn>

      <!--      <DeleteRecipeDialogBox-->
      <!--          v-if="event"-->
      <!--          @delete-confirmation="deleteRecipe"-->
      <!--      ></DeleteRecipeDialogBox>-->
      <v-btn
          v-if="id"
          color="normal"
          class="mx-1"
          :to="{ name: 'event-detail', params: { id: id } }"
      >
        Back
      </v-btn>
      <v-btn v-else color="normal" class="mx-1" :to="{ name: 'home' }">
        Back
      </v-btn>

      <div class="mt-3">
        <v-alert type="error" v-if="error">
          {{ error }}
        </v-alert>
      </div>
    </form>
  </div>
</template>

<script>
import {apiService} from "@/common/api_service";

export default {
  name: "EventEditor",
  props: {
    parent_id: {
      required: false
    },
    id: {
      required: false
    },
  },
  data() {
    return {
      currentUser: {},
      event: {},
      eventToEdit: {},
      error: null,
      labels: {},
      typeChoices: [],
      parentChoices: []
    };
  },
  methods: {
    getCurrentUser(delayedFunc) {
      let endpoint = `/api/shared/current-user/`;
      apiService(endpoint).then(response => {
        this.currentUser = response;
        if (delayedFunc) delayedFunc();
      });
    },
    primeEvent() {
      this.eventToEdit = {
        name: null,
        nom: null,
        location: null,
        proponent: null,
        type: null,
        dates: [],
        parent_event: this.parent_id, // will either be null or it will already contain the correct value!
        rsvp_email: this.currentUser.email
      };
    },
    getEventMetadata() {
      let endpoint = `/api/events-planner/meta/models/event/`;
      apiService(endpoint).then(data => {
        this.labels = data.labels;
        this.typeChoices = data.type_choices;
        this.parentChoices = data.event_choices;
      });
    },
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      if (this.id) {
        endpoint = `/api/events-planner/events/${this.id}/`;
        method = "PUT";
      } else {
        endpoint = "/api/events-planner/events/";
        method = "POST";
      }
      var data = this.eventToEdit;
      if (this.eventToEdit.dates.length) {
        let dates = [...this.eventToEdit.dates];
        data.start_date = dates.sort()[0] + " 00:00:00";
        if (dates.length === 2) {
          data.end_date = dates.sort()[1] + " 00:00:00";
        } else {
          data.end_date = null;
        }
      }
      apiService(endpoint, method, data).then(response => {
        if (response.id) {
          this.$router.push({
            name: "event-detail",
            params: {id: response.id}
          });
        } else {
          this.error = JSON.stringify(response)
              .replace("{", "")
              .replace("}", "")
              .replace("[", "")
              .replace("]", "");
        }
      });
    },
    getEvent() {
      var id;
      if (this.parent_id) id = this.parent_id;
      else id = this.id;
      let endpoint = `/api/events-planner/events/${id}/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.event = data;
          if (this.id) {
            this.eventToEdit = JSON.parse(JSON.stringify(this.event)); // deep copy;
          } else if (this.parent_id) {
            this.primeEvent();
          }
        } else {
          document.title = this.message404;
        }
      });
    }
  },
  created() {
    this.getCurrentUser();
    this.getEventMetadata();
    if (this.id) {
      document.title = "Edit Event";
      this.getEvent();
    } else if (this.parent_id) {
      this.getEvent();
      document.title = "New Child Event";
    } else {
      document.title = "New Event";
      this.getCurrentUser(this.primeEvent);


    }
  },
  computed: {}
};
</script>

<style>
.alert {
  width: 500px;
}
</style>
