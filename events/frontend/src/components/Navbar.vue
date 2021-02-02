<!--<template>-->
<!--    <nav class="navbar navbar-expand-lg navbar-light bg-light my-navbar">-->
<!--        <div class="container">-->

<!--            <router-link-->
<!--                    :to="{name: 'home'}"-->
<!--                    class="navbar-brand"-->
<!--            >MealThyme-->
<!--            </router-link>-->

<!--            <v-btn class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav"-->
<!--                    aria-expanded="false" aria-label="Toggle navigation">-->
<!--                <span class="navbar-toggler-icon"></span>-->
<!--            </v-btn>-->
<!--            <div class="collapse navbar-collapse" id="navbarNav">-->
<!--                <ul class="navbar-nav ml-auto">-->
<!--                    <li class="nav-item mx-1">-->
<!--                        <router-link-->
<!--                                :to="{name: 'recipe-editor'}"-->
<!--                                class="btn btn-sm btn-danger"-->
<!--                        >Add a Recipe-->
<!--                        </router-link>-->
<!--                    </li>-->

<!--                    <li class="nav-item">-->
<!--                        <a class="btn btn-sm btn-outline-secondary" href="/accounts/logout/" tabindex="-1" aria-disabled="true">Logout</a>-->
<!--                    </li>-->
<!--                </ul>-->
<!--            </div>-->
<!--        </div>-->

<!--    </nav>-->
<!--</template>-->

<template>
  <div>
    <v-app-bar color="deep-purple accent-4" dark>
      <!--      <v-app-bar-nav-icon></v-app-bar-nav-icon>-->
      <v-btn icon :to="www.google.com">
        <v-icon>mdi-home</v-icon>
      </v-btn>
      <!--      <v-toolbar-title>-->
      <!--        Meal Thyme-->
      <!--      </v-toolbar-title>-->

      <v-spacer></v-spacer>

      <v-btn :to="{ name: 'recipe-editor' }">
        New Recipe
      </v-btn>
      <v-btn icon href="/accounts/logout/">
        <v-icon>mdi-logout</v-icon>
      </v-btn>

      <!--      <v-menu-->
      <!--        left-->
      <!--        bottom-->
      <!--      >-->
      <!--        <template v-slot:activator="{ on, attrs }">-->
      <!--          <v-btn-->
      <!--            icon-->
      <!--            v-bind="attrs"-->
      <!--            v-on="on"-->
      <!--          >-->
      <!--            <v-icon>mdi-dots-vertical</v-icon>-->
      <!--          </v-btn>-->
      <!--        </template>-->

      <!--        <v-list>-->
      <!--          <v-list-item-->
      <!--            v-for="n in 5"-->
      <!--            :key="n"-->
      <!--            @click="() => {}"-->
      <!--          >-->
      <!--            <v-list-item-title>Option {{ n }}</v-list-item-title>-->
      <!--          </v-list-item>-->
      <!--        </v-list>-->
      <!--      </v-menu>-->
    </v-app-bar>
  </div>
</template>

<script>
export default {
  name: "NavbarComponent"
};
</script>
<style>
.my-navbar {
  border-bottom: 1px solid #ddd;
}

.navbar-brand {
  font-weight: bold;
  font-size: 130%;
}

.navbar-brand:hover {
  color: red !important;
}
</style>
