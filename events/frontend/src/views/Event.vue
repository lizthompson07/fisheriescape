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
              <tr>
                <th class="text-left">
                  Name
                </th>
                <td class="text-left">
                  {{ event.name }}
                </td>
              </tr>
              <tr>
                <th class="text-left">
                  Nom
                </th>
                <td class="text-left">
                  {{ event.nom }}
                </td>
              </tr>
              <tr>
                <th class="text-left">
                  Type
                </th>
                <td class="text-left">
                  {{ event.type_display }}
                </td>
              </tr>
              <tr>
                <th class="text-left">
                  Location
                </th>
                <td class="text-left">
                  {{ event.location }}
                </td>
              </tr>
              <tr>
                <th class="text-left">
                  Proponent
                </th>
                <td class="text-left">
                  {{ event.proponent }}
                </td>
              </tr>
              <tr>
                <th class="text-left">
                  Start / End Date
                </th>
                <td class="text-left" v-html="event.display_dates"></td>
              </tr>
              <tr>
                <th class="text-left">
                  Metadata
                </th>
                <td class="text-left" v-html="event.metadata">
                  {{ event.metadata }}
                </td>
              </tr>
              </tbody>
            </template>


          </v-simple-table>

          <div class="mt-3">
            <h1>Resources</h1>
          </div>

          <div class="mt-3">
            <h1>Invitees</h1>
          </div>


          <!--            </div>-->
          <!--            <div class="col">-->
          <!--&lt;!&ndash;              <v-btn&ndash;&gt;-->
          <!--&lt;!&ndash;                color="primary"&ndash;&gt;-->
          <!--&lt;!&ndash;                small&ndash;&gt;-->
          <!--&lt;!&ndash;                :to="{ name: 'recipe-editor1', params: { id: recipe.id } }"&ndash;&gt;-->
          <!--&lt;!&ndash;                class="mx-1"&ndash;&gt;-->
          <!--&lt;!&ndash;              >&ndash;&gt;-->
          <!--&lt;!&ndash;                Edit&ndash;&gt;-->
          <!--&lt;!&ndash;              </v-btn>&ndash;&gt;-->
          <!--            </div>-->
          <!--          </div>-->

          <!--          <v-combobox-->
          <!--            v-model="selectedHashtags"-->
          <!--            :items="allHashtags"-->
          <!--            item-text="name"-->
          <!--            label="Tags"-->
          <!--            multiple-->
          <!--            outlined-->
          <!--            @change="updateTags"-->
          <!--          >-->
          <!--          </v-combobox>-->

          <!--          <p class="mb-2">-->
          <!--            <strong>Posted by:</strong>-->
          <!--            <span v-if="isCurrentUsersRecipe">You</span>-->
          <!--            <span v-else>{{ recipe.author }}</span>-->
          <!--          </p>-->
          <!--          <p>{{ recipe.created_at }}</p>-->
          <!--          <p class="">-->
          <!--            <strong>Tags:</strong>-->
          <!--            <v-chip-->
          <!--              class="mx-1"-->
          <!--              v-for="tag in recipe.hashtags"-->
          <!--              color="secondary"-->
          <!--              :to="{ name: 'tag', params: { slug: tag.slug } }"-->
          <!--            >-->
          <!--              <v-avatar-->
          <!--                class="accent white&#45;&#45;text"-->
          <!--                left-->
          <!--                v-text="slicer(tag)"-->
          <!--              ></v-avatar>-->
          <!--              {{ tag.name }}-->
          <!--            </v-chip>-->
          <!--          </p>-->

          <!--          <p v-html="recipe.content_html"></p>-->
          <!--        </div>-->
          <!--        <div class="col">-->
          <!--          <div class="row">-->
          <!--            <div class="col">-->
          <!--              <h4>Comments</h4>-->
          <!--            </div>-->
          <!--            <div class="col">-->
          <!--              <v-btn-->
          <!--                small-->
          <!--                color="success"-->
          <!--                @click="addCommentBtn"-->
          <!--                v-if="!showForm"-->
          <!--                class="mx-1"-->
          <!--              >-->
          <!--                Add a Comment-->
          <!--              </v-btn>-->
          <!--            </div>-->
          <!--          </div>-->

          <!--          <div v-if="showForm" class="mt-3">-->
          <!--            <form @submit.prevent="onSubmit">-->
          <!--              <v-text-field-->
          <!--                name="input"-->
          <!--                label="Comment"-->
          <!--                v-model="newCommentBody"-->
          <!--                ref="newComment"-->
          <!--              ></v-text-field>-->
          <!--              <v-btn type="submit" color="success" class="mx-1">-->
          <!--                Submit-->
          <!--              </v-btn>-->
          <!--              <v-btn-->
          <!--                class="mx-1"-->
          <!--                color="normal"-->
          <!--                v-if="showForm"-->
          <!--                @click="showForm = false"-->
          <!--              >-->
          <!--                Cancel-->
          <!--              </v-btn>-->
          <!--            </form>-->
          <!--            <p v-if="error" class="error mt-2">{{ error }}</p>-->
          <!--            <br />-->
          <!--            <br />-->
          <!--            <br />-->
          <!--          </div>-->

          <!--          <CommentComponent-->
          <!--            v-for="(comment, index) in comments"-->
          <!--            :comment="comment"-->
          <!--            :requestUser="requestUser"-->
          <!--            :key="index"-->
          <!--            @delete-comment="deleteComment"-->
          <!--          />-->
          <!--        </div>-->
          <!--      </div>-->
        </div>
        <div class="col">
          <h1>Notes</h1>
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
      // comments: [],
      // newCommentBody: null,
      //
      // allHashtags: [],
      // selectedHashtags: [],
      // selectedHashtagCount: [],
      // newHashtag: null,
      //
      // error: null,
      // userHasCommented: false,
      // showForm: false,
      // showTagInput: false,
      //
      // requestUser: null,
      // next: null,
      // loadingComments: false,
      message404: "404 - Page Not Found"
    };
  },
  components: {
    DeleteEventDialogBox
  },
  methods: {
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
      let endpoint = `/api/events/${this.id}/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.event = data;
          // this.selectedHashtags = data.hashtags;
          // this.selectedHashtagCount = data.hashtags.length;
          // this.userHasCommented = data.user_has_commented;
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
