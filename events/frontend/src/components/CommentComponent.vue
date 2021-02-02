<template>
  <div class="single-comment my-0">
    <p class="text-muted my-0" style="font-size: small">
      <!--      <strong v-if="isCurrentUsersComment">You </strong>-->
      <strong>{{ comment.author }} </strong>
      &#8901; {{ comment.created_at }}
      <span class="pl-3 my-0">
        (
        <router-link
          :to="{ name: 'comment-editor', params: { id: comment.id } }"
          class="btn btn-sm btn-link px-0 my-0"
        >
          edit
        </router-link>
        |
        <button
          @click="triggerDeleteComment"
          class="btn btn-sm btn-link px-0 my-0"
        >
          delete
        </button>
        )
      </span>
      <br />
      {{ comment.content }}
      &nbsp;&nbsp;
    </p>
    <hr />
  </div>
</template>

<script>
export default {
  name: "CommentComponent",
  props: {
    comment: {
      type: Object,
      required: true
    },
    requestUser: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      userLikedComment: this.comment.user_has_voted,
      numberOfLikes: this.comment.likes_count
    };
  },
  computed: {
    isCurrentUsersComment() {
      return this.requestUser === this.comment.author;
    }
  },
  methods: {
    triggerDeleteComment() {
      this.$emit("delete-comment", this.comment);
    },
    triggerLikeComment() {
      this.$emit("like-comment", this.comment);
      this.userLikedComment = true;
      this.numberOfLikes += 1;
    },
    triggerUnlikeComment() {
      this.$emit("unlike-comment", this.comment);
      this.userLikedComment = false;
      this.numberOfLikes -= 1;
    }
  }
};
</script>

<style>
>>> .my-btn {
  border: none;
  background-color: white;
  font-size: small;
  color: blue;
}

.red {
  color: red;
}

.my-btn:hover {
  color: darkgray !important;
}
</style>
