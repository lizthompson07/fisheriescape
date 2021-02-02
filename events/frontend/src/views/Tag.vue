<template>
  <div class="single-tag mt-2">
    <div class="container" v-if="tag">
      <div class="row">
        <div class="col">
          <div v-if="!edit">
            <h1>{{ tag.name }}</h1>
            <p>Number of recipes: {{ tag.recipe_count }}</p>
          </div>
          <form @submit.prevent="updateTag" v-else>
            <div class="row">
              <div class="col">
                <v-text-field
                  v-model="updated_tag_name"
                  label="Name"
                  required
                ></v-text-field>
              </div>
              <div class="col">
                <v-btn type="submit" color="success">
                  Update
                </v-btn>
              </div>
            </div>

            <div class="mt-3">
              <v-alert type="error" v-if="error">
                {{ error }}
              </v-alert>
            </div>
          </form>
        </div>
        <div class="col-3">
          <v-btn
            color="primary"
            small
            class="mx-1"
            @click="toggleEdit"
            v-if="!edit"
          >
            Edit
          </v-btn>
          <v-btn
            color="error"
            small
            class="mx-1"
            v-if="!hasRecipes"
            @click="deleteTag"
          >
            Delete
          </v-btn>
        </div>
      </div>

      <v-card v-if="hasRecipes" max-width="1000">
        <v-toolbar color="indigo" dark>
          <v-toolbar-title>Recipes</v-toolbar-title>
        </v-toolbar>
        <v-list>
          <v-list-item v-for="recipe in recipes" :key="recipe.id" @click="">
            <v-list-item-content @click="goToRecipe(recipe)">
              <v-list-item-title v-text="recipe.title"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card>
      <div v-else>
        <h2>There are no recipes associated with this tag...</h2>
      </div>
    </div>
    <div class="not-found" v-else>
      <h1>{{ message404 }}</h1>
    </div>
  </div>
</template>

<script>
import { apiService } from "@/common/api_service";
import RecipeComponent from "@/components/RecipeComponent.vue";

export default {
  name: "Tag",
  props: {
    slug: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      tag: {},
      recipes: [],
      error: null,
      edit: false,
      updated_tag_name: null,
      showForm: false,
      requestUser: null,
      message404: "404 - Page Not Found"
    };
  },
  components: {
    RecipeComponent
  },
  methods: {
    getTagData() {
      let endpoint = `/api/hashtags/${this.slug}/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.tag = data;
          this.updated_tag_name = data.name;
          this.setPageTitle(data.name);
        } else {
          this.tag = null;
          this.setPageTitle(this.message404);
        }
      });
    },
    getRelatedRecipes() {
      let endpoint = `/api/hashtags/${this.slug}/recipes/`;
      apiService(endpoint).then(data => {
        if (data) {
          this.recipes = data.results;
        } else {
          this.recipes = null;
        }
      });
    },
    setPageTitle(title) {
      document.title = title;
    },
    goToRecipe(recipe) {
      this.$router.push({ name: "recipe", params: { id: recipe.id } });
    },
    async deleteTag() {
      let endpoint = `/api/hashtags/${this.slug}/`;
      await apiService(endpoint, "DELETE");
      this.$router.push({ name: "home" });
    },
    async updateTag() {
      let endpoint = `/api/hashtags/${this.slug}/`;
      await apiService(endpoint, "PUT", { name: this.updated_tag_name });
      this.getTagData();
      this.edit = false;
    },
    toggleEdit() {
      this.edit = !this.edit;
    }
  },
  computed: {
    hasRecipes() {
      return this.recipes.length > 0;
    }
  },
  created() {
    this.getTagData();
    this.getRelatedRecipes();
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
