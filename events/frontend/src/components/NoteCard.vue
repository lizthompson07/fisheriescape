<template>
  <v-card
      elevation="2"
  >
    <v-card-title>
      {{ note.type_display }}:
    </v-card-title>
    <v-card-text>
      {{ note.note }}
    </v-card-text>

    <v-card-actions>
      <v-checkbox
          v-model="note.is_complete"
          :label="labels.is_complete"
      ></v-checkbox>
    </v-card-actions>

  </v-card>
</template>

<script>
import {apiService} from "@/common/api_service";

export default {
  name: "NoteCard",
  props: {
    note: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      labels: {},

    };
  },
  computed: {},
  methods: {
    getNoteMetadata() {
      let endpoint = `/api/events-planner/meta/models/note/`;
      apiService(endpoint).then(data => {
        this.labels = data.labels;
      });
    },
  },
  created() {
    this.getNoteMetadata()
  }
};
</script>

