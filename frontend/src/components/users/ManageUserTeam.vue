<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="field mb-4 col-span-12">
          <h2 class="text-2xl text-gray-900">
            {{ userProp?.full_name }}
          </h2>
        </div>
        <div class="field mb-4 col-span-12 md:col-span-6">
          <label for="role" class="font-medium text-900 dark:text-0"
            >Agents</label
          >
          <MultiSelect
            filter
            :filter="true"
            v-model="state.currentAssistants"
            :options="state.availableAgents"
            optionLabel="label"
            placeholder="Select Assistants"
            style="width: 30em"
          />
        </div>
        <div class="field mb-4 col-span-12 md:col-span-6">
          <label for="role" class="font-medium text-900 dark:text-0"
            >Managers</label
          >
          <MultiSelect
            filter
            :filter="true"
            v-model="state.currentTeam"
            :options="state.availableManagers"
            optionLabel="label"
            placeholder="Select Team Members"
            style="width: 30em"
          />
        </div>
        <!-- <div class="field mb-4 col-span-12 md:col-span-6">
          <Button
            v-if="userProp?.assistant?.full_name !== undefined"
            :label="`Leave ${userProp.assistant.full_name}'s assistants`"
            @click="createUpdateUser"
            icon="pi pi-trash"
            class="w-auto p-button-danger"
          ></Button>
          <p v-else>This user is not an assistant to anyone.</p>
        </div>
        <div class="field mb-4 col-span-12 md:col-span-6">
          <Button
            v-if="userProp?.team_member?.full_name !== undefined"
            :label="`Leave ${userProp.team_member.full_name}'s Team`"
            @click="createUpdateUser"
            icon="pi pi-trash"
            class="w-auto p-button-danger"
          ></Button>
          <p v-else>This user is not a member of any team.</p>
        </div> -->
      </div>
    </div>
    <Button
      label="Update User"
      @click="createUpdateUser"
      :loading="state.loading"
      icon="pi pi-user-edit"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, onMounted, inject, defineEmits } from "vue"
  import cloneDeep from "lodash.clonedeep"

  import UsersService from "@/service/User"
  import UserApi from "@/api/user"
  import InventoryService from "@/service/Inventory"

  import { useToast } from "primevue/usetoast"
  import { useUsers } from "@/store/modules/users"

  const toast = useToast()

  const userService = new UsersService()
  const userApi = new UserApi()
  const userStore = useUsers()
  const inventoryService = new InventoryService()

  const { userProp } = defineProps({
    userProp: {
      type: Object,
      default: () => ({})
    }
  })

  const emit = defineEmits(["hide"])
  const $removeUnusedProps = inject("$removeUnusedProps")
  const $isObjectPopulated = inject("$isObjectPopulated")

  const swapOldUser = (updatedUser) => {
    const index = cloneDeep(userStore.users)
      .map((u) => u.id)
      .indexOf(updatedUser.id)
    let clonedUsers = cloneDeep(userStore.users)
    clonedUsers[index] = userService.dtoUser(updatedUser)
    userStore.setUsers(clonedUsers)
  }

  onMounted(async () => {
    resetUser()
  })

  const emptyUser = {
    first_name: "",
    last_name: "",
    display_name: "",
    email: "",
    phone: "",
    role: ""
  }

  const state = reactive({
    loading: false,
    user: cloneDeep(emptyUser),
    originalUser: null,
    originalAssistants: [],
    currentAssistants: [],
    availableAssistants: [],
    currentTeam: [],
    availableTeamMembers: [],
    availablePeople: [],
    availableAgents: [],
    availableManagers: [],
    originalCurrentTeam: []
  })

  if (userProp) {
    const assistants = cloneDeep(userProp.manager)
      .map((u) => {
        return { label: u.assistant.full_name, value: u.assistant.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))

    state.originalAssistants = assistants
    state.currentAssistants = assistants

    const team = cloneDeep(userProp.team_lead)
      .map((u) => {
        return { label: u.team_member.full_name, value: u.team_member.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
    state.originalCurrentTeam = team
    state.currentTeam = team

    state.availablePeople = userStore.users
      .filter((u) => u.id !== userProp.id)
      .filter((u) => u.role !== "admin")
      .map((u) => {
        return { label: u.full_name, value: u.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
    state.availableAgents = userStore.users
      .filter((u) => u.id !== userProp.id)
      .filter((u) => u.role !== "admin")
      .filter((u) => u.role_name !== "sales_manager")
      .map((u) => {
        return { label: u.full_name, value: u.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
    state.availableManagers = userStore.users
      .filter((u) => u.id !== userProp.id)
      .filter((u) => u.role !== "admin")
      .filter((u) => u.role_name !== "sales_agent")
      .map((u) => {
        return { label: u.full_name, value: u.id }
      })
      .sort((a, b) => a.label.localeCompare(b.label))
  }

  const resetUser = () => {
    let user = null
    if (userProp) {
      user = userService.dtoUser(userProp)
    } else {
      user = emptyUser
    }
    state.originalUser = cloneDeep(user)
    state.user = cloneDeep(user)
  }

  const $getAddedRemoved = (original, current) => {
    let added = current.filter((c) => {
      return !original.find((o) => o.value === c.value)
    })
    let removed = original.filter((o) => {
      return !current.find((c) => c.value === o.value)
    })
    return { added, removed }
  }

  const removeAddAssistants = async (compared) => {
    await deleteTeamOrAssistant(compared.removed, true)
    await deleteTeamOrAssistant(compared.added, true)

    const mappedAddPromises = compared.added.map(async (a) => {
      return await userApi.createAssistant({
        assistant_id: a.value,
        manager_id: state.user.id
      })
    })

    await Promise.all(mappedAddPromises)
  }

  const deleteTeamOrAssistant = async (list, isAssistant) => {
    if (isAssistant) {
      const mappedRemovePromises = list.map(async (a) => {
        return await userApi.getAssistantById(a.value)
      })

      const assistantsToRemove = await Promise.all(mappedRemovePromises)
      const removedAssistantsPromised = assistantsToRemove.map(async (r) => {
        if (r.data.value) {
          await userApi.deleteAssistant(r.data.value.id)
        }
      })

      await Promise.all(removedAssistantsPromised)
    } else {
      const mappedTeamRemovePromises = list.map(async (a) => {
        return await userApi.getTeamMemberById(a.value)
      })

      const membersToRemove = await Promise.all(mappedTeamRemovePromises)
      const removedMembersPromised = membersToRemove.map(async (r) => {
        if (r.data.value) {
          await userApi.deleteTeamMember(r.data.value.id)
        }
      })

      await Promise.all(removedMembersPromised)
    }
  }

  const removeAddTeamMember = async (compared) => {
    await deleteTeamOrAssistant(compared.removed, false)
    await deleteTeamOrAssistant(compared.added, false)

    const mappedAddPromises = compared.added.map(async (a) => {
      return await userApi.createTeamMember({
        team_member_id: a.value,
        team_lead_id: state.user.id
      })
    })

    await Promise.all(mappedAddPromises)
  }

  const createUpdateUser = async () => {
    state.loading = true

    if (state.user.id) {
      let comparedTeams = $getAddedRemoved(
        state.originalCurrentTeam,
        state.currentTeam
      )

      let comparedAssistants = $getAddedRemoved(
        state.originalAssistants,
        state.currentAssistants
      )

      if (
        comparedTeams.added.length === 0 &&
        comparedTeams.removed.length === 0 &&
        comparedAssistants.added.length === 0 &&
        comparedAssistants.removed.length === 0
      ) {
        toast.add({
          severity: "info",
          summary: "No Changes",
          detail: "No changes were made to the user's team.",
          life: 3000,
          group: "br"
        })
        state.loading = false
        return
      }
      await removeAddAssistants(comparedAssistants)
      await removeAddTeamMember(comparedTeams)

      // const userTeamRes = await userService.getUserTeamById(state.user.id);
      // const assistantsRes = await userService.getUserAssistantsById(
      //   state.user.id
      // );

      // const clonedUser = cloneDeep(state.user);
      // clonedUser.team_lead = userTeamRes.data.value.map((u) => u.team_member);
      // clonedUser.manager = assistantsRes.data.value.map((u) => u.assistant);
      const { data } = await userApi.getUserById(state.user.id)

      swapOldUser(data.value)

      toast.add({
        severity: "success",
        summary: "Updated user successfully",
        detail: "Nice work!",
        life: 3000,
        group: "br"
      })
      state.loading = false
      return
    }
    state.loading = false
  }
</script>

<style></style>
