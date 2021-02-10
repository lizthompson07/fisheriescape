import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import Event from "../views/Event.vue";
// import Tag from "../views/Tag.vue";
import EventEditor from "../views/EventEditor.vue";
// import CommentEditor from "../views/CommentEditor.vue";
// import NotFound from "../views/NotFound.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/events",
    name: "home",
    component: Home
  },
  {
    path: "/events/new-event",
    name: "event-new",
    component: EventEditor,
    props: false
  },
  {
    path: "/events/:id",
    name: "event-detail",
    component: Event,
    props: true
  },
  {
    path: "/events/:id/edit",
    name: "event-edit",
    component: EventEditor,
    props: true
  },
  {
    path: "/events/:parent_id/new-child",
    name: "event-new-child",
    component: EventEditor,
    props: true
  },
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
