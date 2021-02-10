<template>

  <v-menu
      ref="menu"
      v-model="menu"
      :close-on-content-click="false"
      :return-value.sync="dates"
      transition="scale-transition"
      offset-y
      min-width="auto"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-combobox
          v-model="dates"
          multiple
          chips
          small-chips
          label=""
          prepend-icon="mdi-calendar"
          readonly
          v-bind="attrs"
          v-on="on"
      ></v-combobox>
    </template>
    <v-date-picker
        v-model="dates"
        :min="invitee.min_date"
        :max="invitee.max_date"
        multiple
        no-title
        scrollable
        @change="onSubmit"
    >
      <v-spacer></v-spacer>
      <v-btn
          text
          color="primary"
          @click="menu = false"
      >
        Cancel
      </v-btn>
      <v-btn
          text
          color="primary"
          @click="$refs.menu.save(dates)"
      >
        OK
      </v-btn>
    </v-date-picker>
  </v-menu>


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
      dates: this.invitee.attendance,
      menu: null
    };
  },
  methods: {
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
