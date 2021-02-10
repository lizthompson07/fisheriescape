<template>
  <div class="mt-3">
    <v-container v-if="event">
      <v-breadcrumbs
          :items="crumbs"
          divider=">"
      ></v-breadcrumbs>
      <v-row>
        <v-col cols="9">
          <div class="float-right">
            <v-btn v-if="id" :to="{ name: 'event-edit', params: { id: id } }">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <DeleteEventDialogBox
                v-if="id"
                @delete-confirmation="deleteEvent"
            ></DeleteEventDialogBox>

          </div>
          <div class="">
            <h1>Event Detail</h1>
            <v-simple-table dense>
              <template v-slot:default>
                <tbody>
                <DetailRow :label="eventLabels.name" :value="event.name"></DetailRow>
                <DetailRow :label="eventLabels.nom" :value="event.nom"></DetailRow>
                <DetailRow :label="eventLabels.type" :value="event.type_display"></DetailRow>
                <tr v-if="event.parent_event">
                  <th class="text-left" v-html="eventLabels.parent_event"></th>
                  <td class="text-left">
                    <router-link :to="{ name: 'event-detail', params: { id: event.parent_event_display.id } }">{{
                        event.parent_event_display.tname
                      }}
                    </router-link>
                  </td>
                </tr>
                <DetailRow :label="eventLabels.location" :value="event.location"></DetailRow>
                <DetailRow :label="eventLabels.proponent" :value="event.proponent"></DetailRow>
                <DetailRow label="Dates" :value="event.display_dates"></DetailRow>
                <DetailRow label="Attendees" :value="event.attendees"></DetailRow>
                <DetailRow label="Distinct attendees" :value="attendeeCount"></DetailRow>
                <DetailRow label="Metadata" :value="event.metadata"></DetailRow>
                </tbody>
              </template>

            </v-simple-table>
          </div>
          <br>
          <div class="mt-5">
            <table>
              <tr>
                <td class="pr-5 mr-3">
                  <h1>Invitees</h1>
                </td>
                <td>
                  <InviteeEditorOverlay
                      v-if="event.id"
                      :event_id="event.id"
                      @update-invitees="updateInvitees"
                  ></InviteeEditorOverlay>
                </td>
              </tr>
            </table>
            <p v-if="invitees && !invitees.length"><em>Nobody has been invited yet.</em></p>
            <v-simple-table v-else dense>
              <template v-slot:default>
                <thead>
                <tr>
                  <th class="text-left"> Name</th>
                  <th class="text-left"> Association</th>
                  <th class="text-left"> Function</th>
                  <th class="text-left"> Status</th>
                </tr>
                </thead>
                <tbody>

                <InviteeTableRow
                    v-for="(invitee, index) in invitees"
                    :key="index"
                    :invitee="invitee"
                    @update-invitees="getEvent(false)"
                ></InviteeTableRow>


                </tbody>
              </template>
            </v-simple-table>

          </div>

          <br>
          <div class="mt-5">
            <table>

              <tr>
                <td class="pr-5 mr-3">
                  <h1>Resources</h1>
                </td>
                <td>
                  <ResourceEditorOverlay
                      v-if="event.id"
                      :event_id="event.id"
                      @update-resources="updateResources"
                  ></ResourceEditorOverlay>
                </td>
              </tr>
            </table>
            <p v-if="resources && !resources.length"><em>No resources have been added yet.</em></p>
            <v-simple-table v-else dense>
              <template v-slot:default>
                <thead>
                <tr>
                  <th class="text-left"> Name</th>
                  <th class="text-left"> URLs</th>
                  <th class="text-left"> Date added</th>
                </tr>
                </thead>
                <tbody>

                <ResourceTableRow
                    v-for="(resource, index) in resources"
                    :key="index"
                    :resource="resource"
                    @update-resources="getEvent(false)"
                ></ResourceTableRow>


                </tbody>
              </template>
            </v-simple-table>

          </div>

          <br>
          <div class="mt-5">
            <table>

              <tr>
                <td class="pr-5 mr-3">
                  <h1>Children</h1>
                </td>
                <td>
                  <v-btn v-if="event.id" :to="{ name: 'event-new-child', params: {parent_id: event.id} }">
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </td>
              </tr>
            </table>
            <p v-if="event.children && !event.children.length"><em>This event has no children.</em></p>
            <v-simple-table v-else dense>
              <template v-slot:default>
                <thead>
                <tr>
                  <th class="text-left"> Name</th>
                  <th class="text-left"> Type</th>
                  <th class="text-left"> Dates</th>
                </tr>
                </thead>
                <tbody>

                <tr v-for="(child, index) in event.children" :key="index">
                  <td>
                    <router-link :to="{name: 'event-detail', params:{id: child.id}}">{{ child.tname }}</router-link>
                  </td>
                  <td> {{ child.type_display }}</td>
                  <td v-html="child.display_dates"></td>
                </tr>


                </tbody>
              </template>
            </v-simple-table>
            <br>
            <br>
            <br>
          </div>

        </v-col>
        <v-col>
          <table>
            <tr>
              <td class="pr-5">
                <h1>Notes</h1>
              </td>
              <td>
                <NoteEditorOverlay
                    v-if="event.id"
                    :event_id="event.id"
                    @update-notes="updateNotes"
                ></NoteEditorOverlay>
              </td>
            </tr>
          </table>
          <div v-for="(note, index) in notes" :key="index" class="py-1">
            <NoteCard :note="note" @update-notes="updateNotes"></NoteCard>
          </div>
        </v-col>
      </v-row>
    </v-container>

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
import InviteeTableRow from "@/components/InviteeTableRow";
import DetailRow from "@/components/DetailRow";
import NoteCard from "@/components/NoteCard";
import ResourceEditorOverlay from "@/components/ResourceEditorOverlay";
import ResourceTableRow from "@/components/ResourceTableRow";

export default {
  name: "Event",
  props: {
    id: {
      required: true
    }
  },
  data() {
    return {
      crumbs: [
        {
          text: "Home",
          disabled: false,
          href: this.$router.resolve({name: "home"}).href
        },
        {
          text: "Event Detail",
          disabled: true
        },
      ],
      event: {},
      notes: [],
      invitees: [],
      resources: [],
      message404: "404 - Page Not Found",
      eventLabels: {}
    };
  },
  components: {
    DeleteEventDialogBox,
    NoteEditorOverlay,
    InviteeEditorOverlay,
    DetailRow,
    InviteeTableRow,
    NoteCard,
    ResourceTableRow,
    ResourceEditorOverlay
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
        this.invitees = data.results;
      });
    },
    updateResources() {
      let endpoint = `/api/events-planner/resources/?event=${this.event.id}`;
      apiService(endpoint).then(data => {
        this.resources = data.results;
      });
    },
    getEvent(update_notes = true) {
      let endpoint = `/api/events-planner/events/${this.id}/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.event = data;
          if (update_notes) this.notes = this.updateNotes();
          this.invitees = this.updateInvitees();
          this.resources = this.updateResources();
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
    attendeeCount() {
      if (this.event && this.event.attendees && this.event.attendees.length) {
        return this.event.attendees.split(",").length;
      }
      return 0;
    },


    // isCurrentUsersRecipe() {
    //   return this.current_user === this.recipe.author;
    // }
  },
  created() {
    this.getEventMetadata();
    this.getEvent();
  }
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
