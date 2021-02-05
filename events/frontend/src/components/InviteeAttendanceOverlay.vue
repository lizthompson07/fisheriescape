<template>
  <div class="text-center">

    <v-btn small @click="openOverlay">
      <v-icon small>mdi-calendar</v-icon>
    </v-btn>

    <v-overlay :value="overlay" light opacity=".7">
      <form @submit.prevent="onSubmit" style="width: 750px">


        <v-card
            dark
            elevation="2"
        >
          <v-card-title>
            <h4> Invitee Attendance </h4>

          </v-card-title>

          <v-card-text>
            <v-date-picker
                v-model="dates"
                multiple
                :min="invitee.min_date"
                :max="invitee.max_date"
                label="Dates in Attendance"
            ></v-date-picker>

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
</template>


<script>
import {apiService} from "@/common/api_service";

export default {
  name: "NoteEditorOverlay",
  props: {
    invitee: {
      required: true
    }
  },
  data() {
    return {
      overlay: false,
      error: null,
      dates: null
    };
  },
  methods: {
    openOverlay() {
      this.error = null;
      this.overlay = true;
      this.dates = this.invitee.attendance;
    },
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      endpoint = `/api/events-planner/invitees/${this.invitee.id}/`;
      method = "PATCH";
      apiService(endpoint, method, { dates: this.dates }).then(response => {
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
