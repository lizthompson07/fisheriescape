<template>
  <div>
    <v-app-bar color="accent-4" light>
      <v-btn icon href="/">
        <v-icon>mdi-home</v-icon>
      </v-btn>

      <v-spacer></v-spacer>

      <v-btn>
        {{ $t("newEventButton") }}
      </v-btn>

      <v-btn href="/accounts/logout/">
        <v-icon
            large
            color="green darken-2"
        >
          mdi-domain
        </v-icon>
      </v-btn>

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
