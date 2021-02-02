<template>
  <div class="container mt-2">
    <h1 v-if="recipe" class="mb-3">Edit a Recipe</h1>
    <h1 v-else class="mb-3">Add a Recipe</h1>

    <form @submit.prevent="onSubmit">
      <v-text-field v-model="title" label="Title" required></v-text-field>

      <v-textarea
        name="input-7-1"
        filled
        label="Body"
        auto-grow
        v-model="recipe_body"
      ></v-textarea>
      <v-btn type="submit" color="success">
        <span v-if="recipe">Update</span>
        <span v-else>Publish</span>
      </v-btn>

      <DeleteRecipeDialogBox
        v-if="recipe"
        @delete-confirmation="deleteRecipe"
      ></DeleteRecipeDialogBox>
      <v-btn
        v-if="recipe"
        color="normal"
        class="mx-1"
        :to="{ name: 'recipe', params: { id: recipe.id } }"
      >
        Back
      </v-btn>
      <v-btn v-else color="normal" class="mx-1" :to="{ name: 'home' }">
        Back
      </v-btn>

      <div class="mt-3">
        <v-alert type="error" v-if="error">
          {{ error }}
        </v-alert>
      </div>
    </form>
  </div>
</template>

<script>
import { apiService } from "@/common/api_service";
import DeleteRecipeDialogBox from "@/components/DeleteRecipeDialogBox.vue";

export default {
  name: "RecipeEditor",
  props: {
    id: {
      // type: String,
      // required: true
    }
  },
  data() {
    return {
      recipe_body: null,
      title: null,
      error: null,
      recipe: null
    };
  },
  methods: {
    async onSubmit() {
      if (!this.title) {
        this.error = "you must have a title!";
      } else {
        var method;
        var endpoint;
        if (this.recipe) {
          endpoint = `/api/recipes/${this.recipe.id}/`;
          method = "PUT";
        } else {
          endpoint = "/api/recipes/";
          method = "POST";
        }
        await apiService(endpoint, method, {
          title: this.title,
          content: this.recipe_body
        }).then(data => {
          this.$router.push({
            name: "recipe",
            params: { id: data.id }
          });
        });
      }
    },
    getRecipeData() {
      if (this.id) {
        let endpoint = `/api/recipes/${this.id}/`;
        apiService(endpoint).then(data => {
          this.recipe = data;
          this.recipe_body = data.content;
          this.title = data.title;
        });
      }
    },
    async deleteRecipe() {
      let endpoint = `/api/recipes/${this.id}/`;
      await apiService(endpoint, "DELETE");
      this.$router.push({ name: "home" });
    }
  },
  created() {
    document.title = "Edit Recipe";
    this.getRecipeData();
  },
  components: {
    DeleteRecipeDialogBox
  }
};
</script>

<style>
.alert {
  width: 500px;
}
</style>
