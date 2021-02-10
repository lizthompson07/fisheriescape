<template>
  <div class="text-center">

    <v-btn @click="openOverlay" v-if="!invitee.id">
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
            <h4 v-if="!invitee.id"> Add Invitee </h4>
            <h4 v-else> Edit Invitee </h4>

          </v-card-title>

          <v-card-text>

            <v-autocomplete
                v-if="!invitee.id"
                @change="updateInvitee"
                v-model="user"
                :items="personOptions"
                :loading="loadingPersons"
                :search-input.sync="search"
                item-text="full_name"
                label="Quick Search for DM Apps User"
                placeholder="Start typing to Search"
                clearable
                filled
                return-object
            ></v-autocomplete>


            <v-text-field v-model="inviteeToEdit.first_name" :label="labels.first_name"></v-text-field>
            <v-text-field v-model="inviteeToEdit.last_name" :label="labels.last_name"></v-text-field>
            <v-text-field v-model="inviteeToEdit.phone" :label="labels.phone" ref="phone"></v-text-field>
            <v-text-field v-model="inviteeToEdit.email" :label="labels.email"></v-text-field>


            <v-select v-model="inviteeToEdit.role" :items="roleChoices" :label="labels.role" required></v-select>
            <v-select v-model="inviteeToEdit.status" :items="statusChoices" :label="labels.status" required></v-select>
            <v-text-field v-model="inviteeToEdit.organization" :label="labels.organization"></v-text-field>

          </v-card-text>

          <v-card-actions>
            <v-btn type="submit" color="success">
              <span v-if="invitee.id">Update</span>
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
  name: "InviteeEditorOverlay",
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
      search: null,
      user: null,
      dates: null
    };
  },
  methods: {
    openOverlay() {
      this.error = null;
      this.overlay = true;
      if (!this.invitee.id) {
        this.primeInvitee();
      } else {
        this.inviteeToEdit = JSON.parse(JSON.stringify(this.invitee)); // deep copy
;
      }
    },
    closeOverlay() {
      this.error = null;
      if (this.invitee.id) {
        this.primeInvitee();
        this.inviteeToEdit = this.invitee;
      }
      this.overlay = false;
    },
    primeInvitee() {
      this.inviteeToEdit = {
        first_name: null,
        last_name: null,
        phone: null,
        email: "@dfo-mpo.gc.ca",
        status: 0,
        role: 1,
        organization: null,
        event: this.event_id
      };
    },
    updateInvitee() {
      if (this.user) {
        this.inviteeToEdit.first_name = this.user.first_name;
        this.inviteeToEdit.last_name = this.user.last_name;
        this.inviteeToEdit.email = this.user.email;
        this.inviteeToEdit.organization = "DFO-MPO";
        this.search = null;
        console.log(this.$refs.phone.focus());
      }
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
    }
  },
  watch: {
    search(value) {
      // Items have not already been requested
      if (!this.loadingPersons) {
        // Handle empty value
        if (!value || value === "") {
          this.personOptions = [];
          this.user = "";
        } else {
          this.loadingPersons = true;

          let endpoint = `/api/shared/users/?search=${value}`;
          apiService(endpoint).then(data => {
            this.personOptions = data.results;
            this.loadingPersons = false;
          });
        }
      }
    }
  },
  created() {
    this.getInviteeMetadata();
  },
  computed: {}
};
</script>
