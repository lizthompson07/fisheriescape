<template>
  <div class="container mt-2" v-if="comment_body">
    <h1 class="mb-3">Edit Your Comment</h1>
    <form @submit.prevent="onSubmit">
      <v-textarea
        name="input"
        label="Body"
        auto-grow
        v-model="comment_body"
        rows="1"
      ></v-textarea>

      <div class="mt-3">
        <v-alert type="error" v-if="error">
          {{ error }}
        </v-alert>
      </div>
      <v-btn type="submit" color="success">
        Update
      </v-btn>
    </form>
  </div>
  <div class="not-found" v-else>
    <h1>{{ message404 }}</h1>
  </div>
</template>

<script>
import { apiService } from "@/common/api_service";

export default {
  name: "CommentEditor",
  props: {
    id: {
      // type: String,
      required: true
    }
  },
  data() {
    return {
      comment: null,
      comment_body: null,
      error: null,
      message404: "404 - Page Not Found"
    };
  },
  methods: {
    onSubmit() {
      if (!this.comment_body) {
        this.error = "you cannot submit an empty comment!";
      } else if (this.comment_body.length > 240) {
        this.error = "ensure this field has no more than 240 characters!";
      } else {
        let endpoint = `/api/comments/${this.id}/`;
        console.log(endpoint);
        let method = "PUT";
        apiService(endpoint, method, { content: this.comment_body }).then(
          data => {
            // console.log(data);
            if (data.recipe_id) {
              this.$router.push({
                name: "recipe",
                params: { id: data.recipe_id }
              });
            } else {
              this.error = `${data.detail} Endpoint:  ${endpoint}`;
            }
          }
        );
      }
    },
    getCommentData() {
      let endpoint = `/api/comments/${this.id}/`;
      apiService(endpoint).then(data => {
        this.comment = data;
        this.comment_body = data.content;
      });
    }
  },
  created() {
    this.getCommentData();
    document.title = "Edit Your Comment";
  }
};
</script>

<style>
.alert {
  width: 500px;
}
</style>
