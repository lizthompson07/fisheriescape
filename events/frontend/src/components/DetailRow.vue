<template>
  <tr>
    <th class="text-left" v-html="label"></th>
    <td class="text-left" v-html="value"></td>
  </tr>
</template>

<script>
export default {
  name: "DetailRow",
  props: {
    label: {
      type: String,
      required: false
    },
    value: {
      required: false
    }
  },
  data() {
    return {};
  },
  methods: {}
};
</script>
