<template>
  <div class="text-center">

    <v-btn @click="openOverlay" v-if="!note.id">
      <v-icon>mdi-plus</v-icon>
    </v-btn>
    <v-btn small @click="openOverlay" v-else>
      <v-icon small>mdi-pencil</v-icon>
    </v-btn>

    <v-overlay :value="overlay" light opacity=".7">


      <form @submit.prevent="onSubmit">
        <v-card
            dark
            elevation="2"
        >

          <v-card-title>
            <h4 v-if="!note.id"> Add Note </h4>
            <h4 v-else> Edit Note </h4>

          </v-card-title>

          <v-card-text>


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
          </v-card-text>
          <v-card-actions>
            <v-btn type="submit" color="success">
              <span v-if="note.id">Update</span>
              <span v-else>Create</span>
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
    event_id: {
      required: false
    },
    note: {
      required: false,
      default: function () {
        return {}
      }
    },
  },
  data() {
    return {
      overlay: false,
      labels: {},
      typeChoices: [],
      error: null
    };
  }
  ,
  methods: {
    openOverlay() {
      this.overlay = true;
      if (!this.note.id) {
        this.primeNote()
      }
    }
    ,
    primeNote() {
      this.note = {
        type: null,
        note: null,
        is_complete: false,
        event: this.event_id
      };
    }
    ,
    getNoteMetadata() {
      let endpoint = `/api/events-planner/meta/models/note/`;
      apiService(endpoint).then(data => {
        this.labels = data.labels;
        this.typeChoices = data.type_choices;
      });
    }
    ,
    onSubmit() {
      this.error = null;
      var method;
      var endpoint;
      if (this.note.id) {
        endpoint = `/api/events-planner/notes/${this.note.id}/`;
        method = "PUT";
      } else {
        endpoint = "/api/events-planner/notes/";
        method = "POST";
      }
      apiService(endpoint, method, this.note).then(response => {
        if (response.id) {
          this.$emit("update-notes");
          if (!this.note.id) this.primeNote();
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
    this.getNoteMetadata();
  },
  computed: {}
};
</script>
