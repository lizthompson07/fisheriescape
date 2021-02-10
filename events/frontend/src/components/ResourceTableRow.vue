<template>
  <tr>
    <td> {{ resource.tname }}</td>
    <td>
      <a v-if="resource.url_en" :href="resource.url_en">English URL</a>
      <br>
      <a v-if="resource.url_fr" :href="resource.url_fr">French URL</a>
    </td>
    <td>{{ resource.date_added }}</td>

    <td>
      <ResourceEditorOverlay :resource="resource" @update-resources="$emit('update-resources')"></ResourceEditorOverlay>
    </td>
    <td>
      <DeleteResourceDialogBox
          @delete-confirmation="deleteResource"
      ></DeleteResourceDialogBox>
    </td>
  </tr>
</template>

<script>
import DeleteResourceDialogBox from "@/components/DeleteResourceDialogBox";
import ResourceEditorOverlay from "@/components/ResourceEditorOverlay";
import {apiService} from "@/common/api_service";

export default {
  name: "DetailRow",
  props: {
    resource: {
      required: true
    }
  },
  components: {
    ResourceEditorOverlay,
    DeleteResourceDialogBox
  },
  data() {
    return {};
  },
  methods: {
    async deleteResource() {
      let endpoint = `/api/events-planner/resources/${this.resource.id}/`;
      await apiService(endpoint, "DELETE");
      this.$emit("update-resources");
    },

  },
  computed: {
    btnColor() {
      if (this.invitee.status === 0) return "light";
      else if (this.invitee.status === 1) return "primary";
      else if (this.invitee.status === 2) return "error";
      else return "secondary";
    }
  }
};
</script>
