<template>
  <div class="single-recipe">
    <p class="text-muted mb-1 mt-2">
      <strong>{{ recipe.author }} </strong>
      &#8901; {{ recipe.created_at }} &#8901; {{ recipe.title }}
    </p>
    <hr />
  </div>
</template>

<script>
export default {
  name: "RecipeComponent",
  props: {
    recipe: {
      type: Object,
      required: true
    },
    requestUser: {
      type: String,
      required: true
    }
  },
  data() {
    return {};
  },
  methods: {}
};
</script>
