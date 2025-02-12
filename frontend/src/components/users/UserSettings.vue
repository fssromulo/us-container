<template>
  <div>
    <div>
      <div class="grid grid-cols-12 gap-4 formgrid p-fluid">
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >First Name</label
          >
          <InputText
            placeholder="First Name"
            v-model="state.user.first_name"
            :class="{ 'p-invalid': v$.user.first_name.$invalid }"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Last Name</label
          >
          <InputText
            placeholder="Last Name"
            v-model="state.user.last_name"
            :class="{ 'p-invalid': v$.user.last_name.$invalid }"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Display Name</label
          >
          <InputText
            placeholder="Display Name"
            v-model="state.user.display_name"
            :class="{ 'p-invalid': v$.user.display_name.$invalid }"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="state" class="font-medium text-900 dark:text-0"
            >Email</label
          >
          <InputText
            placeholder="Email"
            v-model="state.user.email"
            :class="{ 'p-invalid': v$.user.email.$invalid }"
            id="cost"
            type="text"
          />
        </div>
        <div class="col-span-12 mb-4 field md:col-span-3">
          <label for="price_per_mile" class="font-medium text-900 dark:text-0"
            >Phone</label
          >
          <InputMask
            id="phone"
            v-model="state.user.phone"
            mask="(999)-999-9999"
            placeholder="999-99-9999"
          />
        </div>
        <div class="mb-3 field col-12 md:col-3">
          <label for="role" class="font-medium text-900">Role</label>
          <Select
            placeholder="Select role"
            :options="state.roles"
            v-model="state.user.role_id"
            id="role"
            type="text"
            optionLabel="label"
            optionValue="value"
          />
        </div>
        <div
          v-if="$isObjectPopulated(userProp)"
          class="col-span-12 mb-4 field md:col-span-2"
        >
          <label for="active" class="block font-medium text-900 dark:text-0"
            >Is Active</label
          >
          <toggleSwitch class="text-sm" v-model="state.user.is_active" />
        </div>
      </div>
    </div>
    <Button
      :label="$isObjectPopulated(userProp) ? 'Update User' : 'Create User'"
      @click="createUpdateUser"
      :loading="state.loading"
      icon="pi pi-user"
      class="w-auto"
    ></Button>
  </div>
</template>

<script setup>
  import { reactive, computed, onMounted, inject, defineEmits } from "vue"

  import { useVuelidate } from "@vuelidate/core"
  import { required, email } from "@vuelidate/validators"

  import StateService from "../../service/StateService"
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

  const stateService = new StateService()

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
    userStore.setUsers(clonedUsers.map((u) => userService.dtoUser(u)))
  }

  onMounted(async () => {
    state.statesList = stateService.getStates()
    state.roles = userStore.roles.map((r) => ({
      label: r.name,
      value: r.id
    }))
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
    roles: []
  })

  const rules = computed(() => ({
    user: {
      first_name: { required, $lazy: true },
      last_name: { required, $lazy: true },
      display_name: { required, $lazy: true },
      email: { required, email, $lazy: true }
      // role: { required, $lazy: true },
    }
  }))

  const v$ = useVuelidate(rules, state)

  const resetUser = () => {
    let user = null
    if (userProp) {
      user = userService.dtoUser(userProp)
    } else {
      user = emptyUser
    }
    state.originalUser = cloneDeep(user)
    state.user = cloneDeep(user)
    v$.value.$reset()
    state.loading = false
  }

  const createUpdateUser = async () => {
    const isFormCorrect = await v$.value.$validate()
    if (!isFormCorrect) {
      return
    }
    state.loading = true

    if (state.user.id) {
      let requestData = $removeUnusedProps(state.user, state.originalUser)

      if (requestData.phone) {
        requestData.phone = requestData.phone.replace(/-/g, "")
      }

      if (!$isObjectPopulated(requestData)) {
        toast.add({
          severity: "warn",
          summary: "User Unchanged",
          detail: "User Unchanged",
          group: "br",
          life: 5000
        })
        return
      }

      const { data, error } = await userApi.updateUser(
        state.user.id,
        requestData
      )
      if (data.value) {
        toast.add({
          severity: "success",
          summary: "User Price Updated",
          detail: "Successfully updated user",
          group: "br",
          life: 5000
        })
      }
      if (error.value) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Error updating user price",
          group: "br",
          life: 5000
        })
      }
      swapOldUser(data.value)
      state.loading = false
    } else {
      const { data } = await userApi.createUser(state.user)

      if (data.value) {
        toast.add({
          severity: "success",
          summary: "Container Saved",
          detail: "Successfully saved user",
          group: "br",
          life: 5000
        })
      }

      let updatedUsers = cloneDeep(userStore.users)
      updatedUsers.unshift(userService.dtoUser(data.value))
      userStore.setUsers(updatedUsers.map((u) => userService.dtoUser(u)))
      resetUser()
    }
    state.loading = false
    emit("hide")
  }
</script>

<style></style>
