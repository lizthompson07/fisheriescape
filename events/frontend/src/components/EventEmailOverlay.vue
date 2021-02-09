<template>
  <div>
    <v-btn small @click="openOverlay" title="Edit Invitation Email">
      <v-icon small>mdi-email</v-icon>
    </v-btn>
    <div class="text-center">

      <v-overlay :value="overlay" light opacity=".7">
        <form @submit.prevent="onSubmit" style="width: 750px">

          <v-card
              dark
              elevation="2"
          >
            <v-card-title>
              <h4> Event Invitation Email</h4>

            </v-card-title>

            <v-card-text>
              <v-simple-table dense light>
                 <template v-slot:default>
                <tr>
                  <th>FROM</th>
                  <td v-html="email.from"></td>
                </tr>
                <tr>
                  <th>TO</th>
                  <td v-html="email.to"></td>
                </tr>
                <tr>
                  <th>Subject</th>
                  <td v-html="email.subject"></td>
                </tr>
                <tr>
                  <th>Message</th>
                  <td v-html="email.message"></td>
                </tr>
                 </template>
              </v-simple-table>

            </v-card-text>

            <v-card-actions>
              <v-btn type="submit" color="success">
                <span>Update</span>
              </v-btn>

              <v-btn color="normal" class="mx-1" @click="overlay = false">
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
  </div>
</template>


<script>
import {apiService} from "@/common/api_service";

export default {
  name: "EventEmailOverlay",
  props: {
    invitee: {
      required: true
    }
  },
  data() {
    return {
      overlay: false,
      error: null,
      email: {}
    };
  },
  methods: {
    openOverlay() {

      this.error = null;
      this.overlay = true;
      this.getEmailPreview()
    },
    getEmailPreview() {
      let endpoint = `/api/events-planner/invitees/${this.invitee.id}/invitation/`;
      apiService(endpoint, "GET").then(data => {
        this.email = data
      });
    },
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      endpoint = `/api/events-planner/invitees/${this.invitee.id}/`;
      method = "PATCH";
      apiService(endpoint, method, {dates: this.dates}).then(response => {
        if (response.id) {
          this.$emit("update-invitees");
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
  computed: {}
};
</script>
