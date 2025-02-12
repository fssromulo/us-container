<template>
  <div class="card">
    <div class="card-header flex justify-center flex-wrap">
      <h3>Invoice Column Ordering</h3>
    </div>
    <div class="card-header flex justify-center flex-wrap">
      <Label> Order type </Label>
      <Select
        style="margin-left: 10px; margin-bottom: 10px"
        placeholder="Order type"
        optionLabel="name"
        optionValue="code"
        :options="state.order_types"
        v-model="state.selected_type"
        type="text"
      />
    </div>
    <PickList
      v-model="state.columns"
      listStyle="height:600px"
      dataKey="display"
    >
      <template #sourceheader> All Columns </template>
      <template #targetheader> Selected Order (default all)</template>
      <template #item="slotProps">
        <div class="flex flex-wrap p-2 items-center gap-4">
          <div class="flex-1 flex flex-col gap-2">
            <span class="font-bold">{{ slotProps.item.display }}</span>
          </div>
        </div>
      </template>
    </PickList>
    <div class="flex justify-center flex-wrap mt-6">
      <Button
        class="p-button-accent p-button-lg"
        :loading="state.loadingSavePreferences"
        @click="saveUserPreferences"
        :disabled="state.selected_type == null"
        >Save</Button
      >
      <Button
        class="p-button-accent p-button-lg ml-2"
        :loading="state.loadingResetColumnOrdering"
        @click="resetColumnOrdering"
        >Reset</Button
      >
    </div>
  </div>
</template>

<script setup>
  import { reactive, watch, onMounted, inject, ref } from "vue"

  import CustomerService from "@/service/Customers"
  import UsersService from "@/service/User"
  import UserApi from "@/api/user"

  import PickList from "primevue/picklist"
  import { useCustomerOrder } from "@/store/modules/customerOrder"
  import { useUsers } from "@/store/modules/users"

  import { useAuth0 } from "@auth0/auth0-vue"
  import cloneDeep from "lodash.clonedeep"
  import {
    rentalStatusOptions,
    salesStatusOptions,
    rentToOwnStatusOptions
  } from "@/utils/constants"

  import { useToast } from "primevue/usetoast"

  // import { useWindowSize } from '@vueuse/core'
  // const { width, height } = useWindowSize()
  const toast = useToast()
  const usersStore = useUsers()
  const usersService = new UsersService()
  const userApi = new UserApi()
  const customerService = new CustomerService()

  const { user } = useAuth0()
  const authUser = user

  const $ability = inject("$ability")

  const state = reactive({
    refreshKey: 0,
    columns: [],
    loadingSavePreferences: false,
    loadingResetColumnOrdering: false,
    selectedColumns: [],
    submitted: false,
    offlineMode: false,
    order_types: [
      { name: "purchase", code: "purchase" },
      { name: "rent", code: "rent" },
      { name: "rent to own", code: "rent_to_own" },
      { name: "all", code: "all" }
    ],
    selected_type: "all"
  })

  const filteredCols = () => {
    let defaultCols = customerService.columnOrdering($ability.can)
    return defaultCols.filter((col) => col.allowed)
  }

  const resetColumnOrdering = async () => {
    if (!usersStore.currentUser) {
      return
    }
    state.loadingResetColumnOrdering = true
    userApi
      .updateUserPreference(usersStore.currentUser.id, {
        preferences: {
          invoice_table_column_ordering: filteredCols()
        },
        order_type: state.selected_type
      })
      .then(({ data }) => {
        console.log(data)
        usersStore.setCurrentUser(usersService.dtoUser(data.value[0]))
        state.columns = [filteredCols(), []]
        toast.add({
          severity: "success",
          summary: "Success",
          detail: `Column order saved`,
          group: "br",
          life: 2000
        })
        state.loadingResetColumnOrdering = false
      })
  }

  onMounted(async () => {
    state.columns = [
      filteredCols(),
      usersStore.currentUser?.preferences?.invoice_table_column_ordering || []
    ]
  })

  const saveUserPreferences = async () => {
    let newPreferences = {
      preferences: {
        ...usersStore.currentUser?.preferences,
        invoice_table_column_ordering: state.columns[1]
      },
      order_type: state.selected_type
    }
    /*if (!usersStore.currentUser) {
    await refreshUsers();
  }*/
    state.loadingSavePreferences = true
    userApi
      .updateUserPreference(usersStore.currentUser.id, newPreferences)
      .then(({ data }) => {
        let user = usersStore.currentUser
        user.preferences = data.value[0].preferences
        usersStore.setCurrentUser(user)
        toast.add({
          severity: "success",
          summary: "Success",
          detail: `Column order saved`,
          group: "br",
          life: 2000
        })
        state.loadingSavePreferences = false
      })
  }

  watch(
    () => state.selected_type,
    async (newVal) => {
      if (newVal == "purchase") {
        state.columns = [
          filteredCols(),
          usersStore.currentUser?.preferences?.purchase
            ?.invoice_table_column_ordering || []
        ]
      } else if (newVal == "rent") {
        state.columns = [
          filteredCols(),
          usersStore.currentUser?.preferences?.rent
            ?.invoice_table_column_ordering || []
        ]
      } else if (newVal == "rent_to_own") {
        state.columns = [
          filteredCols(),
          usersStore.currentUser?.preferences?.rent_to_own
            ?.invoice_table_column_ordering || []
        ]
      } else if (newVal == "all") {
        state.columns = [
          filteredCols(),
          usersStore.currentUser?.preferences?.all
            ?.invoice_table_column_ordering || []
        ]
      }
    }
  )
</script>

<style lang="scss" scoped></style>
