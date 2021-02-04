<template>
  <div>
    <v-app-bar color="accent-4" light>
      <v-btn icon href="/">
        <img src="@/assets/dmapps.png" width="30"/>
      </v-btn>
      <v-btn icon :to="{name: 'home'}">
        <v-icon>mdi-home</v-icon>
      </v-btn>

      <v-spacer></v-spacer>


      <v-btn @click="toggleLocale">{{ $i18n.locale }}</v-btn>
    </v-app-bar>
  </div>
</template>

<script>
export default {
  name: "NavbarComponent",
  methods: {
    toggleLocale() {
      console.log(this.$i18n.locale)
      if (this.$i18n.locale === "en") this.$i18n.locale = "fr";
      else this.$i18n.locale = "en";
    }
  }
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
