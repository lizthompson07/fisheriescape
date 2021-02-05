<template>
  <tr>
    <td> {{ invitee.full_name }}</td>
<!--    <td>{{ invitee.email }}</td>-->
    <td> {{ invitee.organization }}</td>
    <td>{{ invitee.role_display }}</td>


    <td v-if="!invitee.attendance.length">
      <v-btn x-small :color="btnColor" @click="toggleStatus">
        {{ invitee.status_display }}
      </v-btn>
    </td>
    <td v-else>
      Attended ({{invitee.attendance_percentage}})
    </td>

    <td>
      <InviteeAttendanceOverlay
          :invitee="invitee"
          @update-invitees="$emit('update-invitees')"
      ></InviteeAttendanceOverlay>
    </td>
    <td>
      <InviteeEditorOverlay :invitee="invitee" @update-invitees="$emit('update-invitees')"></InviteeEditorOverlay>
    </td>
    <td>
      <DeleteInviteeDialogBox
          @delete-confirmation="deleteInvitee"
      ></DeleteInviteeDialogBox>
    </td>
  </tr>
</template>

<script>
import DeleteInviteeDialogBox from "@/components/DeleteInviteeDialogBox";
import InviteeEditorOverlay from "@/components/InviteeEditorOverlay";
import InviteeAttendanceOverlay from "@/components/InviteeAttendanceOverlay";
import {apiService} from "@/common/api_service";

export default {
  name: "DetailRow",
  props: {
    invitee: {
      required: true
    }
  },
  components: {
    InviteeEditorOverlay,
    InviteeAttendanceOverlay,
    DeleteInviteeDialogBox
  },
  data() {
    return {};
  },
  methods: {
    async deleteInvitee() {
      let endpoint = `/api/events-planner/invitees/${this.invitee.id}/`;
      await apiService(endpoint, "DELETE");
      this.$emit("update-invitees");
    },
    async toggleStatus() {
      let nextStatus = 0;
      let statusArray = [0, 1, 2, 9];
      let currentStatusPos = statusArray.indexOf(this.invitee.status) + 1;
      if (currentStatusPos >= 4) {
        nextStatus = currentStatusPos % 4;
      } else {
        nextStatus = statusArray[currentStatusPos];

      }

      let endpoint = `/api/events-planner/invitees/${this.invitee.id}/`;
      await apiService(endpoint, "PATCH", {
        status: nextStatus
      });
      this.$emit("update-invitees");
    }
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
