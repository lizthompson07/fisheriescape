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
          <h1>Detail</h1>
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
            <h1>Resources</h1>
          </div>

          <div class="mt-3">
            <h1>Invitees</h1>
          </div>


          <div class="mt-3">
            <h1>Children</h1>
          </div>

        </div>
        <div class="col">
          <div class="float-right">
            <NoteEditorOverlay :event_id="event.id"></NoteEditorOverlay>
          </div>
          <h1>Notes</h1>
          <div v-for="(note, index) in event.notes" :key="index" class="py-1">
            <NoteCard :note="note"></NoteCard>
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
// import CommentComponent from "@/components/CommentComponent.vue";
import DeleteEventDialogBox from "@/components/DeleteEventDialogBox.vue";
import NoteEditorOverlay from "@/components/NoteEditorOverlay";
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
      message404: "404 - Page Not Found",
      eventLabels: {}
    };
  },
  components: {
    DeleteEventDialogBox,
    NoteEditorOverlay,
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
    // async deleteComment(comment) {
    //   let endpoint = `/api/comments/${comment.id}/`;
    //   let method = "DELETE";
    //   try {
    //     await apiService(endpoint, method);
    //     this.$delete(this.comments, this.comments.indexOf(comment));
    //     this.userHasCommented = false;
    //   } catch (err) {
    //   }
    // },
    // addCommentBtn() {
    //   this.showForm = true;
    //   console.log(this.$refs);
    //   this.$nextTick(() => this.$refs.newComment.focus());
    //   // this.$refs.newComment.$el.select();
    // },
    // slicer(input) {
    //   let myStr = input.name;
    //   return myStr.slice(0, 1).toUpperCase();
    // },
    // updateTags() {
    //   // did we subtract or add?
    //   if (this.selectedHashtags.length < this.selectedHashtagCount) {
    //     // something was subtracted
    //
    //     for (var i = 0; i < this.recipe.hashtags.length; i++) {
    //       if (!this.selectedHashtags.includes(this.recipe.hashtags[i])) {
    //         var tag2Remove = this.recipe.hashtags[i];
    //         this.removeTag(tag2Remove.name);
    //       }
    //     }
    //   } else {
    //     // something was added
    //     for (var i = 0; i < this.selectedHashtags.length; i++) {
    //       if (!this.recipe.hashtags.includes(this.selectedHashtags[i])) {
    //         var tag2Add = this.selectedHashtags[i];
    //         if (tag2Add.name) {
    //           this.addTag(tag2Add.name);
    //         } else {
    //           this.addTag(tag2Add);
    //         }
    //       }
    //     }
    //   }
    // },
    //
    // async addTag(tagName) {
    //   let endpoint = `/api/recipes/${this.recipe.id}/add-remove-hashtag/`;
    //   let method = "POST";
    //   await apiService(endpoint, method, {hashtag: tagName});
    //   this.selectedHashtags = [];
    //   this.getRecipeData();
    //   this.getHashtags();
    // },
    // async removeTag(tagName) {
    //   let endpoint = `/api/recipes/${this.recipe.id}/add-remove-hashtag/`;
    //   let method = "DELETE";
    //   await apiService(endpoint, method, {hashtag: tagName});
    //   this.getRecipeData();
    // },
    // setRequestUser() {
    //   this.requestUser = window.localStorage.getItem("username");
    // },
    getEvent() {
      let endpoint = `/api/events-planner/events/${this.id}/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.event = data;
          document.title = data.tname;
        } else {
          this.event = null;
          document.title = this.message404;
        }
      });
    },
    async deleteEvent() {
      let endpoint = `/api/events/${this.id}/`;
      await apiService(endpoint, "DELETE");
      this.$router.push({name: "home"});
    }
    // getRecipeCommentsData() {
    //   let endpoint = `/api/recipes/${this.id}/comments/`;
    //   if (this.next) {
    //     endpoint = this.next;
    //   }
    //   this.loadingComments = true;
    //   apiService(endpoint).then(data => {
    //     this.comments.push(...data.results);
    //     if (data.next) {
    //       this.next = data.next;
    //     } else {
    //       this.next = null;
    //     }
    //   });
    //   this.loadingComments = false;
    // },
    //
    // getHashtags() {
    //   let endpoint = `/api/hashtags/`;
    //   apiService(endpoint).then(data => {
    //     this.allHashtags = data.results;
    //   });
    // },
    // setPageTitle(title) {
    //   document.title = title;
    // },
    // goNewTag() {
    //   this.showTagInput = true;
    //   this.$refs.newtag.focus();
    // },
    // onSubmit() {
    //   if (!this.newCommentBody) {
    //     this.error = "You cannot submit an empty comment!";
    //   } else if (this.newCommentBody.length > 240) {
    //     this.error = "Ensure this field has no more than 240 characters!";
    //   } else {
    //     let endpoint = `/api/recipes/${this.recipe.id}/comment/`;
    //     let method = "POST";
    //     apiService(endpoint, method, {content: this.newCommentBody}).then(
    //         data => {
    //           this.comments.unshift(data);
    //         }
    //     );
    //     this.newCommentBody = null;
    //     this.showForm = false;
    //
    //     if (this.error) {
    //       this.error = null;
    //     }
    //   }
    // }
  },
  computed: {
    // isCurrentUsersRecipe() {
    //   return this.current_user === this.recipe.author;
    // }
  },
  created() {
    this.getEventMetadata();
    this.getEvent();
    // this.getRecipeCommentsData();
    // this.getHashtags();
    // this.setRequestUser();
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
