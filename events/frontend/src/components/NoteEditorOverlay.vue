<template>
  <div class="text-center">
    <v-btn
        @click="overlay = !overlay"
    >
      <v-icon>mdi-plus</v-icon>
    </v-btn>

    <v-overlay :value="overlay" light opacity=".7">
      <form @submit.prevent="onSubmit">
        <v-select v-model="note.type" :items="typeChoices" :label="labels.type" required></v-select>

        <v-textarea
            name="input-7-1"
            filled
            :label="labels.note"
            auto-grow
            v-model="note.note"
        ></v-textarea>

        <v-checkbox
            v-model="note.is_complete"
            :label="labels.is_complete"
        ></v-checkbox>

        <v-btn type="submit" color="success">
          <span v-if="id">{{ $t("Update") }}</span>
          <span v-else>{{ $t("Create") }}</span>
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
      required: true
    },
    id: {
      required: false
    }
  },
  data() {
    return {
      overlay: false,
      note: {},

      labels: {},
      typeChoices: [],
      error: null
    };
  },
  methods: {
    primeNote() {
      this.note = {
        type: null,
        note: null,
        is_complete: false,
        event: this.event_id
      };
    },

    getNoteMetadata() {
      let endpoint = `/api/events-planner/meta/models/note/`;
      apiService(endpoint).then(data => {
        this.labels = data.labels;
        this.typeChoices = data.type_choices;
      });
    },
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      if (this.id) {
        endpoint = `/api/events-planner/notes/${this.id}/`;
        method = "PUT";
      } else {
        endpoint = "/api/events-planner/notes/";
        method = "POST";
      }
      apiService(endpoint, method, this.note).then(response => {
        if (response.id) {
          this.$emit("update-notes");
          this.primeNote();
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

  },
  created() {
    this.primeNote();
    this.getNoteMetadata();
  },
  computed: {}
};
</script>
