<template>

  <div class="text-center">
    <v-dialog
        v-model="dialog"
        width="1000"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn small title="Edit Invitation Email" v-bind="attrs" v-on="on" @click="openDialog">
          <v-icon small>mdi-email</v-icon>
        </v-btn>
      </template>

      <v-card>
        <v-card-title class="headline grey lighten-2">
          <h4> Event Invitation Email</h4>
        </v-card-title>

        <v-card-text>
          <p><u class="font-weight-bold">FROM:</u><br><span v-html="email.from"></span></p>
          <p><u class="font-weight-bold">TO:</u><br><span v-html="email.to"></span></p>
          <p><u class="font-weight-bold">SUBJECT:</u><br><span v-html="email.subject"></span></p>
          <p><u class="font-weight-bold">MESSAGE:</u><br><span v-html="email.message"></span></p>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
              color="secondary"
              text
              @click="dialog = false"
          >
            Back
          </v-btn>
          <v-btn
              color="primary"
              text
              @click="sendInvitation"
          >
            Send Invitation
          </v-btn>
        </v-card-actions>
      </v-card>
      <div class="mt-3">
        <v-alert type="error" v-if="error">
          {{ error }}
        </v-alert>
      </div>
    </v-dialog>
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
      dialog: false,
      error: null,
      email: {}
    };
  },
  methods: {
    openDialog() {
      this.error = null;
      this.getEmailPreview();
    },
    getEmailPreview() {
      let endpoint = `/api/events-planner/invitees/${this.invitee.id}/invitation/`;
      apiService(endpoint, "GET").then(data => {
        this.email = data
      });
    },
    sendInvitation() {
      this.error = null;
      var method;
      var endpoint;
      endpoint = `/api/events-planner/invitees/${this.invitee.id}/invitation/`;
      method = "POST";
      apiService(endpoint, method).then(() => {
        this.$emit("update-invitees");
        this.dialog = false;
      });
    }
  },
  computed: {},
  watch: {
    overlay() {
      this.$nextTick(() => {
        this.$refs.myoverlay.showScroll();
      });
    }
  }


};
</script>
