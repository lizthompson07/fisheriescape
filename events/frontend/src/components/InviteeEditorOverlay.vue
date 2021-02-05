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
            v-model="inviteeToEdit.person"
            :items="personOptions"
            :loading="loadingPersons"
            :search-input.sync="search"
            hide-no-data
            item-text="full_name_and_email"
            item-value="id"
            :label="labels.person"
            placeholder="Start typing to Search"
        ></v-autocomplete>
        {{invitee.person}}
        <v-select v-model="inviteeToEdit.role" :items="roleChoices" :label="labels.role" required></v-select>
        <v-select v-model="inviteeToEdit.status" :items="statusChoices" :label="labels.status" required></v-select>
        <v-text-field v-model="inviteeToEdit.organization" :label="labels.organization"></v-text-field>

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
import debounce from "debounce";

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
      inviteeToEdit: {},
      labels: {},
      statusChoices: [],
      roleChoices: [],
      error: null,
      personOptions: [],
      loadingPersons: false,
      search: ""
    };
  },
  methods: {
    openOverlay() {
      this.error = null;
      this.overlay = true;
      if (!this.invitee.id) {
        this.primeInvitee();
      } else {
        this.inviteeToEdit = this.invitee;
        this.search = this.invitee.person_object.full_name;
      }
    },
    primeInvitee() {
      this.inviteeToEdit = {
        person: null,
        status: 0,
        role: 1,
        organization: "DFO",
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
      apiService(endpoint, method, this.inviteeToEdit).then(response => {
        if (response.id) {
          this.$emit("update-invitees");
          if (!this.inviteeToEdit.id) this.primeInvitee();
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
    makePersonSearch: (value, self) => {
      console.log(value)
      // Items have not already been requested
      if (!self.loadingPersons) {

        // Handle empty value
        if (!value || value === "") {
          self.personOptions = [];
          self.invitee.person = "";
        } else {

          self.loadingPersons = true;

          // YOUR AJAX Methods go here
          let endpoint = `/api/events-planner/people/?search=${value}`;
          apiService(endpoint).then(data => {
            self.personOptions = data.results;
            self.loadingPersons = false;
          });
        }
      }

    }
  },
  watch: {
    search(value) {
      // Debounce the input and wait for a pause of at
      // least 200 milliseconds. This can be changed to
      // suit your needs.
      debounce(this.makePersonSearch, 200)(value, this)
    }
  },
  created() {
    this.getInviteeMetadata();
  },
  computed: {}
};
</script>
