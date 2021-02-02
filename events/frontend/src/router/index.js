import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
// import Recipe from "../views/Recipe.vue";
// import Tag from "../views/Tag.vue";
// import RecipeEditor from "../views/RecipeEditor.vue";
// import CommentEditor from "../views/CommentEditor.vue";
// import NotFound from "../views/NotFound.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/events/",
    name: "home",
    component: Home
  },
  //
  // {
  //   path: "recipe/:id",
  //   name: "recipe",
  //   component: Recipe,
  //   props: true
  // },
  // {
  //   path: "tag/:slug",
  //   name: "tag",
  //   component: Tag,
  //   props: true
  // },
  // {
  //   path: "comment/:id",
  //   name: "comment-editor",
  //   component: CommentEditor,
  //   props: true
  // },
  // {
  //   path: "new-recipe",
  //   name: "recipe-editor",
  //   component: RecipeEditor,
  //   props: false
  // },
  // {
  //   path: "recipe/:id/edit",
  //   name: "recipe-editor1",
  //   component: RecipeEditor,
  //   props: true
  // },
  // {
  //   path: "*",
  //   name: "page-not-found",
  //   component: NotFound
  // }
];

const router = new VueRouter({
  mode: "history",
  //base: process.env.BASE_URL,
  routes
});

export default router;
