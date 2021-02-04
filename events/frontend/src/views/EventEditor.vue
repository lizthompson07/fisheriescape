<template>
  <div class="container mt-2">
    <h1 v-if="id" class="mb-3">{{ $t("Edit Event") }}</h1>
    <h1 v-else class="mb-3">{{ $t("Create Event") }}</h1>

    <form @submit.prevent="onSubmit">
      <v-text-field v-model="name" label="Name (English)" required color="red"></v-text-field>
      <v-text-field v-model="nom" label="Name (French)"></v-text-field>
      <v-select v-model="type" :items="typeChoices" label="Event Type" required></v-select>
      <v-text-field v-model="location" label="Location"></v-text-field>
      <v-text-field v-model="proponent" label="Proponent"></v-text-field>
      <div class="row">
        <div class="col">
          <v-date-picker
              label="dates"
              v-model="dates"
              range
          ></v-date-picker>
        </div>
      </div>
      <v-btn type="submit" color="success">
        <span v-if="id">{{ $t("Update") }}</span>
        <span v-else>{{ $t("Create") }}</span>
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
    id: {
      // type: String,
      // required: true
    }
  },
  data() {
    return {
      name: null,
      nom: null,
      location: null,
      proponent: null,
      type: null,
      dates: [],

      error: null,
      typeChoices: [
        {text: "CSAS meeting", value: 1},
        {text: "Other", value: 9}
      ],

    };
  },
  methods: {
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      if (this.id) {
        endpoint = `/api/events/${this.id}/`;
        method = "PUT";
      } else {
        endpoint = "/api/events/";
        method = "POST";
      }
      apiService(endpoint, method, this.data).then(response => {
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
      let endpoint = `/api/events/${this.id}/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.name = data.name;
          this.nom = data.nom;
          this.location = data.location;
          this.proponent = data.proponent;
          this.type = data.type;
          this.dates = data.dates;

        } else {
          document.title = this.message404;
        }
      });
    }

  },
  created() {
    if (this.id) {
      document.title = "Edit Event";
      this.getEvent();
    } else {
      document.title = "New Event";

    }

  },
  computed: {
    data() {
      var data = {
        name: this.name,
        nom: this.nom,
        location: this.location,
        proponent: this.proponent,
        type: this.type
      };
      if (this.dates.length) {
        let dates = [...this.dates];

        data.start_date = dates.sort()[0] + " 00:00:00"
        if (this.dates.length === 2) {
          data.end_date = dates.sort()[1] + " 00:00:00"
        }
      }


      return data
    }
  },
};
</script>

<style>
.alert {
  width: 500px;
}
</style>
