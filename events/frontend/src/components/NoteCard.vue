<template>
  <v-card
      :color="fontColor"
      elevation="2"
  >
    <v-card-title>
      {{ note.type_display }}:
    </v-card-title>
    <v-card-text >
      {{ note.note }}
    </v-card-text>

    <v-card-actions>
      <v-btn x-small color="success" v-if="!note.is_complete" @click="toggleComplete">
        Done!
      </v-btn>
      <v-btn x-small color="warning" v-else @click="toggleComplete">
        Re-open
      </v-btn>

      <v-spacer></v-spacer>

      <NoteEditorOverlay
        :note="note"
      ></NoteEditorOverlay>
      <DeleteNoteDialogBox
          @delete-confirmation="deleteNote"
      ></DeleteNoteDialogBox>
    </v-card-actions>

  </v-card>
</template>

<script>
import {apiService} from "@/common/api_service";
import DeleteNoteDialogBox from "@/components/DeleteNoteDialogBox";
import NoteEditorOverlay from "@/components/NoteEditorOverlay";

export default {
  name: "NoteCard",
  props: {
    note: {
      type: Object,
      required: true
    }
  },
  components: {
    NoteEditorOverlay,
    DeleteNoteDialogBox,
  },
  data() {
    return {
      labels: {},

    };
  },
  computed: {
    fontColor(){
      var color = "#fffff1"
      if(this.note.is_complete) color = "#e4e5e4"
      else if(this.note.type === 1) color = "#d3ead3"
      else if(this.note.type === 2) color = "#cbd3f6"
      else if(this.note.type === 3) color = "#fdeed0"
      return color
    }

  },
  methods: {
    getNoteMetadata() {
      let endpoint = `/api/events-planner/meta/models/note/`;
      apiService(endpoint).then(data => {
        this.labels = data.labels;
      });
    },
    async deleteNote() {
      let endpoint = `/api/events-planner/notes/${this.note.id}/`;
      await apiService(endpoint, "DELETE");
      this.$emit("update-notes");
    },
    async toggleComplete() {
      let endpoint = `/api/events-planner/notes/${this.note.id}/`;
      await apiService(endpoint, "PATCH", {
        is_complete: !this.note.is_complete
      });
      this.$emit("update-notes");
    }
  },
  created() {
    this.getNoteMetadata()
  }
};
</script>

