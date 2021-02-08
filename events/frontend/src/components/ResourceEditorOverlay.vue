<template>
  <div class="text-center">

    <v-btn @click="openOverlay" v-if="!resource.id">
      <v-icon>mdi-plus</v-icon>
    </v-btn>
    <v-btn small @click="openOverlay" v-else>
      <v-icon small>mdi-pencil</v-icon>
    </v-btn>

    <v-overlay :value="overlay" light opacity=".7">
      <form @submit.prevent="onSubmit" style="width: 750px">


        <v-card
            dark
            elevation="2"
        >
          <v-card-title>
            <h4 v-if="!resource.id"> Add Resource </h4>
            <h4 v-else> Edit Resource </h4>

          </v-card-title>

          <v-card-text>

            <v-text-field v-model="resourceToEdit.name" :label="labels.name"></v-text-field>
            <v-text-field v-model="resourceToEdit.nom" :label="labels.nom"></v-text-field>
            <v-text-field v-model="resourceToEdit.url_en" :label="labels.url_en"></v-text-field>
            <v-text-field v-model="resourceToEdit.url_fr" :label="labels.url_fr"></v-text-field>

          </v-card-text>

          <v-card-actions>
            <v-btn type="submit" color="success">
              <span v-if="resource.id">Update</span>
              <span v-else>Add</span>
            </v-btn>

            <v-btn color="normal" class="mx-1" @click="closeOverlay">
              Back
            </v-btn>
          </v-card-actions>

        </v-card>


        <div class="mt-3">
          <v-alert type="error" v-if="error">
            {{ error }}
          </v-alert>
        </div>
      </form>
    </v-overlay>
  </div>
</template>


<script>
import {apiService} from "@/common/api_service";

export default {
  name: "ResourceEditorOverlay",
  props: {
    event_id: {
      required: false
    },
    resource: {
      required: false,
      default: function () {
        return {};
      }
    }
  },
  data() {
    return {
      overlay: false,
      resourceToEdit: {},
      labels: {},
      error: null
    };
  },
  methods: {
    openOverlay() {
      this.error = null;
      this.overlay = true;
      if (!this.resource.id) {
        this.primeResource();
      } else {
        this.resourceToEdit = JSON.parse(JSON.stringify(this.resource)); // deep copy;
      }
    },
    closeOverlay() {
      this.error = null;
      if (this.resource.id) {
        this.primeResource();
        this.resourceToEdit = this.resource;
      }
      this.overlay = false;
    },
    primeResource() {
      this.resourceToEdit = {
        name: null,
        nom: null,
        url_en: null,
        url_fr: null,
        event: this.event_id
      };
    },
    getResourceMetadata() {
      let endpoint = `/api/events-planner/meta/models/resource/`;
      apiService(endpoint).then(data => {
        this.labels = data.labels;
      });
    },
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      if (this.resource.id) {
        endpoint = `/api/events-planner/resources/${this.resource.id}/`;
        method = "PUT";
      } else {
        endpoint = "/api/events-planner/resources/";
        method = "POST";
      }
      apiService(endpoint, method, this.resourceToEdit).then(response => {
        if (response.id) {
          this.$emit("update-resources");
          if (!this.resourceToEdit.id) this.primeResource();
          this.overlay = false;
        } else {
          this.error = JSON.stringify(response)
              .replace("{", "")
              .replace("}", "")
              .replace("[", "")
              .replace("]", "");
        }
      });
    }
  },
  created() {
    this.getResourceMetadata();
  },
  computed: {}
};
</script>
