<template>
  <div class="text-center">

    <v-btn @click="openOverlay" v-if="!invitee.id">
      <v-icon>mdi-plus</v-icon>
    </v-btn>
    <v-btn small @click="openOverlay" v-else>
      <v-icon small>mdi-pencil</v-icon>
    </v-btn>

    <v-overlay :value="overlay" light opacity=".7">
      <form @submit.prevent="onSubmit">

        <v-autocomplete
            v-model="invitee.person"
            :items="personOptions"
            :loading="loadingPersons"
            :search-input.sync="search"
            hide-no-data
            item-text="name"
            item-value="id"
            :label="labels.person"
            placeholder="Start typing to Search"
            clearable
            return-object
        ></v-autocomplete>


        <v-select v-model="invitee.role" :items="roleChoices" :label="labels.role" required></v-select>
        <v-select v-model="invitee.status" :items="statusChoices" :label="labels.status" required></v-select>
        <v-text-field v-model="invitee.organization" :label="labels.organization"></v-text-field>

        <v-btn type="submit" color="success">
          <span v-if="invitee.id">{{ $t("Update") }}</span>
          <span v-else>{{ $t("Add") }}</span>
        </v-btn>

        <v-btn color="normal" class="mx-1" @click="overlay = false">
          Back
        </v-btn>

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
  name: "NoteEditorOverlay",
  props: {
    event_id: {
      required: false
    },
    invitee: {
      required: false,
      default: function () {
        return {};
      }
    }
  },
  data() {
    return {
      overlay: false,
      labels: {},
      statusChoices: [],
      roleChoices: [],
      error: null,
      personOptions: [],
      loadingPersons: true
    };
  },
  methods: {
    openOverlay() {
      this.overlay = true;
      if (!this.invitee.id) {
        this.primeInvitee();
      }
    },
    primeInvitee() {
      this.invitee = {
        type: null,
        note: null,
        is_complete: false,
        event: this.event_id
      };
    },
    getInviteeMetadata() {
      let endpoint = `/api/events-planner/meta/models/invitee/`;
      apiService(endpoint).then(data => {
        this.labels = data.labels;
        this.roleChoices = data.role_choices;
        this.statusChoices = data.status_choices;
      });
    },
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      if (this.invitee.id) {
        endpoint = `/api/events-planner/invitees/${this.invitee.id}/`;
        method = "PUT";
      } else {
        endpoint = "/api/events-planner/invitees/";
        method = "POST";
      }
      apiService(endpoint, method, this.invitee).then(response => {
        if (response.id) {
          this.$emit("update-invitees");
          if (!this.note.id) this.primeInvitee();
          this.overlay = false;
        } else {
          this.error = JSON.stringify(response)
              .replace("{", "")
              .replace("}", "")
              .replace("[", "")
              .replace("]", "");
        }
      });
    },
    makePersonSearch: async (value, self) => {
      // Handle empty value
      if (!value) {
        self.personOptions = [];
        self.person = '';
      }
      // Items have already been requested
      if (self.loadingPerson) {
        return
      }

      self.loadingPerson = true

      // YOUR AJAX Methods go here
      // if you prefer not to use vue-api-query
      await Person
          .where('name', value)
          .get()
          .then(response => {
            self.personOptions = response.data
          }).catch(error => {
            self.error = 'Unknown Error. Please check details and try again.'
            self.failed()
          })
          .finally(() => (self.loadingLearner = false))
    }
  },
  watch: {
    search(value) {
      if (!value) {
        return
      }
      // Debounce the input and wait for a pause of at
      // least 200 milliseconds. This can be changed to
      // suit your needs.
      debounce(this.makeSearch, 200)(value, this)
    }
  },
  created() {
    this.getInviteeMetadata();
  },
  computed: {}
};
</script>
