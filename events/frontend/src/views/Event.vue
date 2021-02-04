<template>
  <div class="mt-3">
    <div class="container" v-if="event">
      <div class="row">
        <div class="col-8">
          <div class="float-right">
            <v-btn :to="{ name: 'event-edit', params: { id: event.id } }">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <DeleteEventDialogBox
                v-if="id"
                @delete-confirmation="deleteEvent"
            ></DeleteEventDialogBox>

          </div>
          <h1>Event Detail</h1>
          <v-simple-table dense>
            <template v-slot:default>
              <tbody>
              <DetailRow :label="eventLabels.name" :value="event.name"></DetailRow>
              <DetailRow :label="eventLabels.nom" :value="event.nom"></DetailRow>
              <DetailRow :label="eventLabels.type" :value="event.type_display"></DetailRow>
              <DetailRow :label="eventLabels.location" :value="event.location"></DetailRow>
              <DetailRow :label="eventLabels.proponent" :value="event.proponent"></DetailRow>
              <DetailRow label="Start / End Date" :value="event.display_dates"></DetailRow>
              <DetailRow label="Metadata" :value="event.metadata"></DetailRow>
              </tbody>
            </template>

          </v-simple-table>

          <div class="mt-3">
            <div class="float-right">
              <InviteeEditorOverlay
                  v-if="event.id"
                  :event_id="event.id"
                  @update-invitees="updateInvitees"
              ></InviteeEditorOverlay>
            </div>
            <h1>Invitees</h1>
            <!--          <div v-for="(note, index) in notes" :key="index" class="py-1">-->
            <!--            <NoteCard :note="note" @update-notes="updateNotes"></NoteCard>-->
            <!--          </div>-->

          </div>


          <div class="mt-3">
            <h1>Resources</h1>
          </div>


          <div class="mt-3">
            <h1>Children</h1>
          </div>

        </div>
        <div class="col">
          <div class="float-right">
            <NoteEditorOverlay
                v-if="event.id"
                :event_id="event.id"
                @update-notes="updateNotes"
            ></NoteEditorOverlay>
          </div>
          <h1>Notes</h1>
          <div v-for="(note, index) in notes" :key="index" class="py-1">
            <NoteCard :note="note" @update-notes="updateNotes"></NoteCard>
          </div>
        </div>
      </div>
    </div>

    <div class="not-found" v-else>
      <h1>{{ message404 }}</h1>
    </div>
  </div>
</template>

<script>
import {apiService} from "@/common/api_service";
import DeleteEventDialogBox from "@/components/DeleteEventDialogBox.vue";
import NoteEditorOverlay from "@/components/NoteEditorOverlay";
import InviteeEditorOverlay from "@/components/InviteeEditorOverlay";
import DetailRow from "@/components/DetailRow";
import NoteCard from "@/components/NoteCard";

export default {
  name: "Recipe",
  props: {
    id: {
      required: true
    }
  },
  data() {
    return {
      event: {},
      notes: [],
      invitees: [],
      message404: "404 - Page Not Found",
      eventLabels: {}
    };
  },
  components: {
    DeleteEventDialogBox,
    NoteEditorOverlay,
    InviteeEditorOverlay,
    DetailRow,
    NoteCard
  },
  methods: {
    getEventMetadata() {
      let endpoint = `/api/events-planner/meta/models/event/`;
      apiService(endpoint).then(data => {
        this.eventLabels = data.labels;
      });
    },
    updateNotes() {
      let endpoint = `/api/events-planner/notes/?event=${this.event.id}`;
      apiService(endpoint).then(data => {
        this.notes = data.results;
      });
    },
    updateInvitees() {
      let endpoint = `/api/events-planner/invitees/?event=${this.event.id}`;
      apiService(endpoint).then(data => {
        this.notes = data.results;
      });
    },
    getEvent() {
      let endpoint = `/api/events-planner/events/${this.id}/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.event = data;
          this.notes = this.updateNotes();
          this.invitees = this.updateInvitees();
          document.title = data.tname;
        } else {
          this.event = null;
          document.title = this.message404;
        }
      });
    },
    async deleteEvent() {
      let endpoint = `/api/events-planner/events/${this.id}/`;
      await apiService(endpoint, "DELETE");
      this.$router.push({name: "home"});
    }

  },
  computed: {
    // isCurrentUsersRecipe() {
    //   return this.current_user === this.recipe.author;
    // }
  },
  created() {
    this.getEventMetadata();
    this.getEvent();
  },
};
</script>

<style>
.user-has-commented {
  font-weight: bold;
  font-size: 110%;
  color: green;
}

.error {
  font-weight: bold;
  font-size: 110%;
  color: red;
}
</style>
