<template>
  <div id="app">
    <v-app>
      <v-main>
        <NavbarComponent />
        <router-view />
        <localeChanger/>

      </v-main>
    </v-app>
  </div>
</template>

<script>
import localeChanger from "@/components/HelloI18n.vue";
import NavbarComponent from "@/components/Navbar.vue";
import { apiService } from "@/common/api_service";

export default {
  name: "App",
  components: {
    NavbarComponent,
    localeChanger
  },
  methods: {
    async setUserInfo() {
      const data = await apiService("/api/user/");
      const requestUser = data.username;
      window.localStorage.setItem("username", requestUser);
    }
  },
  created() {
    this.setUserInfo();
  }
};
</script>

<style>
html,
body {
  height: 100%;
  font-family: "Playfair Display", serif;
}

.btn:focus {
  box-shadow: none !important;
}
</style>
