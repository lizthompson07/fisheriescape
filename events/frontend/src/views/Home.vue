<template>
  <div class="home">
    <div class="container mt-2">
      <div class="mt-2 mb-5">
        <div class="text-h2">{{ $t("welcomeMsg") }}</div>
        <div class="text-h5 text-muted mt-2 mb-2">
          {{ $t("message") }}
        </div>
      </div>
      <div class="row">
        <div class="col">
          <v-card>
            <v-card-title>
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search Meal Ideas"
                single-line
                hide-details
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn small color="primary" :to="{ name: 'recipe-editor' }"
                >New</v-btn
              >
            </v-card-title>
            <v-data-table :headers="headers" :items="recipes" :search="search">
              <template v-slot:item.title="{ item }">
                <router-link :to="{ name: 'recipe', params: { id: item.id } }"
                  >{{ item.title }}
                </router-link>
              </template>
            </v-data-table>
          </v-card>
        </div>
        <div class="col-4">
          <v-card>
            <v-card-title>
              <v-text-field
                v-model="search_tag"
                append-icon="mdi-magnify"
                label="Search Tags"
                single-line
                hide-details
              ></v-text-field>
            </v-card-title>
            <v-data-table
              :headers="tag_headers"
              :items="tags"
              :search="search_tag"
            >
              <template v-slot:item.name="{ item }">
                <router-link :to="{ name: 'tag', params: { slug: item.slug } }"
                  >{{ item.name }}
                </router-link>
              </template>
            </v-data-table>
          </v-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiService } from "@/common/api_service";

export default {
  name: "home",
  data() {
    return {
      recipes: [],
      tags: [],
      next: null,
      loadingRecipes: false,
      current_user: null,
      search: "",
      search_tag: "",
      headers: [
        {
          text: "Title",
          align: "start",
          sortable: false,
          value: "title"
        },
        // {text: 'Author', value: 'author'},
        { text: "Date created", value: "created_at" },
        { text: "Tags", value: "hashtags_string" }
      ],

      tag_headers: [
        {
          text: "Name",
          align: "start",
          value: "name"
        },
        { text: "Recipe count", value: "recipe_count" }
      ]
    };
  },
  methods: {
    getUserData() {
      let endpoint = `/api/user/`;
      apiService(endpoint).then(data => {
        this.current_user = data.username;
      });
    },
    getRecipes() {
      let endpoint = "api/recipes/";
      if (this.next) {
        endpoint = this.next;
      }
      this.loadingRecipes = true;
      apiService(endpoint).then(data => {
        this.recipes.push(...data.results);
        if (data.next) {
          this.next = data.next;
        } else {
          this.next = null;
        }
      });
      this.loadingRecipes = false;
    },
    getTags() {
      let endpoint = "api/hashtags/";
      apiService(endpoint).then(data => {
        this.tags = data.results;
      });
    }
  },

  created() {
    this.getRecipes();
    this.getUserData();
    this.getTags();
    document.title = "MealThyme";
  }
};
</script>

<style>
.author-name {
  font-weight: bold;
  color: #dc3545;
}

.recipe-link {
  font-weight: bold;
  color: black;
}

.recipe-link:hover {
  color: #343a40;
  text-decoration: none;
}
</style>
